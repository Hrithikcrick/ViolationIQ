import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.process_helmet_video_demo import process_video
from scripts.process_ocr_samples import process_ocr_samples
from scripts.process_signboard_showcase import process_signboard_showcase
from scripts.build_helmet_showcase import build_helmet_showcase_from_frames


def clean_old_outputs():
    old_paths = [
        "outputs/final_best",
        "outputs/redlight",
        "outputs/video",
        "outputs/speed_estimation_demo",
        "outputs/contact_sheets",
        "outputs/FINAL_SHOWCASE/redlight"
    ]

    for p in old_paths:
        path = Path(p)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)


def make_index(showcase_dir):
    showcase_dir = Path(showcase_dir)
    index_path = showcase_dir / "final_showcase_index.csv"

    rows = []

    for path in sorted(showcase_dir.rglob("*")):
        if path.is_file():
            rel = str(path).replace("\\", "/")

            if "redlight" in rel.lower():
                continue

            rows.append({
                "task": path.parent.name,
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
    parser.add_argument("--signboard_input", default="data/sample_images/signboard_showcase")
    parser.add_argument("--video_input", default="data/sample_videos/violationiq_bike_helmet_demo.mp4")

    args = parser.parse_args()

    clean_old_outputs()

    shutil.rmtree("outputs/FINAL_SHOWCASE", ignore_errors=True)
    shutil.rmtree("outputs/helmet_plate", ignore_errors=True)

    showcase_dir = Path("outputs/FINAL_SHOWCASE")
    video_dir = showcase_dir / "videos"
    ocr_dir = showcase_dir / "plate_ocr"
    signboard_dir = showcase_dir / "signboard_context"
    reports_dir = Path("reports")

    video_dir.mkdir(parents=True, exist_ok=True)
    ocr_dir.mkdir(parents=True, exist_ok=True)
    signboard_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    helmet_videos_processed = 0
    helmet_image_outputs = 0

    if Path(args.video_input).exists():
        process_video(
            video_path=args.video_input,
            model_path=args.helmet_model,
            out_video=video_dir / "helmet_video_demo_processed_1.mp4",
            out_json=video_dir / "helmet_video_report_1.json"
        )
        helmet_videos_processed = 1
        helmet_image_outputs = build_helmet_showcase_from_frames()

    if Path(args.ocr_input).exists():
        process_ocr_samples(
            input_dir=args.ocr_input,
            model_path=args.plate_model,
            out_dir=ocr_dir
        )

    if Path(args.signboard_input).exists():
        process_signboard_showcase(
            input_dir=args.signboard_input,
            out_dir=signboard_dir
        )

    clean_old_outputs()

    safe_ocr_reports_generated = len(list(ocr_dir.glob("plate_ocr_report_*.json")))
    signboard_outputs = len(list(signboard_dir.glob("signboard_evidence_*.jpg")))

    index_path = make_index(showcase_dir)

    summary = {
        "project": "ViolationIQ",
        "status": "Final judge reproduction ready",
        "helmet_videos_processed": helmet_videos_processed,
        "helmet_image_outputs": helmet_image_outputs,
        "safe_ocr_reports_generated": safe_ocr_reports_generated,
        "signboard_context_outputs": signboard_outputs,
        "helmet_video": "outputs/FINAL_SHOWCASE/videos/helmet_video_demo_processed_1.mp4",
        "helmet_output": "outputs/FINAL_SHOWCASE/helmet_plate",
        "safe_ocr_output": "outputs/FINAL_SHOWCASE/plate_ocr",
        "signboard_output": "outputs/FINAL_SHOWCASE/signboard_context",
        "final_showcase_index": str(index_path).replace("\\", "/"),
        "safety_note": "ViolationIQ is an AI evidence copilot. Manual review is required before challan or legal action."
    }

    summary_path = reports_dir / "reproduction_summary.json"

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    helmet_count_final = len(list((showcase_dir / "helmet_plate").glob("helmet_evidence_*.jpg")))
    signboard_count_final = len(list((showcase_dir / "signboard_context").glob("signboard_evidence_*.jpg")))
    ocr_count_final = len(list((showcase_dir / "plate_ocr").glob("plate_ocr_report_*.json")))

    print("Reproduction completed.")
    print("Helmet evidence images generated:", helmet_count_final)
    print("Signboard context images generated:", signboard_count_final)
    print("Safe OCR reports generated:", ocr_count_final)
    print("Helmet videos processed:", helmet_videos_processed)
    print("Summary saved:", summary_path)
    print("Showcase index:", index_path)


if __name__ == "__main__":
    main()
