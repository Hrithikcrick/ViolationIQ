import cv2
import json
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


def clean_label(label):
    text = str(label).replace("_", " ").replace("-", " ").strip()
    low = text.lower().replace(" ", "")

    if low == "trafficlight":
        return "Traffic Light"

    if low == "speedlimit":
        return "Speed Limit Sign"

    if low == "crosswalk":
        return "Crosswalk Sign"

    if low == "stop":
        return "Stop Sign"

    return text.title()


def context_text(label):
    low = str(label).lower()

    if "stop" in low:
        return "Stop Sign", "Vehicle should stop before crossing the stop line."

    if "speed" in low:
        return "Speed Limit Sign", "Speed context is available, but speed enforcement needs calibrated tracking."

    if "crosswalk" in low:
        return "Crosswalk Sign", "Pedestrian crossing context is available for reviewer support."

    if "traffic light" in low:
        return "Traffic Light Context", "Signal context is available for reviewer support."

    return "Traffic Sign Context", "Traffic rule context is available for reviewer support."


def read_voc(xml_path):
    boxes = []

    if not xml_path.exists():
        return boxes

    tree = ET.parse(xml_path)
    root = tree.getroot()

    for obj in root.findall("object"):
        name = obj.findtext("name")
        bnd = obj.find("bndbox")

        if bnd is None:
            continue

        x1 = int(float(bnd.findtext("xmin", 0)))
        y1 = int(float(bnd.findtext("ymin", 0)))
        x2 = int(float(bnd.findtext("xmax", 0)))
        y2 = int(float(bnd.findtext("ymax", 0)))

        boxes.append({
            "label": clean_label(name),
            "box": [x1, y1, x2, y2],
            "source": "VOC annotation"
        })

    return boxes


def draw_panel(image, detections, image_name):
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
    cv2.putText(canvas, "ViolationIQ Signboard Context Module", (25, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.82, (255, 255, 255), 2)
    cv2.putText(canvas, "Real road sign image -> context evidence -> manual review", (25, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (220, 240, 255), 2)

    sx = left_w / w
    sy = canvas_h / h

    for i, d in enumerate(detections, 1):
        x1, y1, x2, y2 = d["box"]

        ax1 = int(x1 * sx)
        ay1 = int(y1 * sy)
        ax2 = int(x2 * sx)
        ay2 = int(y2 * sy)

        color = (0, 180, 255)

        cv2.rectangle(canvas, (ax1, ay1), (ax2, ay2), color, 4)

        label = f"S{i}: {d['label']}"
        cv2.rectangle(canvas, (ax1, max(86, ay1 - 34)), (min(left_w - 5, ax1 + 360), ay1), color, -1)
        cv2.putText(canvas, label[:30], (ax1 + 8, max(108, ay1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

    if detections:
        context, meaning = context_text(detections[0]["label"])
        status = "Detected"
    else:
        context = "Manual Review"
        meaning = "No strong signboard context found."
        status = "Manual Review"

    px = left_w + 25
    py = 125

    cv2.putText(canvas, "Context Summary", (px, py), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (20, 20, 20), 2)
    py += 45

    rows = [
        "Image: " + image_name,
        "Status: " + status,
        "Context: " + context,
        "Detections: " + str(len(detections))
    ]

    for row in rows:
        cv2.putText(canvas, row[:40], (px, py), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (45, 45, 45), 2)
        py += 31

    py += 10
    cv2.line(canvas, (px, py), (canvas_w - 25, py), (170, 170, 170), 2)
    py += 38

    cv2.putText(canvas, "Decision", (px, py), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 0, 0), 2)
    py += 38

    words = meaning.split()
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
    cv2.putText(canvas, "Safety: signboard context supports review; no automatic challan is generated.", (25, canvas_h - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (0, 100, 180), 2)

    return canvas, context, meaning, status


def process_signboard_showcase(input_dir="data/sample_images/signboard_showcase", out_dir="outputs/FINAL_SHOWCASE/signboard_context", model_path=None):
    input_dir = Path(input_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    images = []
    images += list(input_dir.glob("*.jpg"))
    images += list(input_dir.glob("*.jpeg"))
    images += list(input_dir.glob("*.png"))
    images = sorted(images)[:5]

    reports = []

    for i, path in enumerate(images, 1):
        image = cv2.imread(str(path))

        if image is None:
            continue

        xml_path = path.with_suffix(".xml")
        detections = read_voc(xml_path)

        panel, context, meaning, status = draw_panel(image, detections, path.name)

        out_img = out_dir / f"signboard_evidence_{i}.jpg"
        out_json = out_dir / f"signboard_report_{i}.json"

        cv2.imwrite(str(out_img), panel)

        report = {
            "module": "signboard_context",
            "input_image": str(path).replace("\\", "/"),
            "annotation": str(xml_path).replace("\\", "/"),
            "output_image": str(out_img).replace("\\", "/"),
            "status": status,
            "context": context,
            "meaning": meaning,
            "detections": detections,
            "safety": "Signboard context supports reviewer decision-making and does not trigger automatic challan."
        }

        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)

        reports.append(report)

    summary = {
        "module": "signboard_context",
        "images_processed": len(reports),
        "safety": "Signboard context supports review and is not used for automatic challan generation."
    }

    with open(out_dir / "signboard_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    print("Signboard outputs:", len(reports))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="data/sample_images/signboard_showcase")
    parser.add_argument("--out_dir", default="outputs/FINAL_SHOWCASE/signboard_context")
    parser.add_argument("--model", default=None)
    args = parser.parse_args()

    process_signboard_showcase(args.input_dir, args.out_dir, args.model)


if __name__ == "__main__":
    main()
