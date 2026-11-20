"""Run local YOLO inference on an image, folder, video, or webcam."""

from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--source", required=True, help="Image, folder, video path, RTSP URL, or camera index.")
    parser.add_argument("--output", type=Path, default=Path("runs/local-test"))
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--track", action="store_true")
    args = parser.parse_args()

    source: int | str = int(args.source) if args.source.isdigit() else args.source
    model = YOLO(str(args.weights))
    infer = model.track if args.track else model.predict
    options = {
        "source": source,
        "conf": args.conf,
        "imgsz": args.imgsz,
        "save": True,
        "project": str(args.output.parent),
        "name": args.output.name,
        "exist_ok": True,
    }
    if args.track:
        options.update(persist=True, tracker="bytetrack.yaml")
    results = infer(**options)
    print(f"Saved results to {args.output.resolve()}")
    print(f"Processed {len(results)} result(s).")


if __name__ == "__main__":
    main()
