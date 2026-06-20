import json
from pathlib import Path

import cv2
import numpy as np


class RedLightModule:
    def __init__(self, vehicle_model=None):
        self.vehicle_model = vehicle_model

    def detect_signal_color(self, frame):
        h, w = frame.shape[:2]

        x1 = int(w * 0.78)
        y1 = int(h * 0.02)
        x2 = int(w * 0.99)
        y2 = int(h * 0.38)

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

        results = self.vehicle_model.predict(
            source=frame,
            conf=conf,
            imgsz=960,
            verbose=False,
        )

        vehicles = []
        allowed = ["car", "truck", "bus", "motorcycle", "motorbike", "auto", "vehicle"]

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                score = float(box.conf[0])
                label = str(self.vehicle_model.names[cls_id])

                if label.lower() not in allowed:
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

    def draw_frame_evidence(self, frame, result, output_path):
        frame = cv2.resize(frame, (1280, 720))

        x1, y1, x2, y2 = result["signal_roi"]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 3)

        stop_y = result["stop_line_y"]
        cv2.line(frame, (0, stop_y), (1280, stop_y), (0, 255, 255), 3)

        for vehicle in result["crossing_vehicles"]:
            bx1, by1, bx2, by2 = vehicle["box"]
            cv2.rectangle(frame, (bx1, by1), (bx2, by2), (0, 0, 255), 3)

        title = f"{result['decision']} | Signal: {result['signal_color']} | Priority: {result['priority']}"
        cv2.rectangle(frame, (0, 0), (1280, 45), (255, 255, 255), -1)
        cv2.putText(frame, title, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), frame)

    def run_video(self, video_path, output_json_path=None, evidence_dir=None, frame_step=3, max_frames=240):
        cap = cv2.VideoCapture(str(video_path))

        results = []
        frame_id = 0
        processed = 0
        saved = 0

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            if frame_id % frame_step == 0:
                result = self.process_frame(frame, frame_id)
                results.append(result)

                if evidence_dir and result["violation"] and saved < 5:
                    out = Path(evidence_dir) / f"redlight_violation_frame_{frame_id}.jpg"
                    self.draw_frame_evidence(frame, result, out)
                    saved += 1

                processed += 1

                if processed >= max_frames:
                    break

            frame_id += 1

        cap.release()

        summary = {
            "module": "redlight_module",
            "input_video": str(video_path),
            "processed_frames": len(results),
            "violation_frames": sum(1 for r in results if r["violation"]),
            "final_status": "Manual review required before final challan",
            "frames": results,
        }

        if output_json_path:
            Path(output_json_path).parent.mkdir(parents=True, exist_ok=True)

            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=4)

        return summary
