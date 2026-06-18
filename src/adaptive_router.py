"""
ViolationIQ Adaptive Router
Routes input to the correct expert module.
"""

import os

class ViolationIQRouter:
    def __init__(self):
        self.video_exts = [".mp4", ".avi", ".mov", ".mkv"]
        self.image_exts = [".jpg", ".jpeg", ".png", ".webp"]

    def get_input_type(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext in self.video_exts:
            return "video"
        if ext in self.image_exts:
            return "image"
        return "unknown"

    def route_by_input_type(self, path):
        input_type = self.get_input_type(path)
        if input_type == "video":
            return {
                "selected_module": "redlight_video_module",
                "reason": "Video input supports temporal voting and red-light crossing analysis",
                "manual_review": False
            }
        if input_type == "image":
            return {
                "selected_module": "image_adaptive_module",
                "reason": "Image input can be analyzed for helmet, plate, and signboard context",
                "manual_review": False
            }
        return {
            "selected_module": "manual_review",
            "reason": "Unsupported input type",
            "manual_review": True
        }

    def route_by_detected_objects(self, labels):
        labels = [str(x).lower() for x in labels]

        helmet_keywords = ["rider", "helmet", "motorcycle", "facewithnohelmet", "facewithgoodhelmet", "facewithbadhelmet"]
        sign_keywords = ["no entry", "no stopping", "stop sign", "speed limit", "no left turn", "no right turn", "no u-turn", "red light", "green light"]

        selected = []

        if any(x in labels for x in helmet_keywords):
            selected.append("helmet_plate_module")

        if any(any(k in x for k in sign_keywords) for x in labels):
            selected.append("signboard_context_module")

        if len(selected) == 0:
            selected.append("manual_review")

        return {
            "selected_modules": selected,
            "manual_review": "manual_review" in selected,
            "reason": "Routing based on detected object labels"
        }