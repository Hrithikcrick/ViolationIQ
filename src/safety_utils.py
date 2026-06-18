"""Safety utilities for ViolationIQ."""

import cv2
import re
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
        r"^[A-Z]{2}[0-9]{2}[A-Z]{1}[0-9]{4}$"
    ]
    return any(re.match(p, text) for p in patterns)

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
    if should_display_plate(text, ocr_confidence, readability):
        return text, "Reliable"
    return "UNREADABLE", "Manual Review"