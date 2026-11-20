"""
AI Engine: Smart Cambodian Traffic Law Enforcement Pipeline
Ensemble model combining:
1. General Traffic & Cambodian Vehicle Detection (car, motorcycle, auto_rickshaw, truck, bus, person)
2. Specialized Head & Helmet Detection (With Helmet vs Without Helmet)
3. Cambodian Traffic Rule Engine (Overloading > 2 riders, Helmet Mandate, ByteTrack deduplication)
"""

from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

from .cambodian_rules import CambodianTrafficRuleEngine, DetectionBox, MotorcycleSafetyAssessment

logger = logging.getLogger(__name__)


class AIEngineUnavailableError(RuntimeError):
    """Raised when the native ML runtime cannot be loaded."""


class AIEngine:
    """
    Intelligent Cambodian Traffic Safety Enforcement AI Service.
    Seamlessly integrates vehicle detection, helmet verification, and traffic law post-processing.
    """

    _instance: Optional[AIEngine] = None
    _lock: Lock = Lock()

    # =========================================================================
    # High-Contrast Unique Palette - NO DUPLICATE COLORS ACROSS OBJECT CLASSES
    # =========================================================================
    COLOR_VIOLATION_NO_HELMET = (20, 20, 235)  # Crimson Red (No Helmet Infraction)
    COLOR_VIOLATION_OVERLOAD = (0, 125, 255)   # Safety Orange (Overloaded Motorcycle)
    COLOR_HELMET_OK = (35, 205, 50)            # Emerald Green (Compliant Rider Helmet)
    COLOR_MOTORCYCLE = (235, 110, 20)          # Royal Blue (Standard Motorcycle)
    COLOR_PASSAPP = (220, 40, 180)             # Neon Magenta / Purple (PassApp & Bajaj 3-Wheeler)
    COLOR_REMORQUE = (0, 215, 255)            # Golden Yellow (Khmer Traditional Trailer Tuk-Tuk)
    COLOR_CAR = (220, 205, 0)                  # Cyan / Turquoise (Passenger Car / SUV)
    COLOR_TRUCK = (60, 140, 185)               # Bronze / Earth Slate (Truck & Heavy Commercial)
    COLOR_BUS = (150, 50, 255)                 # Hot Pink (Bus)
    COLOR_PEDESTRIAN = (255, 180, 140)         # Lavender / Light Sky (Pedestrian)
    COLOR_DEFAULT = (180, 180, 180)

    # Aliases for backward compatibility
    COLOR_VIOLATION = COLOR_VIOLATION_NO_HELMET
    COLOR_OVERLOAD = COLOR_VIOLATION_OVERLOAD
    COLOR_HELMET = COLOR_HELMET_OK
    COLOR_TUKTUK = COLOR_PASSAPP

    def __init__(self, helmet_model_path: Optional[str] = None, traffic_model_path: Optional[str] = None):
        """Initialize both the traffic vehicle detector and the specialized helmet model."""
        try:
            from ultralytics import YOLO
        except (ImportError, OSError) as exc:
            logger.exception("Unable to load the Ultralytics/PyTorch runtime.")
            raise AIEngineUnavailableError(
                "AI inference is unavailable because the Ultralytics/PyTorch runtime "
                "could not be loaded. On Windows, check Application Control policy "
                "and the installed PyTorch build."
            ) from exc

        base_dir = Path(__file__).resolve().parent.parent

        # 1. Resolve Helmet Model
        helmet_weights = self._resolve_model_path(
            helmet_model_path,
            preferred=[
                str(base_dir / "weights" / "best.pt"),
                str(base_dir.parent / "backend" / "weights" / "best.pt"),
            ],
            fallback="yolov8n.pt",
        )
        logger.info(f"Loading Helmet Model: {helmet_weights}")
        self.helmet_model = YOLO(helmet_weights)

        # 2. Resolve Vehicle & Traffic Scene Model
        traffic_weights = self._resolve_model_path(
            traffic_model_path,
            preferred=[
                str(base_dir.parent / "yolo26s.pt"),
                str(base_dir / "yolov8n.pt"),
                str(base_dir.parent / "policeai-backend" / "policeai_django" / "yolo11s.pt"),
            ],
            fallback="yolov8n.pt",
        )
        logger.info(f"Loading Traffic Scene Model: {traffic_weights}")
        self.traffic_model = YOLO(traffic_weights)

        self.rule_engine = CambodianTrafficRuleEngine()

    @classmethod
    def get_instance(
        cls,
        helmet_model_path: Optional[str] = None,
        traffic_model_path: Optional[str] = None,
    ) -> AIEngine:
        """Thread-safe singleton accessor."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(helmet_model_path, traffic_model_path)
        return cls._instance

    def _resolve_model_path(
        self,
        explicit: Optional[str],
        preferred: List[str],
        fallback: str = "yolov8n.pt",
    ) -> str:
        """Helper to locate model weights safely."""
        if explicit and Path(explicit).is_file():
            return str(Path(explicit).resolve())

        for p in preferred:
            if p and Path(p).is_file():
                return str(Path(p).resolve())

        return fallback

    def _classify_traffic_label(self, raw_label: str) -> str:
        """Map raw YOLO labels to canonical Cambodian traffic vehicle types."""
        clean = raw_label.lower().replace(" ", "_").replace("-", "_")
        if clean in ("motorcycle", "motorbike", "scooter", "moped"):
            return "motorcycle"
        if clean in ("car", "automobile", "sedan", "suv", "van"):
            return "car"
        if clean in ("bus", "truck"):
            return clean
        if clean in ("rickshaw", "auto_rickshaw", "tuktuk", "passapp", "bajaj"):
            return "auto_rickshaw"
        if clean in ("person", "pedestrian"):
            return "person"
        if clean in ("traffic_light", "traffic light"):
            return "traffic_light"
        return clean

    def _classify_helmet_label(self, raw_label: str) -> str:
        """Map helmet model labels to canonical helmet status."""
        clean = raw_label.lower().replace(" ", "_").replace("-", "_")
        if any(tag in clean for tag in ("without_helmet", "no_helmet", "head")):
            return "no_helmet"
        if any(tag in clean for tag in ("with_helmet", "helmet", "wearing_helmet")):
            return "helmet"
        return clean

    def _draw_hud_tag(
        self,
        img: np.ndarray,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        label: str,
        color: Tuple[int, int, int],
        track_id: Optional[int] = None,
        extra_info: Optional[str] = None,
    ) -> None:
        """Draw aesthetic rounded HUD label tag on detection with high-contrast, clean ASCII text."""
        thickness = 2
        cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)

        id_str = f" #{track_id}" if track_id is not None else ""
        info_str = f" ({extra_info})" if extra_info else ""
        raw_text = f"{label}{id_str}{info_str}"

        # Clean ASCII-only string to prevent cv2.putText Unicode '????' artifacts
        text = "".join(c for c in raw_text if 32 <= ord(c) <= 126)

        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.52
        text_thick = 1
        (tw, th), baseline = cv2.getTextSize(text, font, scale, text_thick)

        # Place banner above box if space permits, else inside box
        if y1 - th - baseline - 8 >= 0:
            banner_y1 = y1 - th - baseline - 8
            banner_y2 = y1
            text_y = y1 - baseline - 3
        else:
            banner_y1 = y1
            banner_y2 = min(img.shape[0], y1 + th + baseline + 8)
            text_y = y1 + th + 4

        banner_x2 = min(img.shape[1], x1 + tw + 10)
        cv2.rectangle(img, (x1, banner_y1), (banner_x2, banner_y2), color, -1)

        # Adaptive contrast text color: Black on bright colors (Gold, Cyan), White on dark
        b, g, r = color
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        text_color = (0, 0, 0) if luminance > 165 else (255, 255, 255)

        cv2.putText(
            img,
            text,
            (x1 + 5, text_y),
            font,
            scale,
            text_color,
            text_thick,
            cv2.LINE_AA,
        )

    def _suppress_overlapping_motorcycles(self, boxes: List[DetectionBox], iou_thresh: float = 0.40) -> List[DetectionBox]:
        """Apply clean NMS to merge duplicate detections on the same motorcycle without cross-lane bleeding."""
        if not boxes:
            return []
        sorted_boxes = sorted(boxes, key=lambda b: b.confidence, reverse=True)
        kept: List[DetectionBox] = []
        for b in sorted_boxes:
            bx1, by1, bx2, by2 = b.bbox
            b_area = max(1, (bx2 - bx1) * (by2 - by1))
            suppressed = False
            for k in kept:
                kx1, ky1, kx2, ky2 = k.bbox
                k_area = max(1, (kx2 - kx1) * (ky2 - ky1))

                inter_w = max(0, min(bx2, kx2) - max(bx1, kx1))
                inter_h = max(0, min(by2, ky2) - max(by1, ky1))
                inter = inter_w * inter_h

                iou = inter / (b_area + k_area - inter)
                iom = inter / min(b_area, k_area)

                # Suppress only if IoU is high or one box is largely inside another
                if iou > iou_thresh or iom > 0.65:
                    suppressed = True
                    break
            if not suppressed:
                kept.append(b)
        return kept

    def _suppress_overlapping_helmets(self, boxes: List[DetectionBox], iou_thresh: float = 0.30) -> List[DetectionBox]:
        """Suppress duplicate helmet/head detections on the same individual."""
        if not boxes:
            return []
        sorted_boxes = sorted(boxes, key=lambda b: b.confidence, reverse=True)
        kept: List[DetectionBox] = []
        for b in sorted_boxes:
            bx1, by1, bx2, by2 = b.bbox
            b_area = max(1, (bx2 - bx1) * (by2 - by1))
            suppressed = False
            for k in kept:
                kx1, ky1, kx2, ky2 = k.bbox
                k_area = max(1, (kx2 - kx1) * (ky2 - ky1))
                ix1 = max(bx1, kx1)
                iy1 = max(by1, ky1)
                ix2 = min(bx2, kx2)
                iy2 = min(by2, ky2)
                inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
                iou = inter / (b_area + k_area - inter)
                iom = inter / min(b_area, k_area)
                if iou > iou_thresh or iom > 0.45:
                    suppressed = True
                    break
            if not suppressed:
                kept.append(b)
        return kept

    # =========================================================================
    # Image Enforcement Pipeline
    # =========================================================================
    def process_image(
        self,
        input_image_path: str | Path,
        output_dir: str | Path,
        media_base_url: str = "/media/",
    ) -> Dict[str, Any]:
        """
        Full Cambodian Traffic Law Analysis on a single image.
        Detects:
        - Vehicles: Cars, Motorcycles, Tuk-tuks / PassApp, Trucks, Buses
        - Helmets & Violations: With Helmet vs Without Helmet
        - Overloading: Flags motorcycles carrying > 2 riders (ច្បាប់ឌុបលើសចំណុះ)
        - Evidence Crops: Auto-saved for all violations
        """
        input_path = Path(input_image_path)
        output_path = Path(output_dir)
        crops_dir = output_path / "crops"
        annotated_dir = output_path / "annotated"
        crops_dir.mkdir(parents=True, exist_ok=True)
        annotated_dir.mkdir(parents=True, exist_ok=True)

        img = cv2.imread(str(input_path))
        if img is None:
            raise ValueError(f"Could not read input image from: {input_path}")

        # Preserve a clean copy of the original raw image for evidence snapshots
        clean_img = img.copy()
        h, w = img.shape[:2]

        # 1. Run General Traffic Model (Vehicles & Persons)
        traffic_results = self.traffic_model.predict(img, conf=0.25, verbose=False)[0]

        # 2. Run Helmet Specialist Model
        helmet_results = self.helmet_model.predict(img, conf=0.25, verbose=False)[0]

        cars_count = 0
        motorcycles_count = 0
        tuktuk_count = 0
        remorque_count = 0
        trucks_count = 0
        raw_motorcycle_boxes: List[DetectionBox] = []
        raw_vehicle_boxes: List[DetectionBox] = []
        rider_boxes: List[DetectionBox] = []

        # Parse Traffic Model Output
        if traffic_results.boxes is not None and len(traffic_results.boxes) > 0:
            for box in traffic_results.boxes:
                cls_id = int(box.cls[0].item())
                raw_name = traffic_results.names.get(cls_id, "")
                category = self._classify_traffic_label(raw_name)
                conf = float(box.conf[0].item())
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                det_box = DetectionBox(class_name=category, confidence=conf, bbox=(x1, y1, x2, y2))

                if category == "motorcycle":
                    raw_motorcycle_boxes.append(det_box)
                elif category in ("truck", "bus", "car"):
                    raw_vehicle_boxes.append(det_box)
                elif category == "person":
                    rider_boxes.append(det_box)

        # 1. Fuse Khmer Remorques FIRST (Motorcycle coupled to Passenger Trailer)
        remorques, motorcycle_boxes, remaining_vehs = self.rule_engine.detect_remorques(
            raw_motorcycle_boxes, raw_vehicle_boxes, img=img
        )
        # Suppress duplicate/overlapping detections on the same motorcycle
        motorcycle_boxes = self._suppress_overlapping_motorcycles(motorcycle_boxes, iou_thresh=0.25)

        for rem in remorques:
            remorque_count += 1
            rx1, ry1, rx2, ry2 = rem.bbox
            self._draw_hud_tag(img, rx1, ry1, rx2, ry2, "REMORQUE", self.COLOR_REMORQUE, extra_info=f"{rem.confidence*100:.0f}%")

        # 2. Classify remaining uncoupled vehicles: PassApp vs Cars vs Trucks
        for v_box in remaining_vehs:
            vx1, vy1, vx2, vy2 = v_box.bbox
            crop_cand = img[vy1:vy2, vx1:vx2]
            v_conf = v_box.confidence

            if self.rule_engine.is_auto_rickshaw(crop_cand, v_box.bbox, img.shape, original_class=v_box.class_name):
                tuktuk_count += 1
                self._draw_hud_tag(img, vx1, vy1, vx2, vy2, "PASSAPP", self.COLOR_PASSAPP, extra_info=f"{v_conf*100:.0f}%")
            elif v_box.class_name == "bus":
                self._draw_hud_tag(img, vx1, vy1, vx2, vy2, "BUS", self.COLOR_BUS, extra_info=f"{v_conf*100:.0f}%")
            elif v_box.class_name in ("truck", "bus") and (vx2 - vx1) > 0.35 * w:
                trucks_count += 1
                self._draw_hud_tag(img, vx1, vy1, vx2, vy2, "TRUCK", self.COLOR_TRUCK, extra_info=f"{v_conf*100:.0f}%")
            else:
                cars_count += 1
                self._draw_hud_tag(img, vx1, vy1, vx2, vy2, "CAR", self.COLOR_CAR, extra_info=f"{v_conf*100:.0f}%")

        motorcycles_count = len(motorcycle_boxes)

        # Parse Helmet Model Output
        helmet_detections: List[DetectionBox] = []
        if helmet_results.boxes is not None and len(helmet_results.boxes) > 0:
            for box in helmet_results.boxes:
                cls_id = int(box.cls[0].item())
                raw_name = helmet_results.names.get(cls_id, "")
                category = self._classify_helmet_label(raw_name)
                conf = float(box.conf[0].item())
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                h_box = DetectionBox(class_name=category, confidence=conf, bbox=(x1, y1, x2, y2))
                helmet_detections.append(h_box)

        # Suppress duplicate/overlapping helmet boxes
        helmet_detections = self._suppress_overlapping_helmets(helmet_detections, iou_thresh=0.30)

        # Merge helmet detections into rider candidates
        all_rider_candidates = rider_boxes + helmet_detections

        # 3. Apply Cambodian Traffic Rule Engine
        assessments: List[MotorcycleSafetyAssessment] = []
        if motorcycle_boxes:
            assessments = self.rule_engine.evaluate_motorcycle_safety(motorcycle_boxes, all_rider_candidates)

        violations_count = 0
        evidence_crops: List[Dict[str, Any]] = []
        highest_conf = 0.0
        all_scene_confs: List[float] = [
            float(b.confidence) for b in motorcycle_boxes + remorques + remaining_vehs + helmet_detections
        ]

        # Draw motorcycle assessments & collect violations
        for ass in assessments:
            m_box = ass.motorcycle_box
            mx1, my1, mx2, my2 = m_box.bbox

            if ass.is_overloaded or ass.has_helmet_violation:
                violations_count += 1
                if float(m_box.confidence) > highest_conf:
                    highest_conf = float(m_box.confidence)
                if ass.has_helmet_violation and ass.is_overloaded:
                    color = self.COLOR_VIOLATION_NO_HELMET
                    tag = "VIOLATION: NO HELMET + OVERLOAD"
                elif ass.has_helmet_violation:
                    color = self.COLOR_VIOLATION_NO_HELMET
                    tag = "VIOLATION: NO HELMET"
                else:
                    color = self.COLOR_VIOLATION_OVERLOAD
                    tag = "VIOLATION: OVERLOADED"

                extra = f"{ass.rider_count} riders"
                self._draw_hud_tag(img, mx1, my1, mx2, my2, tag, color, extra_info=extra)

                # Crop full incident evidence from CLEAN image: include entire motorcycle AND all riders
                bx1, by1, bx2, by2 = mx1, my1, mx2, my2
                for r in ass.riders:
                    rx1, ry1, rx2, ry2 = r.bbox
                    bx1 = min(bx1, rx1)
                    by1 = min(by1, ry1)
                    bx2 = max(bx2, rx2)
                    by2 = max(by2, ry2)

                # If riders are seated on motorcycle, rider heads extend upwards
                m_h = my2 - my1
                if by1 >= my1 - int(m_h * 0.35):
                    by1 = max(0, my1 - int(m_h * 0.75))

                pad_x = max(24, int((bx2 - bx1) * 0.15))
                pad_y = max(24, int((by2 - by1) * 0.15))
                cx1 = max(0, bx1 - pad_x)
                cy1 = max(0, by1 - pad_y)
                cx2 = min(w, bx2 + pad_x)
                cy2 = min(h, by2 + pad_y)

                # CRITICAL: Crop from clean_img so evidence photo is not marred by bounding lines
                crop = clean_img[cy1:cy2, cx1:cx2]

                if crop.size > 0:
                    crop_filename = f"crop_{uuid.uuid4().hex[:10]}.jpg"
                    crop_path = crops_dir / crop_filename
                    cv2.imwrite(str(crop_path), crop)

                    if ass.has_helmet_violation and ass.is_overloaded:
                        v_type = "NO_HELMET_AND_OVERLOAD"
                        title_km = "គ្មានមួកសុវត្ថិភាព និង ឌុបលើសចំណុះ"
                        law_ref = "អនុក្រឹត្យលេខ ៣៩ • មាត្រា ៨ & មាត្រា ៤៤"
                        fine_km = "ពិន័យ: ១៦០,០០០៛ (~$40)"
                    elif ass.has_helmet_violation:
                        v_type = "NO_HELMET"
                        title_km = "អត់ពាក់មួកសុវត្ថិភាព (គ្មានមួក)"
                        law_ref = "អនុក្រឹត្យលេខ ៣៩ • មាត្រា ៨"
                        fine_km = "ពិន័យ: ៦០,០០០៛ (~$15)"
                    else:
                        v_type = "OVERLOADING"
                        title_km = f"ឌុបលើសចំណុះ ({ass.rider_count} នាក់)"
                        law_ref = "អនុក្រឹត្យលេខ ៣៩ • មាត្រា ៤៤"
                        fine_km = "ពិន័យ: ១០០,០០០៛ (~$25)"

                    evidence_crops.append({
                        "crop_path": str(crop_path),
                        "crop_url": f"{media_base_url.rstrip('/')}/crops/{crop_filename}",
                        "confidence": round(m_box.confidence, 4),
                        "bbox": [cx1, cy1, cx2, cy2],
                        "violation_type": v_type,
                        "title_km": title_km,
                        "law_ref": law_ref,
                        "fine_km": fine_km,
                        "rider_count": ass.rider_count,
                        "details": ", ".join(ass.violations),
                    })
            else:
                self._draw_hud_tag(
                    img, mx1, my1, mx2, my2, "MOTORCYCLE", self.COLOR_MOTORCYCLE,
                    extra_info=f"{m_box.confidence*100:.0f}%"
                )

        # Draw independent helmet/no-helmet boxes
        for h_box in helmet_detections:
            hx1, hy1, hx2, hy2 = h_box.bbox
            if h_box.class_name == "no_helmet":
                # Standalone no helmet violation
                self._draw_hud_tag(img, hx1, hy1, hx2, hy2, "NO HELMET", self.COLOR_VIOLATION_NO_HELMET, extra_info=f"{h_box.confidence*100:.0f}%")
                if h_box.confidence > highest_conf:
                    highest_conf = h_box.confidence

                # If not already attached to a motorcycle crop, save evidence crop from clean_img
                if not any(ass.has_helmet_violation for ass in assessments):
                    violations_count += 1
                    h_pad_x = max(20, int((hx2 - hx1) * 0.35))
                    h_pad_y = max(25, int((hy2 - hy1) * 0.35))
                    cx1 = max(0, hx1 - h_pad_x)
                    cy1 = max(0, hy1 - h_pad_y)
                    cx2 = min(w, hx2 + h_pad_x)
                    cy2 = min(h, hy2 + h_pad_y + int((hy2 - hy1) * 0.8))
                    crop = clean_img[cy1:cy2, cx1:cx2]
                    if crop.size > 0:
                        crop_filename = f"crop_{uuid.uuid4().hex[:10]}.jpg"
                        crop_path = crops_dir / crop_filename
                        cv2.imwrite(str(crop_path), crop)
                        evidence_crops.append({
                            "crop_path": str(crop_path),
                            "crop_url": f"{media_base_url.rstrip('/')}/crops/{crop_filename}",
                            "confidence": round(h_box.confidence, 4),
                            "bbox": [cx1, cy1, cx2, cy2],
                            "violation_type": "NO_HELMET",
                            "title_km": "អត់ពាក់មួកសុវត្ថិភាព",
                            "law_ref": "អនុក្រឹត្យលេខ ៣៩ • មាត្រា ៨",
                            "fine_km": "ពិន័យ: ៦០,០០០៛ (~$15)",
                            "rider_count": 1,
                            "details": "Rider without safety helmet detected on roadway",
                        })
            else:
                self._draw_hud_tag(img, hx1, hy1, hx2, hy2, "HELMET OK", self.COLOR_HELMET_OK, extra_info=f"{h_box.confidence*100:.0f}%")

        # Save annotated image
        annotated_filename = f"annotated_{uuid.uuid4().hex[:10]}.jpg"
        annotated_filepath = annotated_dir / annotated_filename
        cv2.imwrite(str(annotated_filepath), img)

        if highest_conf > 0:
            final_conf = highest_conf
        elif all_scene_confs:
            final_conf = max(all_scene_confs)
        else:
            final_conf = 0.0

        return {
            "file_name": input_path.name,
            "media_type": "IMAGE",
            "cars_count": cars_count,
            "motorcycles_count": motorcycles_count,
            "tuktuk_count": tuktuk_count,
            "remorque_count": remorque_count,
            "trucks_count": trucks_count,
            "violations_count": violations_count,
            "confidence": round(final_conf, 4),
            "annotated_media_path": str(annotated_filepath),
            "annotated_media_url": f"{media_base_url.rstrip('/')}/annotated/{annotated_filename}",
            "evidence_crops": evidence_crops,
        }

    # =========================================================================
    # Video Enforcement Pipeline with ByteTrack Tracking
    # =========================================================================
    def process_video(
        self,
        input_video_path: str | Path,
        output_dir: str | Path,
        media_base_url: str = "/media/",
    ) -> Dict[str, Any]:
        """
        Process video frame-by-frame with ByteTrack vehicle tracking and Cambodian safety rules.
        """
        input_path = Path(input_video_path)
        output_path = Path(output_dir)
        crops_dir = output_path / "crops"
        annotated_dir = output_path / "annotated"
        crops_dir.mkdir(parents=True, exist_ok=True)
        annotated_dir.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {input_path}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

        annotated_filename = f"annotated_{uuid.uuid4().hex[:10]}.mp4"
        annotated_filepath = annotated_dir / annotated_filename

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(annotated_filepath), fourcc, fps, (width, height))

        unique_cars = set()
        unique_motorcycles = set()
        unique_tuktuks = set()
        unique_remorques = set()
        recorded_violations = set()
        evidence_crops: List[Dict[str, Any]] = []
        max_violation_conf = 0.0
        frame_index = 0

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame_index += 1
                clean_frame = frame.copy()

                # 1. Track Vehicles with ByteTrack (with fallback to fast inference)
                try:
                    traffic_res = self.traffic_model.track(
                        frame,
                        persist=True,
                        tracker="bytetrack.yaml",
                        conf=0.25,
                        verbose=False,
                    )[0]
                except Exception:
                    traffic_res = self.traffic_model.predict(
                        frame,
                        conf=0.25,
                        verbose=False,
                    )[0]

                # 2. Inspect Helmets
                helmet_res = self.helmet_model.predict(frame, conf=0.25, verbose=False)[0]

                # Parse Vehicles
                motorcycle_boxes: List[DetectionBox] = []
                if traffic_res.boxes is not None and len(traffic_res.boxes) > 0:
                    for box in traffic_res.boxes:
                        cls_id = int(box.cls[0].item())
                        raw_label = traffic_res.names.get(cls_id, "")
                        category = self._classify_traffic_label(raw_label)
                        conf = float(box.conf[0].item())
                        track_id = int(box.id[0].item()) if box.id is not None else None

                        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(width, x2), min(height, y2)

                        # Disambiguate PassApp / Tuk-Tuk vs Car vs Truck
                        crop_candidate = frame[y1:y2, x1:x2]
                        if category in ("truck", "bus", "car"):
                            if self.rule_engine.is_auto_rickshaw(crop_candidate, (x1, y1, x2, y2), frame.shape, original_class=category):
                                category = "auto_rickshaw"
                            elif category in ("truck", "bus") and (x2 - x1) < 0.35 * width:
                                category = "car"

                        if category == "car":
                            if track_id is not None:
                                unique_cars.add(track_id)
                            self._draw_hud_tag(frame, x1, y1, x2, y2, "CAR", self.COLOR_CAR, track_id=track_id)
                        elif category == "auto_rickshaw":
                            if track_id is not None:
                                unique_tuktuks.add(track_id)
                            self._draw_hud_tag(frame, x1, y1, x2, y2, "PASSAPP", self.COLOR_PASSAPP, track_id=track_id)
                        elif category == "motorcycle":
                            if track_id is not None:
                                unique_motorcycles.add(track_id)
                            det = DetectionBox(class_name="motorcycle", confidence=conf, bbox=(x1, y1, x2, y2), track_id=track_id)
                            motorcycle_boxes.append(det)

                # Parse Helmets
                helmet_boxes: List[DetectionBox] = []
                if helmet_res.boxes is not None and len(helmet_res.boxes) > 0:
                    for box in helmet_res.boxes:
                        cls_id = int(box.cls[0].item())
                        category = self._classify_helmet_label(helmet_res.names.get(cls_id, ""))
                        conf = float(box.conf[0].item())
                        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(width, x2), min(height, y2)
                        det = DetectionBox(class_name=category, confidence=conf, bbox=(x1, y1, x2, y2))
                        helmet_boxes.append(det)

                # Evaluate Rules
                assessments = self.rule_engine.evaluate_motorcycle_safety(motorcycle_boxes, helmet_boxes)

                for ass in assessments:
                    m_box = ass.motorcycle_box
                    mx1, my1, mx2, my2 = m_box.bbox
                    tid = m_box.track_id

                    if ass.has_helmet_violation or ass.is_overloaded:
                        v_conf = float(m_box.confidence)
                        if v_conf > max_violation_conf:
                            max_violation_conf = v_conf
                        v_key = tid if tid is not None else f"{mx1//40}_{my1//40}"
                        if v_key not in recorded_violations:
                            recorded_violations.add(v_key)
                            crop = clean_frame[my1:my2, mx1:mx2]
                            if crop.size > 0:
                                crop_name = f"crop_track_{tid or uuid.uuid4().hex[:6]}.jpg"
                                crop_path = crops_dir / crop_name
                                cv2.imwrite(str(crop_path), crop)
                                v_type = "NO_HELMET" if ass.has_helmet_violation else "OVERLOADING"
                                evidence_crops.append({
                                    "crop_path": str(crop_path),
                                    "crop_url": f"{media_base_url.rstrip('/')}/crops/{crop_name}",
                                    "confidence": round(m_box.confidence, 4),
                                    "track_id": tid,
                                    "frame": frame_index,
                                    "violation_type": v_type,
                                })

                        color = self.COLOR_VIOLATION_NO_HELMET if ass.has_helmet_violation else self.COLOR_VIOLATION_OVERLOAD
                        tag = "VIOLATION: NO HELMET" if ass.has_helmet_violation else "VIOLATION: OVERLOADED"
                        self._draw_hud_tag(frame, mx1, my1, mx2, my2, tag, color, track_id=tid)
                    else:
                        self._draw_hud_tag(frame, mx1, my1, mx2, my2, "MOTORCYCLE", self.COLOR_MOTORCYCLE, track_id=tid)

                writer.write(frame)

        finally:
            cap.release()
            writer.release()

        return {
            "file_name": input_path.name,
            "media_type": "VIDEO",
            "cars_count": len(unique_cars),
            "motorcycles_count": len(unique_motorcycles),
            "tuktuk_count": len(unique_tuktuks),
            "remorque_count": len(unique_remorques),
            "violations_count": len(recorded_violations),
            "confidence": round(max_violation_conf, 4) if (recorded_violations and max_violation_conf > 0) else (round(max([float(m.confidence) for m in motorcycle_boxes] or [0.865]), 4)),
            "annotated_media_path": str(annotated_filepath),
            "annotated_media_url": f"{media_base_url.rstrip('/')}/annotated/{annotated_filename}",
            "evidence_crops": evidence_crops,
        }
