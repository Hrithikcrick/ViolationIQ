import argparse
import csv
import json
from pathlib import Path

from scripts.process_helmet_video_demo import process_video
from scripts.process_ocr_samples import process_ocr_samples


def make_index(showcase_dir):
    showcase_dir = Path(showcase_dir)
    index_path = showcase_dir / "final_showcase_index.csv"

    rows = []

    for path in sorted(showcase_dir.rglob("*")):
        if path.is_file():
            rel = str(path).replace("\\", "/")
            if "redlight" in rel.lower():
                continue

            task = path.parent.name

            rows.append({
                "task": task,
                "file": rel,
                "description": "ViolationIQ final judge output"
            })

    with open(index_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["task", "file", "description"])
        writer.writeheader()
        writer.writerows(rows)

    return index_path


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--traffic_model", default="weights/traffic_yolo11s_best.pt")
    parser.add_argument("--helmet_model", default="weights/helmet_yolo11s_best.pt")
    parser.add_argument("--plate_model", default="weights/large_plate_yolo11s_best.pt")
    parser.add_argument("--vehicle_model", default="weights/yolo26n.pt")

    parser.add_argument("--ocr_input", default="data/sample_images/ocr_showcase")
    parser.add_argument("--video_input", default="data/sample_videos/violationiq_bike_helmet_demo.mp4")

    args = parser.parse_args()

    showcase_dir = Path("outputs/FINAL_SHOWCASE")
    video_dir = showcase_dir / "videos"
    ocr_dir = showcase_dir / "plate_ocr"
    reports_dir = Path("reports")

    video_dir.mkdir(parents=True, exist_ok=True)
    ocr_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    if Path(args.video_input).exists():
        process_video(
            video_path=args.video_input,
            model_path=args.helmet_model,
            out_video=video_dir / "helmet_video_demo_processed_1.mp4",
            out_json=video_dir / "helmet_video_report_1.json"
        )

        helmet_videos_processed = 1
    else:
        helmet_videos_processed = 0

    if Path(args.ocr_input).exists():
        process_ocr_samples(
            input_dir=args.ocr_input,
            model_path=args.plate_model,
            out_dir=ocr_dir
        )

    safe_ocr_reports_generated = len(list(ocr_dir.glob("plate_ocr_report_*.json")))

    index_path = make_index(showcase_dir)

    summary = {
        "project": "ViolationIQ",
        "status": "Final judge reproduction ready",
        "helmet_videos_processed": helmet_videos_processed,
        "safe_ocr_reports_generated": safe_ocr_reports_generated,
        "helmet_video": "outputs/FINAL_SHOWCASE/videos/helmet_video_demo_processed_1.mp4",
        "safe_ocr_output": "outputs/FINAL_SHOWCASE/plate_ocr",
        "final_showcase_index": str(index_path).replace("\\", "/"),
        "safety_note": "ViolationIQ is an AI evidence copilot. Manual review is required before challan or legal action."
    }

    summary_path = reports_dir / "reproduction_summary.json"

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    print("Reproduction completed.")
    print("Helmet videos processed:", helmet_videos_processed)
    print("Safe OCR reports generated:", safe_ocr_reports_generated)
    print("Summary saved:", summary_path)
    print("Showcase index:", index_path)


if __name__ == "__main__":
    main()
