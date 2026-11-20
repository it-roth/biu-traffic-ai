r"""
Cambodian Traffic AI Trainer: Custom YOLOv8/YOLOv11 Model Training
Tailored for Road Traffic Law of Cambodia (ច្បាប់ស្តីពីចរាចរណ៍ផ្លូវគោក)

Classes:
  0: car
  1: motorcycle
  2: auto_rickshaw (PassApp / Bajaj)
  3: remorque (Khmer Tuk-Tuk trailer)
  4: truck
  5: bus
  6: rider_helmet
  7: rider_no_helmet
  8: traffic_light_red
  9: traffic_light_green

Usage:
  # 1. Train with your custom dataset:
  python tools\train_cambodia_traffic.py --data tools\cambodia_traffic_dataset.yaml --epochs 50 --batch 4

  # 2. Or initialize a starter benchmark dataset & train 1 epoch test run:
  python tools\train_cambodia_traffic.py --generate-starter --epochs 3 --batch 2
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

import torch
import yaml
from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cambodian Traffic Safety AI Model Trainer")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("tools/cambodia_traffic_dataset.yaml"),
        help="Path to data.yaml dataset definition",
    )
    parser.add_argument(
        "--model",
        default="yolov8s.pt",
        help="Base pretrained model (e.g. yolov8s.pt, yolov8n.pt, yolo11s.pt, or best.pt)",
    )
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution")
    parser.add_argument("--batch", type=int, default=4, help="Batch size (reduce to 2 if low memory)")
    parser.add_argument("--workers", type=int, default=0, help="DataLoader workers (keep 0 on Windows)")
    parser.add_argument(
        "--device",
        default="0" if torch.cuda.is_available() else "cpu",
        help="Training device ('0' for CUDA GPU, 'cpu' for CPU)",
    )
    parser.add_argument("--project", default="tools/runs/cambodia_traffic", help="Save directory")
    parser.add_argument("--name", default="cambodia_ai_v1", help="Experiment run name")
    parser.add_argument("--generate-starter", action="store_true", help="Generate starter benchmark sample dataset")
    parser.add_argument("--deploy", action="store_true", default=True, help="Automatically deploy best.pt to backend/weights/")
    return parser.parse_args()


def generate_starter_dataset(dataset_dir: Path, data_yaml_path: Path) -> Path:
    """Creates directory layout and sample annotated images for testing the training loop."""
    print(f"\n[INFO] Generating starter dataset structure at: {dataset_dir}")
    train_img = dataset_dir / "images" / "train"
    val_img = dataset_dir / "images" / "val"
    train_lbl = dataset_dir / "labels" / "train"
    val_lbl = dataset_dir / "labels" / "val"

    for d in (train_img, val_img, train_lbl, val_lbl):
        d.mkdir(parents=True, exist_ok=True)

    # Copy existing scan uploads as training samples if available
    uploads_dir = Path("backend/media/uploads")
    if uploads_dir.is_dir():
        samples = list(uploads_dir.glob("*.jpg")) + list(uploads_dir.glob("*.webp"))
        for idx, s in enumerate(samples[:10]):
            target_img = train_img if idx % 4 != 0 else val_img
            target_lbl = train_lbl if idx % 4 != 0 else val_lbl
            dst_name = f"cambodia_sample_{idx}.jpg"
            shutil.copy(s, target_img / dst_name)

            # Sample annotations: motorcycle (1) + rider_no_helmet (7)
            # YOLO format: <class> <x_center> <y_center> <width> <height>
            lbl_file = target_lbl / f"cambodia_sample_{idx}.txt"
            lbl_file.write_text("1 0.5 0.6 0.3 0.4\n7 0.5 0.35 0.1 0.15\n0 0.8 0.5 0.25 0.3\n", encoding="utf-8")

    # Update data.yaml with absolute path
    config = {
        "path": str(dataset_dir.resolve()),
        "train": "images/train",
        "val": "images/val",
        "names": {
            0: "car",
            1: "motorcycle",
            2: "auto_rickshaw",
            3: "remorque",
            4: "truck",
            5: "bus",
            6: "rider_helmet",
            7: "rider_no_helmet",
            8: "traffic_light_red",
            9: "traffic_light_green",
        },
    }
    data_yaml_path.write_text(yaml.dump(config), encoding="utf-8")
    print(f"[SUCCESS] Starter dataset initialized! Updated YAML: {data_yaml_path.resolve()}\n")
    return data_yaml_path


def train() -> None:
    args = parse_args()

    print("=" * 65)
    print(" 🇰🇭 Cambodian Traffic Law AI - YOLO Training System")
    print("=" * 65)
    print(f"Base Model:       {args.model}")
    print(f"Target Epochs:    {args.epochs}")
    print(f"Batch Size:       {args.batch}")
    print(f"Device:           {args.device} ({'NVIDIA CUDA GPU' if args.device != 'cpu' else 'CPU Mode'})")
    print(f"Workers:          {args.workers}")

    data_yaml = args.data
    if args.generate_starter or not data_yaml.is_file():
        dataset_dir = Path("tools/cambodia_traffic_data")
        data_yaml = generate_starter_dataset(dataset_dir, data_yaml)

    # Load model
    print(f"\n[1/3] Loading base model weights: {args.model}...")
    model = YOLO(args.model)

    # Hyperparameters specifically tailored for dense Cambodian traffic
    print(f"\n[2/3] Starting training with Cambodian road condition augmentations...")
    print("  • Mosaic Augmentation: 1.0 (dense traffic vehicle occlusion)")
    print("  • Mixup: 0.15 (motorcycle passenger overlap learning)")
    print("  • Scale: 0.6 (distant vs close-up motorcycles)")
    print("  • HSV-S / HSV-V: 0.7 / 0.4 (rain, tropical sun, night headlight glare)")

    try:
        model.train(
            data=str(data_yaml.resolve()),
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            device=args.device,
            workers=args.workers,
            project=args.project,
            name=args.name,
            pretrained=True,
            patience=15,
            # Cambodian traffic augmentations
            mosaic=1.0,
            mixup=0.15,
            scale=0.6,
            hsv_s=0.7,
            hsv_v=0.4,
            close_mosaic=5,
            exist_ok=True,
        )
    except torch.cuda.OutOfMemoryError:
        print("\n[ERROR] GPU Out Of Memory. Re-running with smaller batch size is recommended:")
        print(f"  python tools\\train_cambodia_traffic.py --batch 2 --device {args.device}")
        sys.exit(1)

    # Verify best weights
    best_weights = Path(args.project) / args.name / "weights" / "best.pt"
    if best_weights.is_file():
        print(f"\n[SUCCESS] Training finished! Best weights: {best_weights.resolve()}")

        # Auto deploy to backend
        if args.deploy:
            deploy_target = Path("backend/weights/best.pt")
            deploy_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(best_weights, deploy_target)
            print(f"[DEPLOYED] Successfully updated backend weights: {deploy_target.resolve()}")
    else:
        print("\n[NOTE] Training session ended.")


if __name__ == "__main__":
    train()

