import cv2
import re
import json
import argparse
import numpy as np
from pathlib import Path
from ultralytics import YOLO

try:
    import easyocr
except Exception:
    easyocr = None


STATE_CODES = [
    "AP","AR","AS","BR","CG","CH","DD","DL","DN","GA","GJ","HR","HP","JH",
    "JK","KA","KL","LA","LD","MH","ML","MN","MP","MZ","NL","OD","PB","PY",
    "RJ","SK","TN","TR","TS","UK","UP","WB"
]

VALID_STATE_CODES = set(STATE_CODES)

COMMON_STATE_FIX = {
    "IN": "TN",
    "1N": "TN",
    "IM": "TN",
    "T1": "TN",
    "0D": "OD",
    "0L": "DL",
    "D1": "DL"
}


def clean_plate_text(text):
    text = str(text).upper()
    text = re.sub(r"[^A-Z0-9]", "", text)
    return text


def edit_distance_one(a, b):
    if len(a) != len(b):
        return False

    diff = 0

    for x, y in zip(a, b):
        if x != y:
            diff += 1

    return diff == 1


def fix_state_code(text):
    text = clean_plate_text(text)

    if len(text) < 2:
        return text

    state = text[:2]

    if state in VALID_STATE_CODES:
        return text

    if state in COMMON_STATE_FIX:
        return COMMON_STATE_FIX[state] + text[2:]

    possible = []

    for code in STATE_CODES:
        if edit_distance_one(state, code):
            possible.append(code)

    if len(possible) == 1:
        return possible[0] + text[2:]

    return text


def is_possible_indian_plate(text):
    text = clean_plate_text(text)

    if len(text) < 7 or len(text) > 12:
        return False

    state = text[:2]

    if state not in VALID_STATE_CODES:
        return False

    patterns = [
        r"^[A-Z]{2}[0-9]{2}[A-Z]{1,3}[0-9]{4}$",
        r"^[A-Z]{2}[0-9]{1}[A-Z]{1,3}[0-9]{4}$"
    ]

    for pattern in patterns:
        if re.match(pattern, text):
            return True

    return False


def generate_plate_candidates(text):
    text = clean_plate_text(text)

    candidates = []
    seen = set()

    def add(value):
        value = clean_plate_text(value)

        if value and value not in seen:
            seen.add(value)
            candidates.append(value)

    add(text)
    add(fix_state_code(text))

    t = fix_state_code(text)

    if re.match(r"^[A-Z]{2}[0-9]{3}[A-Z][0-9]{4}$", t):
        add(t[:4] + t[5:])

    if re.match(r"^[A-Z]{2}[0-9]{2}[0-9][A-Z][0-9]{4}$", t):
        add(t[:4] + t[5:])

    if re.match(r"^[A-Z]{2}[0-9]{2}[A-Z][0-9]{5}$", t):
        add(t[:-5] + t[-4:])

    return candidates


