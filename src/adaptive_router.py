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
