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
                "reason": "Video supports temporal review, vehicle motion, signal color, and stop-line reasoning.",
                "manual_review": False,
            }

        if kind == "image":
            return {
                "selected_module": "multi_expert_image_review",
                "reason": "Image can be checked by helmet/plate and signboard context modules.",
                "manual_review": False,
            }

        return {
            "selected_module": "manual_review",
            "reason": "Unsupported input type.",
            "manual_review": True,
        }

    def route_by_labels(self, labels):
        labels = [str(x).lower() for x in labels]

        helmet_keys = [
            "rider",
            "helmet",
            "facewithnohelmet",
            "facewithgoodhelmet",
            "facewithbadhelmet",
            "motorcycle",
            "motorbike",
            "numberplate",
            "number plate",
        ]

        sign_keys = [
            "red light",
            "green light",
            "yellow light",
            "stop",
            "speed limit",
            "no entry",
            "no stopping",
            "no left",
            "no right",
            "u-turn",
        ]

        modules = []

        for label in labels:
            for key in helmet_keys:
                if key in label:
                    if "helmet_plate_module" not in modules:
                        modules.append("helmet_plate_module")

        for label in labels:
            for key in sign_keys:
                if key in label:
                    if "signboard_context_module" not in modules:
                        modules.append("signboard_context_module")

        if not modules:
            modules.append("manual_review")

        return {
            "selected_modules": modules,
            "manual_review": "manual_review" in modules,
        }
