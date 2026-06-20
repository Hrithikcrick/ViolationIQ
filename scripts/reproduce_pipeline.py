import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ultralytics import YOLO

from src.helmet_plate_module import HelmetPlateModule
from src.redlight_module import RedLightModule
from src.signboard_context_module import SignboardContextModule


def load_model(path):
    if path is None:
        return None

    path = Path(path)

    if not path.exists():
        print("Missing model:", path)
        return None

    return YOLO(str(path))


def image_files(folder):
    folder = Path(folder)

    if not folder.exists():
        return []

    exts = [".jpg", ".jpeg", ".png", ".webp"]

    return [p for p in folder.rglob("*") if p.suffix.lower() in exts]


def video_files(folder):
    folder = Path(folder)

    if not folder.exists():
        return []

    exts = [".mp4", ".avi", ".mov", ".mkv"]

    return [p for p in folder.rglob("*") if p.suffix.lower() in exts]


def write_index(showcase_dir):
    showcase_dir = Path(showcase_dir)
    rows = [["task", "file", "description"]]

    for p in showcase_dir.rglob("*"):
        if p.is_file():
            if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".json", ".csv", ".mp4"]:
                rows.append([
                    p.parent.name,
                    str(p).replace("\\", "/"),
                    "Generated ViolationIQ reproduction output",
                ])

    out_csv = showcase_dir / "final_showcase_index.csv"

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return out_csv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", default="data/sample_images")
    parser.add_argument("--videos", default="data/sample_videos")
    parser.add_argument("--traffic_model", default="weights/traffic_yolo11s_best.pt")
    parser.add_argument("--helmet_model", default="weights/helmet_yolo11s_best.pt")
    parser.add_argument("--plate_model", default="weights/large_plate_yolo11s_best.pt")
    parser.add_argument("--vehicle_model", default="weights/yolo11s.pt")
    parser.add_argument("--out", default="outputs/FINAL_SHOWCASE")

    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    helmet_out = out / "helmet_plate"
    sign_out = out / "signboard_context"
    red_out = out / "redlight"
    reports_out = Path("reports")

    helmet_out.mkdir(parents=True, exist_ok=True)
    sign_out.mkdir(parents=True, exist_ok=True)
    red_out.mkdir(parents=True, exist_ok=True)
    reports_out.mkdir(parents=True, exist_ok=True)

    traffic_model = load_model(args.traffic_model)
    helmet_model = load_model(args.helmet_model)
    plate_model = load_model(args.plate_model)
    vehicle_model = load_model(args.vehicle_model)

    helmet_module = HelmetPlateModule(
        helmet_model=helmet_model,
        plate_model=plate_model,
    )

    sign_module = SignboardContextModule(
        traffic_model=traffic_model,
    )

    red_module = RedLightModule(
        vehicle_model=vehicle_model,
    )

    summary = {
        "images_processed": 0,
        "videos_processed": 0,
        "helmet_reports": [],
        "signboard_reports": [],
        "redlight_reports": [],
    }

    for i, image_path in enumerate(image_files(args.images), 1):
        helmet_report = helmet_module.run_image(
            image_path=image_path,
            output_image_path=helmet_out / f"helmet_evidence_{i}.jpg",
            output_json_path=helmet_out / f"helmet_report_{i}.json",
        )

        sign_report = sign_module.run_image(
            image_path=image_path,
            output_json_path=sign_out / f"signboard_report_{i}.json",
            output_image_path=sign_out / f"signboard_evidence_{i}.jpg",
        )

        summary["images_processed"] += 1
        summary["helmet_reports"].append(helmet_report)
        summary["signboard_reports"].append(sign_report)

    for i, video_path in enumerate(video_files(args.videos), 1):
        red_report = red_module.run_video(
            video_path=video_path,
            output_json_path=red_out / f"redlight_report_{i}.json",
            evidence_dir=red_out,
        )

        summary["videos_processed"] += 1
        summary["redlight_reports"].append(red_report)

    index_csv = write_index(out)
    summary["final_showcase_index"] = str(index_csv).replace("\\", "/")

    with open(reports_out / "reproduction_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    print("Reproduction completed.")
    print("Images processed:", summary["images_processed"])
    print("Videos processed:", summary["videos_processed"])
    print("Summary saved:", reports_out / "reproduction_summary.json")
    print("Showcase index:", index_csv)


if __name__ == "__main__":
    main()
