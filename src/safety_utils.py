"""
ViolationIQ Safety Utilities

Safety-first helper functions:
- plate text cleaning
- OCR confidence validation
- readability scoring
- evidence quality scoring
- manual-review fallback
"""

import re
import cv2
import numpy as np


def clean_plate_text(text):
    text = str(text).upper()
    text = re.sub(r"[^A-Z0-9]", "", text)
    return text


def is_possible_indian_plate(text):
    text = clean_plate_text(text)

    patterns = [
        r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$",
        r"^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$",
        r"^[A-Z]{2}[0-9]{2}[A-Z]{1}[0-9]{4}$",
    ]

    return any(re.match(pattern, text) for pattern in patterns)


def plate_readability_score(crop):
    if crop is None or crop.size == 0:
        return 0

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    brightness = np.mean(gray)
    contrast = np.std(gray)

    score = 0
    score += min(blur / 120, 1) * 40
    score += min(contrast / 60, 1) * 30

    if 60 <= brightness <= 190:
        score += 30
    else:
        score += 15

    return round(score, 2)


def should_display_plate(text, ocr_confidence, readability):
    valid = is_possible_indian_plate(text)

    if valid and ocr_confidence >= 0.45 and readability >= 45:
        return True

    return False


def safe_plate_output(text, ocr_confidence, readability):
    text = clean_plate_text(text)

    if should_display_plate(text, ocr_confidence, readability):
        return {
            "plate_text": text,
            "status": "Reliable",
            "manual_review": False,
            "ocr_confidence": round(float(ocr_confidence), 3),
            "readability": readability,
        }

    return {
        "plate_text": "UNREADABLE",
        "status": "Manual Review",
        "manual_review": True,
        "ocr_confidence": round(float(ocr_confidence), 3),
        "readability": readability,
    }


def image_quality_score(image):
    if image is None or image.size == 0:
        return {
            "quality": 0,
            "blur": 0,
            "brightness": 0,
            "contrast": 0,
        }

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    brightness = np.mean(gray)
    contrast = np.std(gray)

    quality = 0
    quality += min(blur / 150, 1) * 40
    quality += min(contrast / 70, 1) * 30

    if 50 <= brightness <= 200:
        quality += 30
    else:
        quality += 15

    return {
        "quality": round(float(quality), 2),
        "blur": round(float(blur), 2),
        "brightness": round(float(brightness), 2),
        "contrast": round(float(contrast), 2),
    }


def manual_review_reason(reason):
    return {
        "decision": "Manual Review",
        "reason": reason,
        "safe_for_auto_challan": False,
    }
