"""
BIU Traffic AI — Helmet Detection Model Trainer
================================================
Downloads a public helmet detection dataset from Roboflow and trains
a YOLOv8s model to correctly distinguish:
  - with_helmet  (green ✅)
  - without_helmet / no_helmet (red ❌)
  - motorcycle / bike

Usage:
    cd d:\biu-traffic-ai\backend
    ..\tools\train_helmet_model.py   OR
    ..\django\Scripts\python.exe ..\tools\train_helmet_model.py

The best trained model is automatically saved to:
    d:\biu-traffic-ai\backend\weights\best.pt
"""

import os
import sys
import shutil
import zipfile
import urllib.request
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
EPOCHS        = 50          # Increase to 100 for better accuracy (takes longer)
IMG_SIZE      = 416         # 416 is good balance of speed vs accuracy on CPU
BATCH_SIZE    = 8           # Reduce to 4 if you get memory errors
MODEL_BASE    = 'yolov8s.pt'  # yolov8s = faster training, yolov8m = better accuracy
OUTPUT_NAME   = 'biu_helmet_v2'
WEIGHTS_DIR   = Path(__file__).parent.parent / 'backend' / 'weights'

# ── Dataset options (pick one) ────────────────────────────────────────────────
# Option A: Roboflow public dataset (requires internet)
# Get your free API key at https://roboflow.com
ROBOFLOW_API_KEY     = os.getenv('ROBOFLOW_API_KEY', '')
ROBOFLOW_WORKSPACE   = 'roboflow-universe-projects'
ROBOFLOW_PROJECT     = 'hard-hat-universe-0dy7t'
ROBOFLOW_VERSION     = 1

# Option B: Local dataset (put your images + labels here)
LOCAL_DATASET_YAML   = Path(__file__).parent / 'dataset' / 'data.yaml'

# ─────────────────────────────────────────────────────────────────────────────

def check_dependencies():
    try:
        import ultralytics
        import torch
        print(f"✅ Ultralytics {ultralytics.__version__}")
        print(f"✅ PyTorch {torch.__version__}")
        print(f"🖥️  Device: {'CUDA GPU' if torch.cuda.is_available() else 'CPU'}")
        if not torch.cuda.is_available():
            print("⚠️  No GPU detected — training on CPU will take longer (est. 2-4 hours for 50 epochs)")
            print("   Tip: If you have an NVIDIA GPU, install CUDA for 10× faster training")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        sys.exit(1)