def enhance_plate_crop(crop):
    if crop is None or crop.size == 0:
        return None

    h, w = crop.shape[:2]
    crop = cv2.resize(crop, (w * 5, h * 5), interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharp = cv2.filter2D(gray, -1, kernel)

    return sharp


def plate_readability_score(crop):
    if crop is None or crop.size == 0:
        return 0

    if len(crop.shape) == 3:
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    else:
        gray = crop

    h, w = gray.shape[:2]
    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    contrast = np.std(gray)

    size_score = min(100, (h * w) / 500)
    blur_score = min(100, blur / 10)
    contrast_score = min(100, contrast * 3)

    score = 0.4 * size_score + 0.35 * blur_score + 0.25 * contrast_score

    return round(max(0, min(100, score)), 2)


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

    area_a = max(1, (ax2 - ax1) * (ay2 - ay1))
    area_b = max(1, (bx2 - bx1) * (by2 - by1))
    union = area_a + area_b - inter

    return inter / union


def remove_duplicate_boxes(boxes):
    boxes = sorted(boxes, key=lambda x: x["confidence"], reverse=True)
    keep = []

    for b in boxes:
        ok = True

        for k in keep:
            if box_iou(b["box"], k["box"]) > 0.35:
                ok = False
                break

        if ok:
            keep.append(b)

    return keep


def run_easyocr_on_variants(crop, reader):
    if reader is None:
        return {
            "ocr_status": "Skipped",
            "reason": "EasyOCR not available",
            "plate_text": None,
            "ocr_confidence": 0
        }

    if crop is None or crop.size == 0:
        return {
            "ocr_status": "Failed",
            "reason": "Empty crop",
            "plate_text": None,
            "ocr_confidence": 0
        }

    variants = []
    enhanced = enhance_plate_crop(crop)

    if enhanced is not None:
        variants.append(("enhanced", enhanced))
        _, th1 = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variants.append(("threshold", th1))
        variants.append(("inverted", cv2.bitwise_not(th1)))

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=4.0, fy=4.0, interpolation=cv2.INTER_CUBIC)
    variants.append(("gray", gray))

    candidates = []

    for name, image in variants:
        try:
            results = reader.readtext(image, allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        except Exception:
            results = []

        joined = ""

        for item in results:
            joined += clean_plate_text(item[1])

        if len(joined) >= 4:
            avg_conf = sum(float(x[2]) for x in results) / len(results) if results else 0

            for c in generate_plate_candidates(joined):
                candidates.append((c, avg_conf, name))

        for item in results:
            raw = clean_plate_text(item[1])
            conf = float(item[2])

            if len(raw) >= 4:
                for c in generate_plate_candidates(raw):
                    candidates.append((c, conf, name))

    if not candidates:
        return {
            "ocr_status": "Failed",
            "reason": "OCR could not read useful plate text",
            "plate_text": None,
            "ocr_confidence": 0
        }

    candidates = sorted(
        candidates,
        key=lambda x: (is_possible_indian_plate(x[0]), x[1], len(x[0])),
        reverse=True
    )

    best_text, best_conf, variant = candidates[0]

    if best_conf < 0.25:
        return {
            "ocr_status": "Unreliable",
            "reason": "OCR confidence is low",
            "plate_text": best_text,
            "ocr_confidence": round(best_conf, 3),
            "variant": variant
        }

    if is_possible_indian_plate(best_text):
        return {
            "ocr_status": "Reliable",
            "reason": "Plate text passed OCR confidence, post-processing, and Indian plate format validation",
            "plate_text": best_text,
            "ocr_confidence": round(best_conf, 3),
            "variant": variant
        }

    return {
        "ocr_status": "Needs Manual Review",
        "reason": "OCR text detected but does not fully match Indian plate format",
        "plate_text": best_text,
        "ocr_confidence": round(best_conf, 3),
        "variant": variant
    }


def collect_plate_candidates(image, model):
    h, w = image.shape[:2]
    img_area = h * w

    results = model.predict(source=image, conf=0.25, imgsz=768, verbose=False)
    boxes = []

    for r in results:
        for b in r.boxes:
            conf = float(b.conf[0])
            x1, y1, x2, y2 = b.xyxy[0].cpu().numpy().astype(int)

            x1 = max(0, min(w - 1, int(x1)))
            y1 = max(0, min(h - 1, int(y1)))
            x2 = max(0, min(w - 1, int(x2)))
            y2 = max(0, min(h - 1, int(y2)))

            bw = x2 - x1
            bh = y2 - y1

            if bw <= 0 or bh <= 0:
                continue

            area_ratio = (bw * bh) / img_area
            aspect = bw / max(1, bh)

            if area_ratio < 0.003:
                continue

            if aspect < 1.2 or aspect > 8.5:
                continue

            boxes.append({
                "box": [x1, y1, x2, y2],
                "confidence": round(conf, 3),
                "area_ratio": round(area_ratio, 4),
                "aspect": round(aspect, 2)
            })

    boxes = remove_duplicate_boxes(boxes)
    boxes = sorted(boxes, key=lambda x: (x["confidence"], x["area_ratio"]), reverse=True)

    return boxes


def crop_with_padding(image, box):
    h, w = image.shape[:2]
    x1, y1, x2, y2 = box

    pad_x = int((x2 - x1) * 0.35)
    pad_y = int((y2 - y1) * 0.45)

    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(w, x2 + pad_x)
    y2 = min(h, y2 + pad_y)

    crop = image[y1:y2, x1:x2]

    return crop, [x1, y1, x2, y2]


def draw_panel(image, report, image_name):
    canvas_w = 1280
    canvas_h = 720
    left_w = 850
    right_w = canvas_w - left_w

    h, w = image.shape[:2]
    image2 = cv2.resize(image, (left_w, canvas_h))

    canvas = cv2.copyMakeBorder(
        image2,
        0,
        0,
        0,
        right_w,
        cv2.BORDER_CONSTANT,
        value=(245, 245, 245)
    )

    cv2.rectangle(canvas, (0, 0), (canvas_w, 82), (18, 24, 38), -1)
    cv2.putText(canvas, "ViolationIQ Safe Plate OCR Module", (25, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
    cv2.putText(canvas, "Plate detection -> enhancement -> readability -> OCR validation", (25, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (220, 240, 255), 2)

    sx = left_w / w
    sy = canvas_h / h

    if report["plate_detected"]:
        x1, y1, x2, y2 = report["padded_box"]
        ax1 = int(x1 * sx)
        ay1 = int(y1 * sy)
        ax2 = int(x2 * sx)
        ay2 = int(y2 * sy)

        status = report["ocr_result"]["ocr_status"]

        if status == "Reliable":
            color = (0, 180, 0)
        else:
            color = (0, 180, 255)

        cv2.rectangle(canvas, (ax1, ay1), (ax2, ay2), color, 4)

        text = report["ocr_result"].get("plate_text")

        if text is None:
            text = status

        if status == "Reliable":
            label = "PLATE: " + str(text)
        else:
            label = "OCR CANDIDATE: " + str(text)

        cv2.rectangle(canvas, (ax1, max(86, ay1 - 34)), (min(left_w - 5, ax1 + 430), ay1), color, -1)
        cv2.putText(canvas, label, (ax1 + 8, max(108, ay1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (0, 0, 0), 2)

    px = left_w + 25
    py = 125

    cv2.putText(canvas, "OCR Summary", (px, py), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (20, 20, 20), 2)
    py += 45

    rows = [
        "Image: " + image_name,
        "Plate detected: " + str(report["plate_detected"]),
        "Readability: " + str(report["readability_score"]),
        "OCR status: " + report["ocr_result"]["ocr_status"],
        "OCR text: " + str(report["ocr_result"].get("plate_text")),
        "OCR conf: " + str(report["ocr_result"].get("ocr_confidence"))
    ]

    for row in rows:
        cv2.putText(canvas, row[:40], (px, py), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (45, 45, 45), 2)
        py += 31

    py += 10
    cv2.line(canvas, (px, py), (canvas_w - 25, py), (170, 170, 170), 2)
    py += 38

    cv2.putText(canvas, "Decision", (px, py), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 0, 0), 2)
    py += 38

    reason = report["ocr_result"]["reason"]
    words = reason.split()
    line = ""

    for word in words:
        if len(line + " " + word) < 35:
            line += " " + word
        else:
            cv2.putText(canvas, line.strip(), (px, py), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 80, 180), 1)
            py += 27
            line = word

    if line:
        cv2.putText(canvas, line.strip(), (px, py), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 80, 180), 1)

    cv2.rectangle(canvas, (0, canvas_h - 58), (canvas_w, canvas_h), (255, 255, 255), -1)

    if report["ocr_result"]["ocr_status"] == "Reliable":
        bottom = "Safety: OCR candidate is readable, but reviewer verification is still required."
        bottom_color = (0, 130, 0)
    else:
        bottom = "Safety: OCR is not forced. Weak or doubtful plate evidence goes to manual review."
        bottom_color = (0, 80, 220)

    cv2.putText(canvas, bottom, (25, canvas_h - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.58, bottom_color, 2)

    return canvas


def process_ocr_samples(input_dir, model_path=None, out_dir="outputs/FINAL_SHOWCASE/plate_ocr", plate_model_path=None, max_images=5):
    input_dir = Path(input_dir)
    out_dir = Path(out_dir)
    model_path = model_path or plate_model_path or "weights/large_plate_yolo11s_best.pt"

    out_dir.mkdir(parents=True, exist_ok=True)
    crop_dir = out_dir / "enhanced_plate_crops"
    crop_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(str(model_path))

    reader = None

    if easyocr is not None:
        try:
            reader = easyocr.Reader(["en"], gpu=False)
        except Exception:
            reader = None

    images = []
    images += list(input_dir.glob("*.jpg"))
    images += list(input_dir.glob("*.jpeg"))
    images += list(input_dir.glob("*.png"))
    images = sorted(images)[:max_images]

    all_reports = []

    for idx, path in enumerate(images, 1):
        image = cv2.imread(str(path))

        if image is None:
            continue

        candidates = collect_plate_candidates(image, model)

        if not candidates:
            report = {
                "module": "safe_plate_ocr",
                "input_image": str(path).replace("\\", "/"),
                "plate_detected": False,
                "readability_score": 0,
                "ocr_result": {
                    "ocr_status": "Skipped",
                    "reason": "No strong plate candidate detected",
                    "plate_text": None,
                    "ocr_confidence": 0
                },
                "safety": "OCR text is not forced. Weak OCR is sent to manual review."
            }
        else:
            best = candidates[0]
            crop, padded_box = crop_with_padding(image, best["box"])
            enhanced = enhance_plate_crop(crop)
            score = plate_readability_score(enhanced)

            raw_crop_path = crop_dir / f"raw_plate_{idx}.jpg"
            enhanced_crop_path = crop_dir / f"enhanced_plate_{idx}.jpg"

            cv2.imwrite(str(raw_crop_path), crop)

            if enhanced is not None:
                cv2.imwrite(str(enhanced_crop_path), enhanced)

            if score < 45:
                ocr_result = {
                    "ocr_status": "Skipped",
                    "reason": "Plate crop quality is not sufficient for reliable OCR",
                    "plate_text": None,
                    "ocr_confidence": 0
                }
            else:
                ocr_result = run_easyocr_on_variants(crop, reader)

            report = {
                "module": "safe_plate_ocr",
                "input_image": str(path).replace("\\", "/"),
                "plate_detected": True,
                "selected_box": best["box"],
                "padded_box": padded_box,
                "detection_confidence": best["confidence"],
                "readability_score": score,
                "raw_crop_path": str(raw_crop_path).replace("\\", "/"),
                "enhanced_crop_path": str(enhanced_crop_path).replace("\\", "/"),
                "ocr_result": ocr_result,
                "safety": "OCR text is not forced. Weak OCR is sent to manual review."
            }

        panel = draw_panel(image, report, path.name)

        out_image = out_dir / f"plate_ocr_evidence_{idx}.jpg"
        out_json = out_dir / f"plate_ocr_report_{idx}.json"

        cv2.imwrite(str(out_image), panel)

        report["output_image"] = str(out_image).replace("\\", "/")

        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)

        all_reports.append(report)

        print("Created:", out_image)
        print("Created:", out_json)

    summary = {
        "module": "safe_plate_ocr",
        "images_processed": len(all_reports),
        "reliable_plates": [
            r["ocr_result"]["plate_text"]
            for r in all_reports
            if r["ocr_result"]["ocr_status"] == "Reliable"
        ],
        "manual_review_count": sum(
            1 for r in all_reports
            if r["ocr_result"]["ocr_status"] != "Reliable"
        ),
        "safety": "Unreadable plates and weak OCR are marked for manual review."
    }

    with open(out_dir / "plate_ocr_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    print("Done. OCR samples processed:", len(all_reports))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="data/sample_images/ocr_showcase")
    parser.add_argument("--model", default="weights/large_plate_yolo11s_best.pt")
    parser.add_argument("--plate_model", default=None)
    parser.add_argument("--out_dir", default="outputs/FINAL_SHOWCASE/plate_ocr")
    args = parser.parse_args()

    model_path = args.plate_model if args.plate_model else args.model

    process_ocr_samples(
        input_dir=args.input_dir,
        model_path=model_path,
        out_dir=args.out_dir
    )


if __name__ == "__main__":
    main()
