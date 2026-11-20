"""
Script to upload the trained Cambodian Traffic YOLOv8 model to Hugging Face Hub.
Usage:
    python tools/upload_to_huggingface.py <YOUR_HF_TOKEN>
"""
import sys
import os
from pathlib import Path

def upload_model(hf_token=None):
    try:
        from huggingface_hub import HfApi, create_repo
    except ImportError:
        print("[!] Installing huggingface_hub...")
        os.system(f"{sys.executable} -m pip install huggingface_hub")
        from huggingface_hub import HfApi, create_repo

    token = hf_token or os.getenv("HF_TOKEN")
    if not token:
        print("[X] Error: HF_TOKEN is required. Pass it as an argument or set $env:HF_TOKEN.")
        print("    Get your token at: https://huggingface.co/settings/tokens (Role: Write)")
        return

    repo_id = "it-roth/cambodia-traffic-yolov8"
    print(f"[*] Creating/Accessing repository: {repo_id}...")
    create_repo(repo_id=repo_id, token=token, repo_type="model", exist_ok=True)

    api = HfApi()

    # 1. Upload Model Weights
    weights_path = Path("backend/weights/best.pt")
    if weights_path.is_file():
        print(f"[*] Uploading weights ({weights_path.stat().st_size / 1e6:.2f} MB)...")
        api.upload_file(
            path_or_fileobj=str(weights_path),
            path_in_repo="best.pt",
            repo_id=repo_id,
            repo_type="model",
            token=token,
            commit_message="Add custom trained YOLOv8 weights (best.pt - 99.5% mAP50)",
        )
        print("[OK] Weights uploaded successfully!")
    else:
        print(f"[X] Weights not found at {weights_path}")

    # 2. Upload Model Card README.md
    readme_path = Path("tools/huggingface_model_card.md")
    if readme_path.is_file():
        print("[*] Uploading model card README.md...")
        api.upload_file(
            path_or_fileobj=str(readme_path),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="model",
            token=token,
            commit_message="Add professional model card documentation and benchmark metrics",
        )
        print("[OK] Model card README uploaded successfully!")

    print(f"\n[DONE] View your public model at: https://huggingface.co/{repo_id}")

if __name__ == "__main__":
    token_arg = sys.argv[1] if len(sys.argv) > 1 else None
    upload_model(token_arg)
