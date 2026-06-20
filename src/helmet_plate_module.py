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
