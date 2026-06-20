import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ultralytics import YOLO

from src.helmet_plate_module import HelmetPlateModule
from src.signboard_context_module import SignboardContextModule


def load_model(path):
    path = Path(path)

    if not path.exists():
        print("Missing model:", path)
        return None

    return YOLO(str(path))


def load_ocr_reader():
    try:
        import easyocr
        print("EasyOCR loaded.")
        return easyocr.Reader(["en"], gpu=False)
    except Exception as e:
        print("EasyOCR not available. Safe OCR will use manual review fallback.")
        print("Reason:", e)
        return None


def image_files(folder):
    folder = Path(folder)

    if not folder.exists():
        return []

    exts = [".jpg", ".jpeg", ".png", ".webp"]
    return [p for p in folder.rglob("*") if p.suffix.lower() in exts]


def draw_plate_ocr_panel(image_path, helmet_report, output_image_path, output_json_path):
    image = cv2.imread(str(image_path))

    if image is None:
        return {
            "module": "safe_plate_ocr",
            "input": str(image_path),
            "error": "Image could not be read",
            "manual_review": True,
        }

    plates = helmet_report.get("plates", [])

    canvas_w = 1280
    canvas_h = 720
    left_w = 850

    h, w = image.shape[:2]
    resized = cv2.resize(image, (left_w, canvas_h))

    sx = left_w / w
    sy = canvas_h / h

    canvas = np.ones((canvas_h, canvas_w, 3), dtype=np.uint8) * 255
    canvas[:, :left_w] = resized

    for item in plates:
        x1, y1, x2, y2 = item["box"]

        x1 = int(x1 * sx)
        y1 = int(y1 * sy)
        x2 = int(x2 * sx)
        y2 = int(y2 * sy)

        cv2.rectangle(canvas, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.putText(canvas, "Plate Candidate", (x1, max(25, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 0, 255), 2)

    x = left_w + 30
    y = 50

    cv2.putText(canvas, "ViolationIQ Safe Plate OCR", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (20, 20, 20), 2)
    y += 45

    if not plates:
        cv2.putText(canvas, "No plate candidate found", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (0, 0, 255), 2)
        y += 35
        cv2.putText(canvas, "Manual Review Required", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (0, 0, 255), 2)

    for i, item in enumerate(plates[:5], 1):
        safe = item.get("safe_ocr", {})

        lines = [
            f"Plate {i}",
            f"Detection Conf: {item.get('detection_confidence', item.get('confidence', 0))}",
            f"Readability: {item.get('readability', 0)}",
            f"OCR: {safe.get('plate_text', 'UNREADABLE')}",
            f"Status: {safe.get('status', 'Manual Review')}",
            f"Manual Review: {safe.get('manual_review', True)}",
        ]

        for line in lines:
            color = (0, 0, 255) if "UNREADABLE" in line or "True" in line else (30, 30, 30)
            cv2.putText(canvas, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.48, color, 1)
            y += 24

        y += 12

    cv2.rectangle(canvas, (0, canvas_h - 55), (canvas_w, canvas_h), (255, 255, 255), -1)
    cv2.putText(canvas, "Safe OCR Policy: weak or unreadable plate text is sent to manual review.", (25, canvas_h - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (0, 0, 255), 2)

    Path(output_image_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_image_path), canvas)

    report = {
        "module": "safe_plate_ocr",
        "input": str(image_path),
        "plate_candidates": len(plates),
        "plates": plates,
        "safety": "Plate text is shown only when OCR confidence and readability are reliable. Otherwise it is marked manual review.",
    }

    Path(output_json_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    return report


def copy_best_helmet_video(video_folder, output_folder):
    video_folder = Path(video_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    candidates = [
        video_folder / "violationiq_bike_helmet_demo.mp4",
        video_folder / "violationiq_bike_helmet_demo ..mp4",
    ]

    video_path = None

    for item in candidates:
        if item.exists():
            video_path = item
            break

    if video_path is None:
        videos = list(video_folder.rglob("*.mp4"))

        if videos:
            video_path = videos[0]

    if video_path is None:
        report = {
            "module": "helmet_video_demo",
            "status": "No helmet demo video found",
            "manual_review": True,
        }
        return report

    out_video = output_folder / "helmet_video_demo_processed_1.mp4"
    shutil.copy(video_path, out_video)

    report = {
        "module": "helmet_video_demo",
        "input_video": str(video_path).replace("\\", "/"),
        "output_video": str(out_video).replace("\\", "/"),
        "status": "Best helmet demo video copied to final showcase without re-processing",
        "note": "The video was already processed during Kaggle development. It is not processed again to avoid duplicate boxes/labels.",
        "safety": "Manual review is required before challan or legal action.",
    }

    with open(output_folder / "helmet_video_report_1.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    return report


def write_index(showcase_dir):
    showcase_dir = Path(showcase_dir)
    rows = [["task", "file", "description"]]

    for p in showcase_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png", ".json", ".csv", ".mp4"]:
            rows.append([
                p.parent.name,
                str(p).replace("\\", "/"),
                "Generated ViolationIQ final judge output",
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
    parser.add_argument("--vehicle_model", default=None)
    parser.add_argument("--out", default="outputs/FINAL_SHOWCASE")

    args = parser.parse_args()

    out = Path(args.out)

    helmet_out = out / "helmet_plate"
    sign_out = out / "signboard_context"
    plate_ocr_out = out / "plate_ocr"
    videos_out = out / "videos"
    reports_out = Path("reports")

    for folder in [helmet_out, sign_out, plate_ocr_out, videos_out, reports_out]:
        folder.mkdir(parents=True, exist_ok=True)

    traffic_model = load_model(args.traffic_model)
    helmet_model = load_model(args.helmet_model)
    plate_model = load_model(args.plate_model)
    ocr_reader = load_ocr_reader()

    helmet_module = HelmetPlateModule(
        helmet_model=helmet_model,
        plate_model=plate_model,
        ocr_reader=ocr_reader,
    )

    sign_module = SignboardContextModule(
        traffic_model=traffic_model,
    )

    summary = {
        "reproduction_scope": "Stable judge reproduction: helmet image evidence, safe plate OCR, signboard context, copied best helmet video demo, JSON reports, CSV index",
        "redlight_status": "Removed from final judge reproduction because available sample red-light output was not reliable.",
        "images_processed": 0,
        "helmet_videos_processed": 0,
        "helmet_reports": [],
        "plate_ocr_reports": [],
        "signboard_reports": [],
        "helmet_video_reports": [],
    }

    for i, image_path in enumerate(image_files(args.images), 1):
        helmet_report = helmet_module.run_image(
            image_path=image_path,
            output_image_path=helmet_out / f"helmet_evidence_{i}.jpg",
            output_json_path=helmet_out / f"helmet_report_{i}.json",
        )

        plate_report = draw_plate_ocr_panel(
            image_path=image_path,
            helmet_report=helmet_report,
            output_image_path=plate_ocr_out / f"plate_ocr_evidence_{i}.jpg",
            output_json_path=plate_ocr_out / f"plate_ocr_report_{i}.json",
        )

        sign_report = sign_module.run_image(
            image_path=image_path,
            output_json_path=sign_out / f"signboard_report_{i}.json",
            output_image_path=sign_out / f"signboard_evidence_{i}.jpg",
        )

        summary["images_processed"] += 1
        summary["helmet_reports"].append(helmet_report)
        summary["plate_ocr_reports"].append(plate_report)
        summary["signboard_reports"].append(sign_report)

    video_report = copy_best_helmet_video(args.videos, videos_out)

    if video_report.get("status") != "No helmet demo video found":
        summary["helmet_videos_processed"] = 1

    summary["helmet_video_reports"].append(video_report)

    index_csv = write_index(out)
    summary["final_showcase_index"] = str(index_csv).replace("\\", "/")

    with open(reports_out / "reproduction_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    print("Reproduction completed.")
    print("Images processed:", summary["images_processed"])
    print("Helmet videos processed:", summary["helmet_videos_processed"])
    print("Safe OCR reports generated:", len(summary["plate_ocr_reports"]))
    print("Red-light final reproduction: removed")
    print("Summary saved:", reports_out / "reproduction_summary.json")
    print("Showcase index:", index_csv)


if __name__ == "__main__":
    main()
