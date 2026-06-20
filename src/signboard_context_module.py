import json
from pathlib import Path

import cv2


class SignboardContextModule:
    def __init__(self, traffic_model=None):
        self.traffic_model = traffic_model

    def collect_detections(self, image, conf=0.20, imgsz=768):
        if self.traffic_model is None:
            return []

        results = self.traffic_model.predict(
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
                label = str(self.traffic_model.names[cls_id])

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
            contexts.append("Speed-limit context detected; calibrated speed tracking needed")

        if any("red light" in x for x in labels):
            contexts.append("Traffic-light context detected")

        if any("u-turn" in x or "no left" in x or "no right" in x for x in labels):
            contexts.append("Turn-restriction context detected")

        if not contexts:
            contexts.append("No strong signboard context detected")

        return contexts

    def draw_evidence(self, image, detections, contexts, output_path):
        canvas = image.copy()

        for det in detections:
            x1, y1, x2, y2 = det["box"]

            cv2.rectangle(canvas, (x1, y1), (x2, y2), (255, 0, 0), 3)

            label = f"{det['class']} {det['confidence']}"
            cv2.putText(
                canvas,
                label,
                (x1, max(25, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 0, 0),
                2,
            )

        y = 35

        for context in contexts[:4]:
            cv2.putText(
                canvas,
                context,
                (20, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )
            y += 35

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), canvas)

    def run_image(self, image_path, output_json_path=None, output_image_path=None):
        image = cv2.imread(str(image_path))

        if image is None:
            return {
                "module": "signboard_context_module",
                "input": str(image_path),
                "error": "Image could not be read",
                "manual_review": True,
            }

        detections = self.collect_detections(image)
        labels = [d["class"] for d in detections]
        contexts = self.context_from_labels(labels)

        report = {
            "module": "signboard_context_module",
            "input": str(image_path),
            "detected_signs": len(detections),
            "detections": detections,
            "contexts": contexts,
            "safety": "Image gives sign context. Final challan may need tracking, duration, calibration, or manual review.",
        }

        if output_image_path:
            self.draw_evidence(image, detections, contexts, output_image_path)

        if output_json_path:
            Path(output_json_path).parent.mkdir(parents=True, exist_ok=True)

            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=4)

        return report
