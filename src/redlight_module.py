"""
ViolationIQ Red-Light Video Module

This module detects traffic signal color, vehicle crossing over a virtual
stop-line, and uses temporal voting before final evidence recommendation.
"""

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
        red = red1 + red2

        yellow = cv2.inRange(hsv, np.array([18, 80, 80]), np.array([36, 255, 255]))
        green = cv2.inRange(hsv, np.array([38, 60, 60]), np.array([95, 255, 255]))

        values = {
            "red": int(np.sum(red > 0)),
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

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                score = float(box.conf[0])
                label = self.vehicle_model.names[cls_id]

                if label not in ["car", "truck", "bus", "motorcycle", "motorbike"]:
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
            "violation": violation,
            "decision": decision,
            "priority": priority,
            "safety": "Temporal review required before final challan.",
        }

    def run(self, video_path, frame_step=3, max_frames=240):
        cap = cv2.VideoCapture(video_path)

        results = []
        frame_id = 0
        processed = 0

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            if frame_id % frame_step == 0:
                result = self.process_frame(frame, frame_id)
                results.append(result)
                processed += 1

                if processed >= max_frames:
                    break

            frame_id += 1

        cap.release()

        violation_frames = sum(1 for r in results if r["violation"])

        if violation_frames >= 2:
            final_status = "Confirmed Red-Light Violation Candidate"
            confidence = "High"
        elif violation_frames == 1:
            final_status = "Single-frame Evidence - Manual Review"
            confidence = "Medium"
        else:
            final_status = "No confirmed red-light violation in processed clip"
            confidence = "Low"

        return {
            "module": "redlight_video_module",
            "input": video_path,
            "processed_frames": len(results),
            "violation_frames": violation_frames,
            "final_status": final_status,
            "temporal_confidence": confidence,
            "frames": results,
        }
