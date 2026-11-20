r"""Train, evaluate, and optionally export a local Ultralytics YOLO model.

Example:
    python tools\train_yolo.py --project-root D:\policeai-models\YOLO26s --dataset-root <path_to_dataset>
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

import torch
import yaml
from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True, help="Folder containing dataset or zip")
    parser.add_argument("--model", default="yolov8s.pt", help="Base model weights (e.g. yolov8s.pt, yolo11s.pt, or best.pt)")
    parser.add_argument("--dataset-zip", type=Path, help="Explicit path to dataset .zip file")
    parser.add_argument("--dataset-root", type=Path, help="Folder containing data.yaml")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size for YOLO")
    parser.add_argument("--batch", type=int, default=4, help="Batch size (reduce to 2 or 4 if GPU runs out of VRAM)")
    parser.add_argument("--workers", type=int, default=0, help="DataLoader workers (default 0 on Windows to prevent multiprocessing errors)")
    parser.add_argument("--device", default="0" if torch.cuda.is_available() else "cpu", help="Device '0' for CUDA GPU or 'cpu'")
    parser.add_argument("--run-name", default="police_ai_training", help="Experiment run name")
    parser.add_argument("--export-onnx", action="store_true", help="Export best model to ONNX after training")
    return parser.parse_args()


def find_data_yaml(project_root: Path, dataset_root: Path | None) -> Path:
    candidates = []
    if dataset_root:
        candidates.append(dataset_root / "data.yaml")
    candidates.extend((project_root / name / "data.yaml" for name in ("yolo_dataset", "dataset_coco", "PoliceAI.v7i.yolo26")))
    candidates.extend(project_root.glob("**/data.yaml"))

    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()

    raise FileNotFoundError(
        f"\n[ERROR] No 'data.yaml' found under: {project_root.resolve()}\n"
        f"Troubleshooting:\n"
        f" 1. If you have a dataset zip (e.g. PoliceAI.v7i.yolo26.zip), place it in {project_root} or pass --dataset-zip <path>.\n"
        f" 2. If your dataset is unzipped elsewhere, pass --dataset-root <path> containing data.yaml.\n"
        f" 3. Make sure data.yaml defines 'train', 'val', and class names ('car', 'motorcycle', 'helmet', 'no_helmet').\n"
    )


def prepare_dataset(args: argparse.Namespace) -> Path:
    if args.dataset_root:
        return find_data_yaml(args.project_root, args.dataset_root)

    zip_path = args.dataset_zip
    if zip_path is None:
        zips = list(args.project_root.glob("*.zip"))
        zip_path = zips[0] if len(zips) == 1 else None

    if zip_path is not None and zip_path.is_file():
        target = args.project_root / "yolo_dataset"
        target.mkdir(parents=True, exist_ok=True)
        print(f"Extracting dataset {zip_path.name} -> {target}...")
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(target)

    return find_data_yaml(args.project_root, None)


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    print(f"=== YOLOv8 Training Pipeline ===")
    print(f"Project root: {project_root}")

    try:
        data_yaml = prepare_dataset(args)
    except FileNotFoundError as err:
        print(err, file=sys.stderr)
        sys.exit(1)

    config = yaml.safe_load(data_yaml.read_text(encoding="utf-8"))
    classes = config.get("names", {})
    print(f"Dataset YAML: {data_yaml}")
    print(f"Classes ({len(classes)}): {classes}")
    print(f"Device: {args.device} | Batch: {args.batch} | Workers: {args.workers}")

    # Warn if no_helmet is missing in dataset classes
    class_list = [str(c).lower() for c in (classes.values() if isinstance(classes, dict) else classes)]
    if not any("no_helmet" in c or "without_helmet" in c for c in class_list):
        print(
            "\n[WARNING] Dataset does not contain a 'no_helmet' class!\n"
            "Classes found: " + ", ".join(class_list) + "\n"
            "For traffic safety violation enforcement, annotate helmet violations as 'no_helmet'.\n"
        )

    output_root = project_root / "output"
    model = YOLO(args.model)

    try:
        model.train(
            data=str(data_yaml),
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            device=args.device,
            workers=args.workers,
            project=str(output_root),
            name=args.run_name,
            patience=20,
            pretrained=True,
            plots=True,
            exist_ok=True,
        )
    except torch.cuda.OutOfMemoryError:
        print(
            "\n[CUDA OOM ERROR] GPU ran out of memory on batch size {args.batch}!\n"
            "Try re-running with a smaller batch size:\n"
            f"  python tools\\train_yolo.py --project-root {project_root} --batch 2 --workers 0\n"
            "Or train on CPU:\n"
            f"  python tools\\train_yolo.py --project-root {project_root} --device cpu\n",
            file=sys.stderr,
        )
        sys.exit(1)

    best_path = output_root / args.run_name / "weights" / "best.pt"
    if not best_path.is_file():
        raise FileNotFoundError(f"Training completed without {best_path}")

    print(f"\n[SUCCESS] Best model saved to: {best_path}")

    best_model = YOLO(str(best_path))
    metrics = best_model.val(
        data=str(data_yaml),
        split="test" if (data_yaml.parent / "test").exists() else "val",
        imgsz=args.imgsz,
        device=args.device,
    )
    print(f"Validation mAP50: {metrics.box.map50:.4f}")
    print(f"Validation mAP50-95: {metrics.box.map:.4f}")

    if args.export_onnx:
        exported = best_model.export(format="onnx", imgsz=args.imgsz, simplify=True, opset=17)
        print(f"Exported ONNX model to: {exported}")


if __name__ == "__main__":
    main()
