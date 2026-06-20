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
        r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$",
        r"^[0-9]{2}[A-Z]{1,3}[0-9]{3,4}$",
    ]

    for pattern in patterns:
        if re.match(pattern, text):
            return True

    return False


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
        quality += 10

    return {
        "quality": round(float(min(quality, 100)), 2),
        "blur": round(float(blur), 2),
        "brightness": round(float(brightness), 2),
        "contrast": round(float(contrast), 2),
    }


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

    if 55 <= brightness <= 200:
        score += 30
    else:
        score += 10

    return round(float(min(score, 100)), 2)


def safe_plate_output(text, ocr_confidence, readability):
    text = clean_plate_text(text)

    if text and ocr_confidence >= 0.45 and readability >= 45:
        return {
            "plate_text": text,
            "status": "Readable Candidate",
            "manual_review": not is_possible_indian_plate(text),
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


def box_center(box):
    x1, y1, x2, y2 = box
    return (x1 + x2) // 2, (y1 + y2) // 2


def point_inside_box(point, box):
    px, py = point
    x1, y1, x2, y2 = box

    return x1 <= px <= x2 and y1 <= py <= y2


def box_iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    iw = max(0, ix2 - ix1)
    ih = max(0, iy2 - iy1)

    inter = iw * ih

    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)

    union = area_a + area_b - inter

    if union == 0:
        return 0

    return inter / union


def nms_by_class(detections, iou_threshold=0.35):
    detections = sorted(
        detections,
        key=lambda x: x.get("confidence", 0),
        reverse=True,
    )

    final = []

    for det in detections:
        keep = True

        for old in final:
            same_class = det.get("class") == old.get("class")
            high_overlap = box_iou(det["box"], old["box"]) > iou_threshold

            if same_class and high_overlap:
                keep = False
                break

        if keep:
            final.append(det)

    return final
