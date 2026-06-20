"""
ViolationIQ Helmet + Plate Module

This module performs rider-wise helmet evidence generation and connects
number plate OCR only when the plate evidence is reliable.
"""

import cv2

from safety_utils import plate_readability_score, safe_plate_output, image_quality_score


class HelmetPlateModule:
    def __init__(self, helmet_model=None, plate_model=None, ocr_reader=None):
        self.helmet_model = helmet_model
        self.plate_model = plate_model
        self.ocr_reader = ocr_reader

        self.helmet_names = {
            0: "numberPlate",
            1: "faceWithNoHelmet",
            2: "faceWithGoodHelmet",
            3: "faceWithBadHelmet",
            4: "rider",
        }

    def _center_inside(self, inner_box, outer_box):
        ix1, iy1, ix2, iy2 = inner_box
        ox1, oy1, ox2, oy2 = outer_box

        cx = (ix1 + ix2) // 2
        cy = (iy1 + iy2) // 2

        return ox1 <= cx <= ox2 and oy1 <= cy <= oy2

    def collect_detections(self, image, conf=0.18, imgsz=768):
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
                label = self.helmet_names.get(cls_id, str(cls_id))

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                detections.append({
                    "class": label,
                    "confidence": round(score, 3),
                    "box": [int(x1), int(y1), int(x2), int(y2)],
                })

        return detections

    def associate_riders(self, detections):
        riders = [d for d in detections if d["class"] == "rider"]
        no_helmet_faces = [d for d in detections if d["class"] == "faceWithNoHelmet"]
        good_helmet_faces = [d for d in detections if d["class"] == "faceWithGoodHelmet"]
        bad_helmet_faces = [d for d in detections if d["class"] == "faceWithBadHelmet"]

        rider_results = []

        for i, rider in enumerate(riders, 1):
            rbox = rider["box"]

            has_no_helmet = any(self._center_inside(face["box"], rbox) for face in no_helmet_faces)
            has_good_helmet = any(self._center_inside(face["box"], rbox) for face in good_helmet_faces)
            has_bad_helmet = any(self._center_inside(face["box"], rbox) for face in bad_helmet_faces)

            if has_no_helmet:
                status = "No Helmet"
                violation = True
            elif has_bad_helmet:
                status = "Improper Helmet"
                violation = True
            elif has_good_helmet:
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

    def run(self, image_path):
        image = cv2.imread(image_path)

        if image is None:
            return {
                "module": "helmet_plate_module",
                "input": image_path,
                "error": "Image could not be read",
                "manual_review": True,
            }

        detections = self.collect_detections(image)
        riders = self.associate_riders(detections)

        total_riders = len(riders)
        helmet_ok = sum(1 for r in riders if r["status"] == "Helmet OK")
        violations = sum(1 for r in riders if r["violation"])
        manual_review = sum(1 for r in riders if r["status"] == "Manual Review")

        return {
            "module": "helmet_plate_module",
            "input": image_path,
            "total_riders": total_riders,
            "helmet_ok": helmet_ok,
            "violations": violations,
            "manual_review": manual_review,
            "riders": riders,
            "image_quality": image_quality_score(image),
            "safety": "Plate text is displayed only when OCR is reliable.",
        }
