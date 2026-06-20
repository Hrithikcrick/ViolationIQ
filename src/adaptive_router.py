"""
ViolationIQ Adaptive Router

This module routes an input image/video to the correct evidence expert:
- Helmet + Plate module
- Red-Light video module
- Signboard context module
- Manual review fallback
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
                "input_type": "video",
                "selected_module": "redlight_video_module",
                "reason": "Video input supports temporal voting, vehicle movement, and stop-line crossing evidence.",
                "manual_review": False,
            }

        if input_type == "image":
            return {
                "input_type": "image",
                "selected_module": "image_adaptive_module",
                "reason": "Image input can be analyzed for helmet, number plate, and signboard context.",
                "manual_review": False,
            }

        return {
            "input_type": "unknown",
            "selected_module": "manual_review",
            "reason": "Unsupported input type.",
            "manual_review": True,
        }

    def route_by_detected_objects(self, labels):
        labels = [str(x).lower() for x in labels]

        helmet_keywords = [
            "rider",
            "helmet",
            "motorcycle",
            "motorbike",
            "facewithnohelmet",
            "facewithgoodhelmet",
            "facewithbadhelmet",
        ]

        sign_keywords = [
            "no entry",
            "no stopping",
            "stop sign",
            "speed limit",
            "no left turn",
            "no right turn",
            "no u-turn",
            "red light",
            "green light",
        ]

        selected_modules = []

        if any(any(key in label for key in helmet_keywords) for label in labels):
            selected_modules.append("helmet_plate_module")

        if any(any(key in label for key in sign_keywords) for label in labels):
            selected_modules.append("signboard_context_module")

        if len(selected_modules) == 0:
            selected_modules.append("manual_review")

        return {
            "selected_modules": selected_modules,
            "manual_review": "manual_review" in selected_modules,
            "reason": "Routing based on detected object labels.",
        }

    def route(self, path, labels=None):
        base_route = self.route_by_input_type(path)

        if labels is None:
            return base_route

        object_route = self.route_by_detected_objects(labels)

        return {
            "input_route": base_route,
            "object_route": object_route,
        }
