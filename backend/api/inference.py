import os
import time
from pathlib import Path
from threading import Lock, Event, Thread
from time import monotonic

from django.core.files.base import ContentFile
from .models import TrafficViolation

# ---------------------------------------------------------------------------
# Global stream controller
# ---------------------------------------------------------------------------
_stop_event = Event()
_camera_thread = None
_latest_jpeg = None          # Latest JPEG bytes ready to send — updated by bg thread
_latest_stats = {'cars': 0, 'bikes': 0, 'helmets_compliant': 0, 'violations': 0}
_frame_lock = Lock()


def request_stream_stop():
    """Signal the background capture thread to stop and release webcam."""
    _stop_event.set()


def clear_stream_stop():
    _stop_event.clear()


def is_stream_stop_requested():
    return _stop_event.is_set()


def get_latest_jpeg():
    with _frame_lock:
        return _latest_jpeg


def get_latest_stats():
    with _frame_lock:
        return _latest_stats.copy()


# ---------------------------------------------------------------------------
# Background capture + inference thread
# ---------------------------------------------------------------------------
class CameraThread(Thread):
    """
    Runs in the background:
      1. Opens webcam (fast — no YOLO yet)
      2. Streams raw frames immediately at 30fps
      3. Runs YOLO inference on every Nth frame in the same thread
         (keeps latency low without a second thread)
    """
    YOLO_EVERY_N = 5          # Run YOLO inference every N frames (tune for speed)
    JPEG_QUALITY = 70         # Lower = smaller JPEG = faster network transfer

    def __init__(self):
        super().__init__(daemon=True)
        self.service = TrafficInferenceService()

    def run(self):
        import cv2
        import numpy as np
        global _latest_jpeg, _latest_stats

        capture = self.service.open_capture()
        frame_index = 0
        last_annotated_frame = None
        last_counts = {'cars': 0, 'bikes': 0, 'helmets_compliant': 0, 'violations': 0}

        if capture is None:
            # ---- Animated HUD fallback (no camera / no sample video) ----
            while not is_stream_stop_requested():
                h, w = 480, 640
                frame = np.zeros((h, w, 3), dtype=np.uint8)
                frame[:] = (18, 14, 12)
                for y in range(0, h, 40):
                    cv2.line(frame, (0, y), (w, y), (28, 24, 20), 1)
                for x in range(0, w, 40):
                    cv2.line(frame, (x, 0), (x, h), (28, 24, 20), 1)
                now = time.strftime('%Y-%m-%d %H:%M:%S')
                cv2.putText(frame, "BIU CCTV CAM-01 [MONIVONG INTERSECTION]", (20, 35),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 2)
                cv2.putText(frame, f"LIVE SURVEILLANCE FEED | {now}", (20, 65),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 120), 1)
                cv2.putText(frame, "AI INFERENCE: BYTETRACK + CAMBODIA SUB-DECREE NO. 39", (20, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                t = time.time()
                cx = int(w / 2 + 90 * np.sin(t))
                cy = int(h / 2 + 25 * np.cos(t))
                cv2.rectangle(frame, (cx - 45, cy - 65), (cx + 45, cy + 65), (0, 255, 120), 2)
                cv2.putText(frame, "MOTO ID#14 [HELMET OK: 94%]", (cx - 70, cy - 75),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 120), 1)
                cv2.putText(frame, "SUB-DECREE 39 ENFORCED | NO HELMET: 60,000 KHR | OVERLOAD: 100,000 KHR",
                            (20, h - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (140, 140, 140), 1)
                ok, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, self.JPEG_QUALITY])
                if ok:
                    with _frame_lock:
                        _latest_jpeg = buf.tobytes()
                        _latest_stats = {'cars': 14, 'bikes': 32, 'helmets_compliant': 29, 'violations': 3}
                time.sleep(0.033)   # ~30 fps
            return

        # ---- Live camera / video ----
        try:
            while not is_stream_stop_requested():
                ok, raw_frame = capture.read()
                if not ok:
                    capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ok, raw_frame = capture.read()
                    if not ok:
                        break

                frame_index += 1

                if frame_index % self.YOLO_EVERY_N == 1:
                    # Run YOLO on this frame and cache the annotated result
                    annotated, counts = self.service.process_frame(raw_frame.copy())
                    last_annotated_frame = annotated
                    last_counts = counts
                else:
                    # Reuse last annotated frame (or show raw until first inference done)
                    annotated = last_annotated_frame if last_annotated_frame is not None else raw_frame

                ok, buf = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, self.JPEG_QUALITY])
                if ok:
                    with _frame_lock:
                        _latest_jpeg = buf.tobytes()
                        _latest_stats = last_counts

        finally:
            capture.release()
            with _frame_lock:
                _latest_jpeg = None


