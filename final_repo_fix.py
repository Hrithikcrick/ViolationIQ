from pathlib import Path
import shutil
import csv
import subprocess
import sys

ROOT = Path(".")
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
DOCS = ROOT / "docs"
ARCH = ROOT / "architecture"
SHOWCASE = ROOT / "outputs" / "FINAL_SHOWCASE"
PLATE_OCR = SHOWCASE / "plate_ocr"

folders_to_make = [
    SRC,
    SCRIPTS,
    DOCS,
    ARCH,
    SHOWCASE,
    PLATE_OCR,
    SHOWCASE / "helmet_plate",
    SHOWCASE / "redlight",
    SHOWCASE / "signboard_context",
    SHOWCASE / "videos",
]

for p in folders_to_make:
    p.mkdir(parents=True, exist_ok=True)


def write_file(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")
    print("Wrote:", path)


for p in list(ROOT.rglob("*")):
    if p.is_file() and p.stat().st_size == 0:
        print("Removing empty file:", p)
        p.unlink()

for p in list(ROOT.rglob("__pycache__")) + list(ROOT.rglob(".ipynb_checkpoints")):
    if p.is_dir():
        print("Removing cache folder:", p)
        shutil.rmtree(p, ignore_errors=True)

for p in list(ROOT.rglob("*")):
    if p.is_file() and "speed" in p.name.lower():
        print("Removing speed file:", p)
        p.unlink()


write_file(SRC / "__init__.py", "")


write_file(SRC / "safety_utils.py", r'''
import re
import cv2
import numpy as np


def clean_plate_text(text):
    text = str(text).upper()
    text = re.sub(r"[^A-Z0-9]", "", text)
    return text


def is_possible_indian_plate(text):
    text = clean_plate_text(text)

    patterns = [
        r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$",
        r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$",
        r"^[0-9]{2}[A-Z]{1,3}[0-9]{3,4}$",
    ]

    return any(re.match(pattern, text) for pattern in patterns)


def image_quality_score(image):
    if image is None or image.size == 0:
        return {"quality": 0, "blur": 0, "brightness": 0, "contrast": 0}

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))

    quality = 0
    quality += min(blur / 150, 1) * 40
    quality += min(contrast / 70, 1) * 30

    if 50 <= brightness <= 200:
        quality += 30
    else:
        quality += 10

    return {
        "quality": round(float(min(quality, 100)), 2),
        "blur": round(float(blur), 2),
        "brightness": round(float(brightness), 2),
        "contrast": round(float(contrast), 2),
    }


def plate_readability_score(crop):
    if crop is None or crop.size == 0:
        return 0

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))

    score = 0
    score += min(blur / 120, 1) * 40
    score += min(contrast / 60, 1) * 30

    if 55 <= brightness <= 200:
        score += 30
    else:
        score += 10

    return round(float(min(score, 100)), 2)


def safe_plate_output(text, ocr_confidence, readability):
    text = clean_plate_text(text)

    if text and ocr_confidence >= 0.45 and readability >= 45:
        return {
            "plate_text": text,
            "status": "Readable Candidate",
            "manual_review": not is_possible_indian_plate(text),
            "ocr_confidence": round(float(ocr_confidence), 3),
            "readability": readability,
        }

    return {
        "plate_text": "UNREADABLE",
        "status": "Manual Review",
        "manual_review": True,
        "ocr_confidence": round(float(ocr_confidence), 3),
        "readability": readability,
    }


def box_center(box):
    x1, y1, x2, y2 = box
    return (x1 + x2) // 2, (y1 + y2) // 2


def point_inside_box(point, box):
    px, py = point
    x1, y1, x2, y2 = box
    return x1 <= px <= x2 and y1 <= py <= y2


def box_iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    iw = max(0, ix2 - ix1)
    ih = max(0, iy2 - iy1)

    inter = iw * ih

    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)

    union = area_a + area_b - inter

    if union == 0:
        return 0

    return inter / union


def nms_by_class(detections, iou_threshold=0.35):
    detections = sorted(detections, key=lambda x: x.get("confidence", 0), reverse=True)

    final = []

    for det in detections:
        keep = True

        for old in final:
            if det.get("class") == old.get("class") and box_iou(det["box"], old["box"]) > iou_threshold:
                keep = False
                break

        if keep:
            final.append(det)

    return final
''')


write_file(SRC / "adaptive_router.py", r'''
import os


class ViolationIQRouter:
    def __init__(self):
        self.image_exts = [".jpg", ".jpeg", ".png", ".webp"]
        self.video_exts = [".mp4", ".avi", ".mov", ".mkv"]

    def input_type(self, path):
        ext = os.path.splitext(str(path))[1].lower()

        if ext in self.image_exts:
            return "image"

        if ext in self.video_exts:
            return "video"

        return "unknown"

    def route_by_input(self, path):
        kind = self.input_type(path)

        if kind == "video":
            return {
                "selected_module": "redlight_module",
                "reason": "Video supports temporal review, vehicle motion, and red-light reasoning.",
                "manual_review": False,
            }

        if kind == "image":
            return {
                "selected_module": "multi_expert_image_review",
                "reason": "Image can be checked by helmet/plate and signboard modules.",
                "manual_review": False,
            }

        return {
            "selected_module": "manual_review",
            "reason": "Unsupported file type.",
            "manual_review": True,
        }

    def route_by_labels(self, labels):
        labels = [str(x).lower() for x in labels]

        modules = []

        helmet_keys = ["rider", "helmet", "motorcycle", "motorbike", "numberplate"]
        sign_keys = ["red light", "green light", "stop", "speed limit", "no entry", "no stopping", "u-turn"]

        if any(any(key in label for key in helmet_keys) for label in labels):
            modules.append("helmet_plate_module")

        if any(any(key in label for key in sign_keys) for label in labels):
            modules.append("signboard_context_module")

        if not modules:
            modules.append("manual_review")

        return {
            "selected_modules": modules,
            "manual_review": "manual_review" in modules,
        }
''')


write_file(SRC / "helmet_plate_module.py", r'''
import json
from pathlib import Path
import cv2
import numpy as np

try:
    from .safety_utils import image_quality_score, plate_readability_score, safe_plate_output
    from .safety_utils import point_inside_box, box_center, nms_by_class
except ImportError:
    from safety_utils import image_quality_score, plate_readability_score, safe_plate_output
    from safety_utils import point_inside_box, box_center, nms_by_class


class HelmetPlateModule:
    def __init__(self, helmet_model=None, plate_model=None):
        self.helmet_model = helmet_model
        self.plate_model = plate_model

        self.helmet_names = {
            0: "numberPlate",
            1: "faceWithNoHelmet",
            2: "faceWithGoodHelmet",
            3: "faceWithBadHelmet",
            4: "rider",
        }

    def collect_helmet_detections(self, image, conf=0.18, imgsz=768):
        if self.helmet_model is None:
            return []

        results = self.helmet_model.predict(
            source=image,
            conf=conf,
            imgsz=imgsz,
            verbose=False,
        )

        detections = []

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                score = float(box.conf[0])

                if hasattr(self.helmet_model, "names") and cls_id in self.helmet_model.names:
                    label = self.helmet_model.names[cls_id]
                else:
                    label = self.helmet_names.get(cls_id, str(cls_id))

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                detections.append({
                    "class": label,
                    "confidence": round(score, 3),
                    "box": [int(x1), int(y1), int(x2), int(y2)],
                })

        return nms_by_class(detections, iou_threshold=0.35)

    def associate_riders(self, detections):
        riders = [d for d in detections if d["class"] == "rider"]
        no_helmet = [d for d in detections if d["class"] == "faceWithNoHelmet"]
        good_helmet = [d for d in detections if d["class"] == "faceWithGoodHelmet"]
        bad_helmet = [d for d in detections if d["class"] == "faceWithBadHelmet"]

        rider_results = []

        for i, rider in enumerate(riders, 1):
            rbox = rider["box"]

            has_no = any(point_inside_box(box_center(face["box"]), rbox) for face in no_helmet)
            has_good = any(point_inside_box(box_center(face["box"]), rbox) for face in good_helmet)
            has_bad = any(point_inside_box(box_center(face["box"]), rbox) for face in bad_helmet)

            if has_no:
                status = "No Helmet"
                violation = True
            elif has_bad:
                status = "Improper Helmet"
                violation = True
            elif has_good:
                status = "Helmet OK"
                violation = False
            else:
                status = "Manual Review"
                violation = False

            rider_results.append({
                "rider_id": f"R{i}",
                "box": rbox,
                "status": status,
                "violation": violation,
                "confidence": rider["confidence"],
            })

        return rider_results

    def collect_plate_detections(self, image, conf=0.20, imgsz=768):
        if self.plate_model is None:
            return []

        results = self.plate_model.predict(
            source=image,
            conf=conf,
            imgsz=imgsz,
            verbose=False,
        )

        plates = []

        for result in results:
            for box in result.boxes:
                score = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                crop = image[max(0, y1):max(0, y2), max(0, x1):max(0, x2)]
                readability = plate_readability_score(crop)

                plates.append({
                    "box": [int(x1), int(y1), int(x2), int(y2)],
                    "confidence": round(score, 3),
                    "readability": readability,
                    "safe_ocr": safe_plate_output("", 0.0, readability),
                })

        return plates

    def build_report(self, image_path, image, riders, plates):
        return {
            "module": "helmet_plate_module",
            "input": image_path,
            "total_riders": len(riders),
            "helmet_ok": sum(1 for r in riders if r["status"] == "Helmet OK"),
            "violations": sum(1 for r in riders if r["violation"]),
            "manual_review": sum(1 for r in riders if r["status"] == "Manual Review"),
            "riders": riders,
            "plates": plates,
            "image_quality": image_quality_score(image),
            "safety": "Final challan should be approved only after manual review.",
        }

    def draw_evidence_panel(self, image, report, output_path):
        h, w = image.shape[:2]

        canvas_w = 1280
        canvas_h = 720
        img_w = 850

        resized = cv2.resize(image, (img_w, canvas_h))

        sx = img_w / w
        sy = canvas_h / h

        canvas = np.ones((canvas_h, canvas_w, 3), dtype=np.uint8) * 255
        canvas[:, :img_w] = resized

        for rider in report["riders"][:8]:
            x1, y1, x2, y2 = rider["box"]

            x1 = int(x1 * sx)
            y1 = int(y1 * sy)
            x2 = int(x2 * sx)
            y2 = int(y2 * sy)

            if rider["violation"]:
                color = (0, 0, 255)
            elif rider["status"] == "Helmet OK":
                color = (0, 180, 0)
            else:
                color = (0, 160, 200)

            cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 3)
            cv2.putText(
                canvas,
                rider["rider_id"] + " " + rider["status"],
                (x1, max(25, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                color,
                2,
            )

        x = img_w + 35
        y = 55

        cv2.putText(canvas, "ViolationIQ Evidence", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 20, 20), 2)

        y += 50

        lines = [
            "Helmet + Plate Module",
            f"Total Riders: {report['total_riders']}",
            f"Helmet OK: {report['helmet_ok']}",
            f"Violations: {report['violations']}",
            f"Manual Review: {report['manual_review']}",
        ]

        for line in lines:
            cv2.putText(canvas, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (40, 40, 40), 2)
            y += 36

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(output_path, canvas)

    def run_image(self, image_path, output_image_path=None, output_json_path=None):
        image = cv2.imread(image_path)

        if image is None:
            return {
                "module": "helmet_plate_module",
                "input": image_path,
                "error": "Image could not be read",
                "manual_review": True,
            }

        detections = self.collect_helmet_detections(image)
        riders = self.associate_riders(detections)
        plates = self.collect_plate_detections(image)

        report = self.build_report(image_path, image, riders, plates)

        if output_image_path:
            self.draw_evidence_panel(image, report, output_image_path)

        if output_json_path:
            Path(output_json_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=4)

        return report
''')


write_file(SRC / "redlight_module.py", r'''
import json
from pathlib import Path
import cv2
import numpy as np


class RedLightModule:
    def __init__(self, vehicle_model=None):
        self.vehicle_model = vehicle_model

    def detect_signal_color(self, frame):
        h, w = frame.shape[:2]

        x1 = int(w * 0.82)
        y1 = int(h * 0.02)
        x2 = int(w * 0.98)
        y2 = int(h * 0.34)

        roi = frame[y1:y2, x1:x2]

        if roi.size == 0:
            return "unknown", [x1, y1, x2, y2]

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        red1 = cv2.inRange(hsv, np.array([0, 80, 80]), np.array([10, 255, 255]))
        red2 = cv2.inRange(hsv, np.array([170, 80, 80]), np.array([180, 255, 255]))
        yellow = cv2.inRange(hsv, np.array([18, 80, 80]), np.array([36, 255, 255]))
        green = cv2.inRange(hsv, np.array([38, 60, 60]), np.array([95, 255, 255]))

        values = {
            "red": int(np.sum((red1 + red2) > 0)),
            "yellow": int(np.sum(yellow > 0)),
            "green": int(np.sum(green > 0)),
        }

        color = max(values, key=values.get)

        if values[color] < 50:
            color = "unknown"

        return color, [x1, y1, x2, y2]

    def detect_vehicles(self, frame, conf=0.20):
        if self.vehicle_model is None:
            return []

        results = self.vehicle_model.predict(source=frame, conf=conf, imgsz=960, verbose=False)

        vehicles = []
        allowed = ["car", "truck", "bus", "motorcycle", "motorbike"]

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                score = float(box.conf[0])
                label = self.vehicle_model.names[cls_id]

                if label not in allowed:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                vehicles.append({
                    "class": label,
                    "confidence": round(score, 3),
                    "box": [int(x1), int(y1), int(x2), int(y2)],
                })

        return vehicles

    def process_frame(self, frame, frame_id):
        frame = cv2.resize(frame, (1280, 720))

        h, w = frame.shape[:2]

        signal_color, signal_roi = self.detect_signal_color(frame)
        vehicles = self.detect_vehicles(frame)

        stop_line_y = int(h * 0.72)
        crossing = []

        for vehicle in vehicles:
            x1, y1, x2, y2 = vehicle["box"]

            if y2 >= stop_line_y:
                crossing.append(vehicle)

        violation = signal_color == "red" and len(crossing) > 0

        if violation:
            decision = "Possible Red-Light Violation"
            priority = "High"
        elif signal_color == "red":
            decision = "Red Signal - No clear crossing vehicle"
            priority = "Low"
        elif signal_color == "green":
            decision = "Green Signal - No Violation"
            priority = "Low"
        else:
            decision = "Manual Review"
            priority = "Medium"

        return {
            "frame_id": frame_id,
            "signal_color": signal_color,
            "signal_roi": signal_roi,
            "vehicle_count": len(vehicles),
            "crossing_vehicle_count": len(crossing),
            "stop_line_y": stop_line_y,
            "violation": violation,
            "decision": decision,
            "priority": priority,
            "vehicles": vehicles,
            "crossing_vehicles": crossing[:3],
        }

    def run_video(self, video_path, output_json_path=None, frame_step=3, max_frames=240):
        cap = cv2.VideoCapture(video_path)

        results = []
        frame_id = 0
        processed = 0

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            if frame_id % frame_step == 0:
                results.append(self.process_frame(frame, frame_id))

                processed += 1

                if processed >= max_frames:
                    break

            frame_id += 1

        cap.release()

        summary = {
            "module": "redlight_module",
            "input_video": video_path,
            "processed_frames": len(results),
            "violation_frames": sum(1 for r in results if r["violation"]),
            "final_status": "Manual review required before challan",
            "frames": results,
        }

        if output_json_path:
            Path(output_json_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=4)

        return summary
''')


write_file(SRC / "signboard_context_module.py", r'''
import json
from pathlib import Path
import cv2


class SignboardContextModule:
    def __init__(self, traffic_model=None):
        self.traffic_model = traffic_model

    def collect_detections(self, image, conf=0.20, imgsz=768):
        if self.traffic_model is None:
            return []

        results = self.traffic_model.predict(source=image, conf=conf, imgsz=imgsz, verbose=False)

        detections = []

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                score = float(box.conf[0])
                label = self.traffic_model.names[cls_id]

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                detections.append({
                    "class": label,
                    "confidence": round(score, 3),
                    "box": [int(x1), int(y1), int(x2), int(y2)],
                })

        return detections

    def context_from_labels(self, labels):
        labels = [str(x).lower() for x in labels]

        contexts = []

        if any("no entry" in x for x in labels):
            contexts.append("No-entry sign context detected")

        if any("no stopping" in x for x in labels):
            contexts.append("No-stopping sign context detected")

        if any("stop" in x for x in labels):
            contexts.append("Stop-sign compliance context detected")

        if any("speed limit" in x for x in labels):
            contexts.append("Speed-limit context detected; calibrated tracking needed")

        if any("u-turn" in x or "no left" in x or "no right" in x for x in labels):
            contexts.append("Turn-restriction context detected")

        if not contexts:
            contexts.append("No strong signboard context detected")

        return contexts

    def run_image(self, image_path, output_json_path=None):
        image = cv2.imread(image_path)

        if image is None:
            return {
                "module": "signboard_context_module",
                "input": image_path,
                "error": "Image could not be read",
                "manual_review": True,
            }

        detections = self.collect_detections(image)

        report = {
            "module": "signboard_context_module",
            "input": image_path,
            "detected_signs": len(detections),
            "detections": detections,
            "contexts": self.context_from_labels([d["class"] for d in detections]),
            "safety": "Signboard result gives context. Final challan needs manual review.",
        }

        if output_json_path:
            Path(output_json_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=4)

        return report
''')


write_file(SCRIPTS / "train_yolo.py", r'''
import argparse
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--model", default="yolo11s.pt")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--imgsz", type=int, default=768)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--name", default="violationiq_train")
    parser.add_argument("--project", default="runs")
    args = parser.parse_args()

    model = YOLO(args.model)

    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=args.project,
        name=args.name,
        cos_lr=True,
    )


if __name__ == "__main__":
    main()
''')


write_file(SCRIPTS / "run_helmet_image.py", r'''
import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ultralytics import YOLO
from src.helmet_plate_module import HelmetPlateModule


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--helmet_model", required=True)
    parser.add_argument("--plate_model", default=None)
    parser.add_argument("--out_image", default="outputs/FINAL_SHOWCASE/helmet_plate/evidence.jpg")
    parser.add_argument("--out_json", default="outputs/FINAL_SHOWCASE/helmet_plate/report.json")
    args = parser.parse_args()

    helmet_model = YOLO(args.helmet_model)
    plate_model = YOLO(args.plate_model) if args.plate_model else None

    module = HelmetPlateModule(
        helmet_model=helmet_model,
        plate_model=plate_model,
    )

    report = module.run_image(
        image_path=args.image,
        output_image_path=args.out_image,
        output_json_path=args.out_json,
    )

    print(report)


if __name__ == "__main__":
    main()
''')


write_file(SCRIPTS / "run_redlight_video.py", r'''
import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ultralytics import YOLO
from src.redlight_module import RedLightModule


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--vehicle_model", required=True)
    parser.add_argument("--out_json", default="outputs/FINAL_SHOWCASE/redlight/report.json")
    args = parser.parse_args()

    vehicle_model = YOLO(args.vehicle_model)

    module = RedLightModule(vehicle_model=vehicle_model)

    report = module.run_video(
        video_path=args.video,
        output_json_path=args.out_json,
    )

    print(report)


if __name__ == "__main__":
    main()
''')


write_file(DOCS / "TRAINING_AND_REPRODUCTION.md", r'''
# Training and Reproduction Notes

This repository contains clean source modules for the ViolationIQ submission.

## Training Commands

```bash
python scripts/train_yolo.py --data path/to/traffic_data.yaml --model yolo11s.pt --epochs 30 --imgsz 768 --name traffic_yolo11s
python scripts/train_yolo.py --data path/to/helmet_data.yaml --model yolo11s.pt --epochs 60 --imgsz 768 --name helmet_yolo11s
python scripts/train_yolo.py --data path/to/plate_data.yaml --model yolo11s.pt --epochs 30 --imgsz 768 --name plate_yolo11s
```

## Required Weights

- traffic_yolo11s_best.pt
- helmet_yolo11s_best.pt
- plate_yolo11s_best.pt

Large weights should not be pushed to GitHub.

## Final Outputs Covered

- helmet and rider evidence
- safe plate OCR/manual-review interface
- red-light video evidence JSON
- signboard context report
- final showcase index
''')


write_file(SRC / "README.md", r'''
# Source Code

This folder contains the reusable ViolationIQ modules.

| File | Role |
|---|---|
| adaptive_router.py | Routes image/video input to the correct module |
| helmet_plate_module.py | Rider-wise helmet evidence and plate crop safety |
| redlight_module.py | Red-light video evidence logic |
| signboard_context_module.py | Traffic sign context logic |
| safety_utils.py | OCR validation, quality checks, NMS helpers |

The code can produce outputs when trained YOLO weights are provided at runtime.
''')


write_file(ARCH / "architecture_mermaid.md", r'''
# ViolationIQ Architecture

```mermaid
flowchart TD
    A[Input Image or Video] --> B[Adaptive Router]
    B --> C[Helmet + Plate Module]
    B --> D[Red-Light Video Module]
    B --> E[Signboard Context Module]
    C --> F[Evidence Image + JSON]
    D --> G[Frame-wise Violation Report]
    E --> H[Context Report]
    F --> I[Manual Review Before Challan]
    G --> I
    H --> I
```
''')


index_path = SHOWCASE / "final_showcase_index.csv"

rows = [["task", "rank", "file", "description"]]

folders = [
    ("helmet_plate", SHOWCASE / "helmet_plate", "Helmet and rider evidence panel"),
    ("plate_ocr", SHOWCASE / "plate_ocr", "Safe plate OCR evidence snapshot"),
    ("redlight", SHOWCASE / "redlight", "Red-light evidence output"),
    ("signboard_context", SHOWCASE / "signboard_context", "Traffic sign context evidence"),
    ("videos", SHOWCASE / "videos", "Final demo video"),
]

for task, folder, desc in folders:
    if folder.exists():
        rank = 1

        for p in sorted(folder.iterdir()):
            if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png", ".mp4", ".avi", ".mov", ".mkv", ".json"]:
                rows.append([task, str(rank), p.as_posix(), desc])
                rank += 1

with index_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print("Updated:", index_path)


readme_path = ROOT / "README.md"

if readme_path.exists():
    text = readme_path.read_text(encoding="utf-8", errors="ignore")

    clean_lines = []

    for line in text.splitlines():
        low = line.lower()

        if "speed estimation" in low or "speed_estimation" in low or "speed-estimation" in low:
            continue

        clean_lines.append(line)

    text = "\n".join(clean_lines)
    text = text.replace("/kaggle/working/ViolationIQ/", "")

    if "Final Source Code Status" not in text:
        text += """

## Final Source Code Status

The repository now contains clean modules for adaptive routing, helmet/plate checking, red-light video review, signboard context, safety utilities, training commands, and final showcase indexing.

Plate text is shown only when confidence/readability is reliable. Weak OCR is routed to manual review.
"""

    readme_path.write_text(text.strip() + "\n", encoding="utf-8")
    print("README cleaned.")


print("\nChecking Python files...")

result = subprocess.run(
    [sys.executable, "-m", "compileall", "src", "scripts"],
    text=True,
)

print("Compile return code:", result.returncode)


print("\nFINAL CHECKLIST")

check_items = [
    SRC / "adaptive_router.py",
    SRC / "helmet_plate_module.py",
    SRC / "redlight_module.py",
    SRC / "signboard_context_module.py",
    SRC / "safety_utils.py",
    SCRIPTS / "train_yolo.py",
    SCRIPTS / "run_helmet_image.py",
    SCRIPTS / "run_redlight_video.py",
    DOCS / "TRAINING_AND_REPRODUCTION.md",
    ARCH / "architecture_mermaid.md",
    SHOWCASE / "final_showcase_index.csv",
]

for item in check_items:
    print(("OK   " if item.exists() else "MISS "), item)


remaining_speed = [p for p in ROOT.rglob("*") if p.is_file() and "speed" in p.name.lower()]

if remaining_speed:
    print("\nRemaining speed files:")

    for p in remaining_speed:
        print(p)
else:
    print("\nNo speed files found.")


print("\nDone. Now run git add/commit/push.")
