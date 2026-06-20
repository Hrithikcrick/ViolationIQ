"""
ViolationIQ Signboard Context Module

This module detects traffic sign context and produces manual-review friendly
evidence. It does not overclaim violations that require speed, direction,
or duration tracking.
"""


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
            contexts.append("Speed-limit context detected; speed tracking is required")

        if any("no left" in x or "no right" in x or "u-turn" in x for x in labels):
            contexts.append("Turn-restriction context detected")

        if len(contexts) == 0:
            contexts.append("No strong traffic sign context detected")

        return contexts

    def run(self, image_path, image=None):
        detections = []

        if image is not None:
            detections = self.collect_detections(image)

        labels = [d["class"] for d in detections]
        contexts = self.context_from_labels(labels)

        return {
            "module": "signboard_context_module",
            "input": image_path,
            "detections": detections,
            "contexts": contexts,
            "safety": "Tracking-dependent violations are routed to manual review.",
        }
