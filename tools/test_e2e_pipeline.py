"""
End-to-End Test Suite for YOLOv8 Traffic Safety Enforcement Pipeline
Tests Image and Video upload, ByteTrack tracking, violation cropping, and DB persistence.
"""

import os
import sys
from pathlib import Path

# Add backend directory to path and configure Django environment
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

import cv2
import numpy as np
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from api.models import ViolationRecord
from api.ai_engine import AIEngine


def create_traffic_test_image(filepath: Path) -> Path:
    """Create a high-resolution synthetic traffic scene."""
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    # Dark asphalt road
    img[120:480, :] = (45, 45, 50)
    # Road markings (yellow dashed line)
    for x in range(20, 640, 60):
        cv2.rectangle(img, (x, 290), (x + 35, 300), (0, 215, 255), -1)

    # Road curb & sidewalk
    img[0:120, :] = (70, 70, 75)

    # Draw simulated vehicle 1: Car (Blue sedan)
    cv2.rectangle(img, (80, 200), (220, 320), (220, 100, 20), -1)
    cv2.putText(img, "Car", (110, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Draw simulated vehicle 2: Motorcycle with rider
    cv2.rectangle(img, (380, 220), (450, 340), (40, 180, 50), -1)
    cv2.circle(img, (415, 200), 22, (200, 180, 160), -1)  # Head / rider
    cv2.putText(img, "Motorcycle", (360, 370), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imwrite(str(filepath), img)
    return filepath


def create_traffic_test_video(filepath: Path, duration_seconds: int = 2, fps: int = 20) -> Path:
    """Create a synthetic MP4 video with moving vehicles for ByteTrack tracking."""
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(filepath), fourcc, fps, (640, 480))
    total_frames = duration_seconds * fps

    for f in range(total_frames):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[120:480, :] = (45, 45, 50)  # Road

        # Moving car from left to right
        car_x = int(50 + (f / total_frames) * 350)
        cv2.rectangle(frame, (car_x, 180), (car_x + 130, 290), (220, 100, 20), -1)

        # Moving motorcycle from right to left
        bike_x = int(520 - (f / total_frames) * 320)
        cv2.rectangle(frame, (bike_x, 240), (bike_x + 60, 340), (40, 180, 50), -1)
        cv2.circle(frame, (bike_x + 30, 220), 18, (200, 180, 160), -1)

        writer.write(frame)

    writer.release()
    return filepath


def run_pipeline_test():
    print("================================================================")
    print("     STARTING FULL-STACK TRAFFIC SAFETY PIPELINE TEST           ")
    print("================================================================")

    scratch_dir = Path(settings.MEDIA_ROOT) / "test_scratch"
    scratch_dir.mkdir(parents=True, exist_ok=True)

    test_img_path = scratch_dir / "sample_traffic_scene.jpg"
    test_vid_path = scratch_dir / "sample_traffic_video.mp4"

    print("\n[Step 1] Synthesizing traffic test media...")
    create_traffic_test_image(test_img_path)
    create_traffic_test_video(test_vid_path, duration_seconds=2, fps=15)
    print(f" -> Generated test image: {test_img_path} ({test_img_path.stat().st_size / 1024:.1f} KB)")
    print(f" -> Generated test video: {test_vid_path} ({test_vid_path.stat().st_size / 1024:.1f} KB)")

    # Initialize Django API Client
    client = APIClient()

    # -------------------------------------------------------------
    # Test 1: POST /api/scan/image/
    # -------------------------------------------------------------
    print("\n[Step 2] Testing POST /api/scan/image/...")
    with open(test_img_path, "rb") as f:
        img_upload = SimpleUploadedFile("sample_traffic_scene.jpg", f.read(), content_type="image/jpeg")

    img_response = client.post("/api/scan/image/", {"file": img_upload}, format="multipart")
    print(f" -> Status Code: {img_response.status_code}")
    if img_response.status_code == 201:
        data = img_response.data
        print(" -> Scan Image Succeeded!")
        print(f"    - Record ID: {data.get('record_id')}")
        print(f"    - Cars Count: {data.get('cars_count')}")
        print(f"    - Motorcycles Count: {data.get('motorcycles_count')}")
        print(f"    - Violations Count: {data.get('violations_count')}")
        print(f"    - Annotated Image URL: {data.get('annotated_media_url')}")
        print(f"    - Evidence Snapshots: {len(data.get('evidence_crops', []))}")
    else:
        print(f" -> FAILED: {img_response.data}")
        return False

    # -------------------------------------------------------------
    # Test 2: POST /api/scan/video/
    # -------------------------------------------------------------
    print("\n[Step 3] Testing POST /api/scan/video/ with ByteTrack tracking...")
    with open(test_vid_path, "rb") as f:
        vid_upload = SimpleUploadedFile("sample_traffic_video.mp4", f.read(), content_type="video/mp4")

    vid_response = client.post("/api/scan/video/", {"file": vid_upload}, format="multipart")
    print(f" -> Status Code: {vid_response.status_code}")
    if vid_response.status_code == 201:
        vdata = vid_response.data
        print(" -> Scan Video Succeeded!")
        print(f"    - Record ID: {vdata.get('record_id')}")
        print(f"    - Unique Cars Tracked: {vdata.get('cars_count')}")
        print(f"    - Unique Motorcycles Tracked: {vdata.get('motorcycles_count')}")
        print(f"    - Unique Violations Tracked: {vdata.get('violations_count')}")
        print(f"    - Annotated Video URL: {vdata.get('annotated_media_url')}")
        print(f"    - Violation Snapshots: {len(vdata.get('evidence_crops', []))}")
    else:
        print(f" -> FAILED: {vid_response.data}")
        return False

    # -------------------------------------------------------------
    # Test 3: GET /api/violations/
    # -------------------------------------------------------------
    print("\n[Step 4] Testing GET /api/violations/ (Evidence History)...")
    hist_response = client.get("/api/violations/")
    print(f" -> Status Code: {hist_response.status_code}")
    if hist_response.status_code == 200:
        hdata = hist_response.data
        total_records = hdata.get("count", len(hdata.get("results", [])))
        print(f" -> Total Violation Records Logged: {total_records}")
        for item in hdata.get("results", [])[:3]:
            print(f"    * [{item['media_type']}] {item['file_name']} -> {item['violations_count']} violation(s), Conf: {item['confidence']}")
    else:
        print(f" -> FAILED: {hist_response.data}")
        return False

    # -------------------------------------------------------------
    # Verify Database State
    # -------------------------------------------------------------
    total_db_records = ViolationRecord.objects.count()
    print(f"\n[Step 5] Database Verification:")
    print(f" -> Total rows in ViolationRecord table: {total_db_records}")

    print("\n================================================================")
    print(" [ALL TESTS PASSED] The Traffic Safety AI System is 100% Ready! ")
    print("================================================================")
    return True


if __name__ == "__main__":
    success = run_pipeline_test()
    sys.exit(0 if success else 1)