def download_roboflow_dataset():
    """Download helmet dataset from Roboflow."""
    if not ROBOFLOW_API_KEY:
        print("\n📋 To download from Roboflow:")
        print("   1. Go to https://roboflow.com and sign up (free)")
        print("   2. Get your API key from https://app.roboflow.com/settings/api")
        print("   3. Set it: set ROBOFLOW_API_KEY=your_key_here")
        print("   4. Run this script again\n")
        return None

    try:
        from roboflow import Roboflow
    except ImportError:
        import subprocess
        print("Installing roboflow...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'roboflow'], check=True)
        from roboflow import Roboflow

    print(f"\n📥 Downloading helmet dataset from Roboflow...")
    rf = Roboflow(api_key=ROBOFLOW_API_KEY)
    project = rf.workspace(ROBOFLOW_WORKSPACE).project(ROBOFLOW_PROJECT)
    dataset = project.version(ROBOFLOW_VERSION).download("yolov8")
    return Path(dataset.location) / 'data.yaml'


def download_public_dataset():
    """
    Download a free public helmet detection dataset (no API key needed).
    Uses the Safety Helmet Detection dataset from GitHub.
    """
    dataset_dir = Path(__file__).parent / 'helmet_dataset'
    yaml_path   = dataset_dir / 'data.yaml'

    if yaml_path.exists():
        print(f"✅ Dataset already exists at {dataset_dir}")
        return yaml_path

    dataset_dir.mkdir(parents=True, exist_ok=True)

    # Download from a public source
    url = "https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset/archive/refs/heads/master.zip"
    zip_path = dataset_dir / 'dataset.zip'

    print(f"\n📥 Downloading public safety helmet dataset...")
    print(f"   This may take a few minutes...")

    try:
        urllib.request.urlretrieve(url, zip_path, reporthook=progress_hook)
        print(f"\n✅ Downloaded. Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(dataset_dir)
        zip_path.unlink()
        print("✅ Extracted successfully")
        return prepare_dataset_yaml(dataset_dir)
    except Exception as e:
        print(f"❌ Download failed: {e}")
        print("\nManual option: Download a dataset from:")
        print("  https://universe.roboflow.com/search?q=helmet+motorcycle&t=metadata")
        print("  Choose 'YOLOv8' format and place data.yaml in tools/helmet_dataset/")
        return None


def progress_hook(block_num, block_size, total_size):
    downloaded = block_num * block_size
    if total_size > 0:
        pct = min(downloaded * 100 / total_size, 100)
        bar = '█' * int(pct / 2) + '░' * (50 - int(pct / 2))
        print(f"\r   [{bar}] {pct:.0f}%", end='', flush=True)


def prepare_dataset_yaml(dataset_dir: Path) -> Path:
    """Create a data.yaml for the dataset."""
    yaml_content = f"""# BIU Helmet Detection Dataset
path: {dataset_dir.as_posix()}
train: images/train
val:   images/val
test:  images/test

nc: 3
names:
  0: with_helmet
  1: without_helmet
  2: motorcycle
"""
    yaml_path = dataset_dir / 'data.yaml'
    yaml_path.write_text(yaml_content)
    return yaml_path


def train(dataset_yaml: Path):
    """Run YOLOv8 training."""
    from ultralytics import YOLO
    import torch

    device = '0' if torch.cuda.is_available() else 'cpu'
    print(f"\n🚀 Starting training on {device.upper()}")
    print(f"   Model:   {MODEL_BASE}")
    print(f"   Epochs:  {EPOCHS}")
    print(f"   ImgSize: {IMG_SIZE}")
    print(f"   Dataset: {dataset_yaml}\n")

    model = YOLO(MODEL_BASE)
    results = model.train(
        data=str(dataset_yaml),
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        batch=BATCH_SIZE,
        device=device,
        name=OUTPUT_NAME,
        patience=15,            # Stop early if no improvement for 15 epochs
        save=True,
        plots=True,
        workers=2,
        # Augmentation for better generalization
        augment=True,
        fliplr=0.5,
        degrees=10.0,
        translate=0.1,
        scale=0.5,
        shear=2.0,
        perspective=0.0,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
    )

    # Copy best weights to backend/weights/best.pt
    best_pt = Path('runs') / 'detect' / OUTPUT_NAME / 'weights' / 'best.pt'
    if best_pt.exists():
        WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
        dest = WEIGHTS_DIR / 'best.pt'
        backup = WEIGHTS_DIR / 'best_old.pt'
        if dest.exists():
            shutil.copy2(dest, backup)
            print(f"💾 Backed up old model → {backup}")
        shutil.copy2(best_pt, dest)
        print(f"\n✅ New model saved → {dest}")
        print(f"🎯 Restart the Django server to use the new model!")
    else:
        print(f"⚠️  Could not find best.pt at {best_pt}")

    return results


def main():
    print("=" * 60)
    print("  BIU Traffic AI — Helmet Model Trainer")
    print("=" * 60)

    check_dependencies()

    # Try to get dataset
    dataset_yaml = None

    if LOCAL_DATASET_YAML.exists():
        print(f"\n✅ Using local dataset: {LOCAL_DATASET_YAML}")
        dataset_yaml = LOCAL_DATASET_YAML

    elif ROBOFLOW_API_KEY:
        dataset_yaml = download_roboflow_dataset()

    else:
        dataset_yaml = download_public_dataset()

    if dataset_yaml is None or not Path(dataset_yaml).exists():
        print("\n❌ No dataset available. Please follow the instructions above.")
        print("\n💡 Quickest path:")
        print("   1. Visit: https://universe.roboflow.com/search?q=helmet+motorcycle")
        print("   2. Download any dataset in YOLOv8 format")
        print("   3. Place data.yaml + images/ + labels/ in d:\\biu-traffic-ai\\tools\\dataset\\")
        print("   4. Run this script again")
        sys.exit(1)

    train(Path(dataset_yaml))


if __name__ == '__main__':
    # Run from backend directory for correct model path resolution
    os.chdir(Path(__file__).parent.parent / 'backend')
    main()