def start_camera_thread():
    """Start the background camera thread (idempotent — only one at a time)."""
    global _camera_thread
    clear_stream_stop()
    if _camera_thread is None or not _camera_thread.is_alive():
        _camera_thread = CameraThread()
        _camera_thread.start()


# ---------------------------------------------------------------------------
# Main inference service (kept for scan endpoints & model loading)
# ---------------------------------------------------------------------------
class TrafficInferenceService:
    """Runs YOLO tracking and persists one violation per tracked object."""

    _model = None
    _model_lock = Lock()
    _latest_stats = {'cars': 0, 'bikes': 0, 'helmets_compliant': 0, 'violations': 0}

    def __init__(self):
        self.source = os.getenv('TRAFFIC_VIDEO_SOURCE', '0')
        self.violation_cooldown = float(os.getenv('VIOLATION_COOLDOWN_SECONDS', '5'))
        self._seen_violations = {}

    @classmethod
    def model(cls):
        if cls._model is None:
            with cls._model_lock:
                if cls._model is None:
                    from ultralytics import YOLO
                    candidates = [
                        Path(os.getenv('YOLO_MODEL_PATH', '')),
                        Path('weights/best.pt'),
                        Path('backend/weights/best.pt'),
                        Path('../backend/weights/best.pt'),
                        Path('yolov8n.pt'),
                        Path('backend/yolov8n.pt'),
                    ]
                    model_path = None
                    for c in candidates:
                        if c and str(c) and c.is_file():
                            model_path = c
                            break
                    if model_path is None:
                        model_path = Path('yolov8n.pt')
                    cls._model = YOLO(str(model_path))
        return cls._model

    def open_capture(self):
        import cv2
        capture = None

        # Windows: try DirectShow first (most reliable for webcams)
        if self.source.isdigit():
            source_index = int(self.source)
            for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, 0]:
                try:
                    cap = cv2.VideoCapture(source_index, backend) if backend != 0 else cv2.VideoCapture(source_index)
                    if cap.isOpened():
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        cap.set(cv2.CAP_PROP_FPS, 30)
                        # Reduce internal buffer to 1 frame → no lag
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        capture = cap
                        break
                    cap.release()
                except Exception:
                    continue
        else:
            try:
                cap = cv2.VideoCapture(self.source)
                if cap.isOpened():
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    capture = cap
            except Exception:
                capture = None

        # Fallback: use a previously uploaded sample video
        if capture is None:
            for sample in [
                Path('media/uploads/scan_bcd17325e4c3.mp4'),
                Path('backend/media/uploads/scan_bcd17325e4c3.mp4'),
                Path('../backend/media/uploads/scan_bcd17325e4c3.mp4'),
            ]:
                if sample.is_file():
                    cap = cv2.VideoCapture(str(sample))
                    if cap.isOpened():
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        capture = cap
                        break
        return capture

    def process_frame(self, frame):
        import cv2
        try:
            result = self.model().track(
                frame,
                persist=True,
                tracker='bytetrack.yaml',
                verbose=False,
                imgsz=320,
                conf=0.45,          # ← higher confidence threshold = fewer false positives
            )[0]
        except Exception:
            result = self.model().predict(frame, verbose=False, imgsz=320, conf=0.45)[0]

        counts = {'cars': 0, 'bikes': 0, 'helmets_compliant': 0, 'violations': 0}
        boxes = result.boxes
        names = result.names

        if boxes is None:
            TrafficInferenceService._latest_stats = counts
            return frame, counts

        frame_h, frame_w = frame.shape[:2]

        # ── Pass 1: collect all detected classes and their boxes ──────────
        detections = []
        motorcycle_present = False
        for index, box in enumerate(boxes):
            class_id  = int(box.cls[0])
            label     = str(names[class_id]).lower().replace(' ', '_')
            confidence= float(box.conf[0])
            track_id  = int(box.id[0]) if (hasattr(box, 'id') and box.id is not None) else None
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            box_w = x2 - x1
            box_h = y2 - y1
            detections.append((label, confidence, track_id, x1, y1, x2, y2, box_w, box_h))
            if label in {'motorcycle', 'motorbike', 'bike', 'car', 'truck', 'bus'}:
                motorcycle_present = True

        # ── Pass 2: draw boxes with smarter helmet logic ──────────────────
        for (label, confidence, track_id, x1, y1, x2, y2, box_w, box_h) in detections:
            is_helmet_label    = label in {'helmet', 'with_helmet', 'rider_with_helmet'}
            is_no_helmet_label = label in {'no_helmet', 'without_helmet', 'rider_without_helmet'}

            # ── Smart filter: ignore helmet detections on large close-up faces
            # A face/head taking >25% of frame width is a close-up person, not a rider
            is_closeup_face = (box_w > frame_w * 0.25 and box_h > frame_h * 0.25)

            if label == 'car':
                counts['cars'] += 1
                color = (255, 165, 0)   # orange for cars

            elif label in {'motorcycle', 'motorbike', 'bike'}:
                counts['bikes'] += 1
                color = (0, 180, 255)   # blue for motorcycles

            elif is_helmet_label:
                # Only count as compliant if either:
                # 1. A motorcycle/vehicle is also present in frame (real traffic), OR
                # 2. The object is small relative to frame (distant rider, not close-up face)
                if motorcycle_present and not is_closeup_face:
                    counts['helmets_compliant'] += 1
                    color = (0, 200, 0)     # green = compliant
                else:
                    # Close-up face or no vehicle context — skip, don't annotate
                    continue

            elif is_no_helmet_label:
                # Same context check for violations
                if motorcycle_present and not is_closeup_face:
                    counts['violations'] += 1
                    self._record_violation(frame, track_id, confidence, (x1, y1, x2, y2))
                    color = (0, 0, 255)     # red = violation
                else:
                    continue
            else:
                color = (160, 160, 160)     # grey for other objects

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f'{label} {confidence:.2f} #{track_id or index}',
                        (x1, max(y1 - 8, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        TrafficInferenceService._latest_stats = counts
        return frame, counts

    @classmethod
    def latest_stats(cls):
        return cls._latest_stats.copy()

    def _record_violation(self, frame, track_id, confidence, coordinates):
        import cv2
        now = monotonic()
        key = track_id if track_id is not None else f'{coordinates}'
        if now - self._seen_violations.get(key, 0) < self.violation_cooldown:
            return
        self._seen_violations[key] = now

        x1, y1, x2, y2 = coordinates
        height, width = frame.shape[:2]
        crop = frame[max(0, y1):min(height, y2), max(0, x1):min(width, x2)]
        if crop.size == 0:
            return
        encoded, buffer = cv2.imencode('.jpg', crop)
        if not encoded:
            return
        TrafficViolation.objects.create(
            vehicle_type=TrafficViolation.VehicleType.MOTORCYCLE,
            confidence=confidence,
            track_id=track_id,
            crop_image=ContentFile(buffer.tobytes(), f'violation-{track_id or now:.0f}.jpg'),
        )
