import argparse
import csv
import json
import sys
from pathlib import Path

import cv2

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ultralytics import YOLO

from src.helmet_plate_module import HelmetPlateModule
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


def helmet_video_files(folder):
    folder = Path(folder)

    if not folder.exists():
        return []

    exts = [".mp4", ".avi", ".mov", ".mkv"]
    videos = [p for p in folder.rglob("*") if p.suffix.lower() in exts]

    preferred = []

    for p in videos:
        name = p.name.lower()

        if "helmet" in name or "bike" in name or "rider" in name:
            preferred.append(p)

    if preferred:
        return preferred[:1]

    return videos[:1]


def normal_label(label):
    label = str(label)
    low = label.lower().replace(" ", "").replace("_", "")

    if "nohelmet" in low:
        return "No Helmet"

    if "badhelmet" in low or "improperhelmet" in low:
        return "Improper Helmet"

    if "goodhelmet" in low or low == "helmet":
        return "Helmet OK"

    if "rider" in low or "person" in low:
        return "Rider"

    if "plate" in low:
        return "Number Plate"

    return label


def status_color(label):
    low = label.lower()

    if "no helmet" in low or "improper" in low:
        return (0, 0, 255)

    if "helmet ok" in low:
        return (0, 180, 0)

    if "plate" in low:
        return (255, 0, 255)

    return (0, 255, 255)


def process_helmet_video(video_path, helmet_model, out_video, out_json, max_frames=450):
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        report = {
            "module": "helmet_video_demo",
            "input_video": str(video_path),
            "error": "Video could not be opened",
            "manual_review": True,
        }

        Path(out_json).parent.mkdir(parents=True, exist_ok=True)

        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)

        return report

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 25

    width = 1280
    height = 720

    Path(out_video).parent.mkdir(parents=True, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_video), fourcc, fps, (width, height))

    frame_id = 0
    written = 0
    violation_frames = 0
    total_detections = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.resize(frame, (width, height))

        results = helmet_model.predict(
            source=frame,
            conf=0.18,
            imgsz=768,
            verbose=False,
        )

        frame_has_violation = False
        detections_this_frame = 0

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                if hasattr(helmet_model, "names"):
                    raw_label = helmet_model.names.get(cls_id, str(cls_id))
                else:
                    raw_label = str(cls_id)

                label = normal_label(raw_label)
                color = status_color(label)

                if label in ["No Helmet", "Improper Helmet"]:
                    frame_has_violation = True

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                x1 = max(0, int(x1))
                y1 = max(0, int(y1))
                x2 = min(width - 1, int(x2))
                y2 = min(height - 1, int(y2))

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

                text = f"{label} {conf:.2f}"
                cv2.rectangle(frame, (x1, max(0, y1 - 34)), (min(width - 1, x1 + 260), y1), color, -1)
                cv2.putText(frame, text, (x1 + 5, max(22, y1 - 9)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)

                detections_this_frame += 1

        total_detections += detections_this_frame

        if frame_has_violation:
            violation_frames += 1

        title = "ViolationIQ Helmet Video Evidence Demo"
        sub = f"Frame: {frame_id} | Detections: {detections_this_frame} | Manual review required before challan"

        cv2.rectangle(frame, (0, 0), (width, 70), (255, 255, 255), -1)
        cv2.putText(frame, title, (20, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(frame, sub, (20, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (20, 20, 20), 2)

        writer.write(frame)

        written += 1
        frame_id += 1

        if written >= max_frames:
            break

    cap.release()
    writer.release()

    report = {
        "module": "helmet_video_demo",
        "input_video": str(video_path),
        "output_video": str(out_video).replace("\\", "/"),
        "frames_written": written,
        "violation_candidate_frames": violation_frames,
        "total_detections": total_detections,
        "status": "Helmet video demo generated successfully",
        "safety": "This video is an evidence demo. Manual review is required before challan or legal action.",
    }

    Path(out_json).parent.mkdir(parents=True, exist_ok=True)

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    return report


def write_index(showcase_dir):
    showcase_dir = Path(showcase_dir)
    rows = [["task", "file", "description"]]

    for p in showcase_dir.rglob("*"):
        if p.is_file():
            if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".json", ".csv", ".mp4"]:
                rows.append([
                    p.parent.name,
                    str(p).replace("\\", "/"),
                    "Generated ViolationIQ stable judge output",
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
    out.mkdir(parents=True, exist_ok=True)

    helmet_out = out / "helmet_plate"
    sign_out = out / "signboard_context"
    videos_out = out / "videos"
    reports_out = Path("reports")

    helmet_out.mkdir(parents=True, exist_ok=True)
    sign_out.mkdir(parents=True, exist_ok=True)
    videos_out.mkdir(parents=True, exist_ok=True)
    reports_out.mkdir(parents=True, exist_ok=True)

    traffic_model = load_model(args.traffic_model)
    helmet_model = load_model(args.helmet_model)
    plate_model = load_model(args.plate_model)

    helmet_module = HelmetPlateModule(
        helmet_model=helmet_model,
        plate_model=plate_model,
    )

    sign_module = SignboardContextModule(
        traffic_model=traffic_model,
    )

    summary = {
        "reproduction_scope": "Stable judge reproduction: helmet/plate evidence, helmet video demo, signboard context, JSON reports, CSV index",
        "redlight_status": "Removed from final judge reproduction because the available sample red-light output was not reliable enough for final evaluation.",
        "images_processed": 0,
        "videos_processed": 0,
        "helmet_reports": [],
        "helmet_video_reports": [],
        "signboard_reports": [],
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

    if helmet_model is not None:
        for i, video_path in enumerate(helmet_video_files(args.videos), 1):
            video_report = process_helmet_video(
                video_path=video_path,
                helmet_model=helmet_model,
                out_video=videos_out / f"helmet_video_demo_processed_{i}.mp4",
                out_json=videos_out / f"helmet_video_report_{i}.json",
            )

            summary["videos_processed"] += 1
            summary["helmet_video_reports"].append(video_report)

    index_csv = write_index(out)
    summary["final_showcase_index"] = str(index_csv).replace("\\", "/")

    with open(reports_out / "reproduction_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    print("Reproduction completed.")
    print("Images processed:", summary["images_processed"])
    print("Helmet videos processed:", summary["videos_processed"])
    print("Red-light final reproduction: removed")
    print("Summary saved:", reports_out / "reproduction_summary.json")
    print("Showcase index:", index_csv)


if __name__ == "__main__":
    main()
