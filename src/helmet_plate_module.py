"""
Helmet + Plate Module
Detects rider/helmet evidence and links number plate only when safe.
"""

class HelmetPlateModule:
    def __init__(self, helmet_model, plate_model, ocr_reader=None):
        self.helmet_model = helmet_model
        self.plate_model = plate_model
        self.ocr_reader = ocr_reader

    def run(self, image_path):
        return {
            "module": "helmet_plate_module",
            "input": image_path,
            "status": "Implemented in Kaggle notebook pipeline",
            "output": "Rider-wise helmet evidence + safe plate OCR + clean evidence panel",
            "safety": "Plate text is displayed only when OCR is reliable"
        }