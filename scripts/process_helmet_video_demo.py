import cv2
import json
import shutil
import argparse
import numpy as np
from pathlib import Path
from ultralytics import YOLO


helmet_names = {
    0: "numberPlate",
    1: "faceWithNoHelmet",
    2: "faceWithGoodHelmet",
    3: "faceWithBadHelmet",
    4: "rider"
}


def point_inside_box(point, box):
    px, py = point
    x1, y1, x2, y2 = box
    return x1 <= px <= x2 and y1 <= py <= y2


def collect_helmet_dets_clean(frame, helmet_model):
    results = helmet_model.predict(
        source=frame,
        conf=0.16,
        imgsz=768,
        verbose=False
    )

    dets = []
    h, w = frame.shape[:2]
    img_area = h * w

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = helmet_names.get(cls_id, str(cls_id))

            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

            bw = x2 - x1
            bh = y2 - y1
            area_ratio = (bw * bh) / img_area

            if label == "rider" and area_ratio < 0.002:
                continue

            if label != "rider" and area_ratio < 0.0001:
                continue

            dets.append({
                "class": label,
                "confidence": round(conf, 3),
                "box": [int(x1), int(y1), int(x2), int(y2)]
            })

    return dets


def analyze_rider_status_clean(dets):
    riders = [d for d in dets if d["class"] == "rider"]
    no_faces = [d for d in dets if d["class"] == "faceWithNoHelmet"]
    good_faces = [d for d in dets if d["class"] == "faceWithGoodHelmet"]
    bad_faces = [d for d in dets if d["class"] == "faceWithBadHelmet"]

    rider_info = []

    for i, r in enumerate(riders, 1):
        rbox = r["box"]

        no_count = 0
        good_count = 0
        bad_count = 0

        for f in no_faces:
            x1, y1, x2, y2 = f["box"]
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            if point_inside_box((cx, cy), rbox):
                no_count += 1

        for f in good_faces:
            x1, y1, x2, y2 = f["box"]
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            if point_inside_box((cx, cy), rbox):
                good_count += 1

        for f in bad_faces:
            x1, y1, x2, y2 = f["box"]
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            if point_inside_box((cx, cy), rbox):
                bad_count += 1

        if no_count > 0:
            status = "No Helmet"
            color = (0, 0, 255)
            violation = True

        elif bad_count > 0:
            status = "Improper Helmet"
            color = (0, 165, 255)
            violation = True

        elif good_count > 0:
            status = "Helmet OK"
            color = (0, 255, 0)
            violation = False

        else:
            status = "Manual Review"
            color = (0, 255, 255)
            violation = False

        rider_info.append({
            "id": f"R{i}",
            "box": rbox,
            "status": status,
            "color": color,
            "confidence": r["confidence"],
            "violation": violation
        })

    rider_info = sorted(
        rider_info,
        key=lambda x: (x["violation"], x["confidence"]),
        reverse=True
    )

    return rider_info[:5]


def make_display_frame(frame):
    canvas_h = 720
    video_w = 860
    panel_w = 420
    canvas_w = video_w + panel_w

    h, w = frame.shape[:2]

    bg = cv2.resize(frame, (video_w, canvas_h))
    bg = cv2.GaussianBlur(bg, (35, 35), 0)
    bg = cv2.addWeighted(bg, 0.45, np.zeros_like(bg), 0.55, 0)

    scale = min(video_w / w, canvas_h / h)
    new_w = int(w * scale)
    new_h = int(h * scale)

    fg = cv2.resize(frame, (new_w, new_h))

    xoff = (video_w - new_w) // 2
    yoff = (canvas_h - new_h) // 2

    canvas = np.ones((canvas_h, canvas_w, 3), dtype=np.uint8) * 245
    canvas[:, :video_w] = bg
    canvas[yoff:yoff + new_h, xoff:xoff + new_w] = fg

    return canvas, scale, xoff, yoff, video_w, canvas_w, canvas_h


def draw_final_helmet_layout(frame, rider_info, frame_id):
    canvas, scale, xoff, yoff, video_w, canvas_w, canvas_h = make_display_frame(frame)

    cv2.rectangle(canvas, (0, 0), (canvas_w, 86), (18, 24, 38), -1)

    total_riders = len(rider_info)
    no_helmet = sum(1 for r in rider_info if r["status"] == "No Helmet")
    helmet_ok = sum(1 for r in rider_info if r["status"] == "Helmet OK")
    improper = sum(1 for r in rider_info if r["status"] == "Improper Helmet")
    manual_review = sum(1 for r in rider_info if r["status"] == "Manual Review")
    violations = no_helmet + improper

    cv2.putText(
        canvas,
        "ViolationIQ Helmet Evidence Module",
        (28, 34),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.85,
        (255, 255, 255),
        2
    )

    info = f"Frame {frame_id} | Riders: {total_riders} | Helmet OK: {helmet_ok} | No Helmet: {no_helmet} | Manual Review: {manual_review}"

    cv2.putText(
        canvas,
        info,
        (28, 64),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.54,
        (220, 240, 255),
        2
    )

    for r in rider_info:
        x1, y1, x2, y2 = r["box"]

        x1 = int(x1 * scale) + xoff
        y1 = int(y1 * scale) + yoff
        x2 = int(x2 * scale) + xoff
        y2 = int(y2 * scale) + yoff

        x1 = max(0, x1)
        y1 = max(90, y1)
        x2 = min(video_w - 8, x2)
        y2 = min(canvas_h - 65, y2)

        if x2 <= x1 or y2 <= y1:
            continue

        color = r["color"]

        cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 4)

        tag = r["id"]
        tag_w = 58
        tag_h = 34

        tx1 = x1
        ty1 = max(92, y1 - tag_h)

        cv2.rectangle(canvas, (tx1, ty1), (tx1 + tag_w, ty1 + tag_h), color, -1)
        cv2.putText(
            canvas,
            tag,
            (tx1 + 8, ty1 + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.70,
            (0, 0, 0),
            2
        )

    px1 = video_w + 20
    py = 120

    cv2.putText(
        canvas,
        "Evidence Summary",
        (px1, py),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.76,
        (20, 20, 20),
        2
    )

    py += 45

    rows = [
        f"Total Riders: {total_riders}",
        f"Helmet OK: {helmet_ok}",
        f"No Helmet: {no_helmet}",
        f"Improper: {improper}",
        f"Manual Review: {manual_review}"
    ]

    for row in rows:
        cv2.putText(
            canvas,
            row,
            (px1, py),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (35, 35, 35),
            2
        )
        py += 32

    py += 10
    cv2.line(canvas, (px1, py), (canvas_w - 25, py), (180, 180, 180), 2)
    py += 35

    cv2.putText(
        canvas,
        "Rider-wise Status",
        (px1, py),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (0, 0, 0),
        2
    )

    py += 34

    for r in rider_info:
        color = r["color"]
        rid = r["id"]
        status = r["status"]

        cv2.rectangle(canvas, (px1, py - 20), (px1 + 24, py + 4), color, -1)
        cv2.putText(
            canvas,
            f"{rid}: {status}",
            (px1 + 36, py),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (25, 25, 25),
            2
        )
        py += 30

    py += 15

    if violations > 0:
        significance = "Helmet violation visible"
        reliability = "High visual evidence candidate"
        priority = "HIGH"
        rel_color = (0, 0, 180)

    elif total_riders > 0:
        significance = "Rider detected"
        reliability = "No violation in this frame"
        priority = "LOW"
        rel_color = (0, 120, 0)

    else:
        significance = "No clear rider"
        reliability = "Manual review"
        priority = "MEDIUM"
        rel_color = (0, 120, 255)

    cv2.putText(canvas, "Significance:", (px1, py), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 180), 2)
    py += 28
    cv2.putText(canvas, significance, (px1, py), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (70, 70, 70), 1)
    py += 40

    cv2.putText(canvas, "Reliability:", (px1, py), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 120, 0), 2)
    py += 28
    cv2.putText(canvas, reliability, (px1, py), cv2.FONT_HERSHEY_SIMPLEX, 0.45, rel_color, 1)

    cv2.rectangle(canvas, (0, canvas_h - 58), (canvas_w, canvas_h), (255, 255, 255), -1)

    if priority == "HIGH":
        msg = "Priority: HIGH | Helmet violation evidence candidate | Manual review before challan"
        msg_color = (0, 0, 255)

    elif priority == "LOW":
        msg = "Priority: LOW | Rider detected with no visible violation"
        msg_color = (0, 140, 0)

    else:
        msg = "Priority: MEDIUM | Scene unclear, manual review recommended"
        msg_color = (0, 120, 255)

    cv2.putText(
        canvas,
        msg,
        (28, canvas_h - 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.64,
        msg_color,
        2
    )

    report = {
        "frame_id": frame_id,
        "total_riders": total_riders,
        "helmet_ok": helmet_ok,
        "no_helmet": no_helmet,
        "improper_helmet": improper,
        "manual_review": manual_review,
        "violations": violations,
        "significance": significance,
        "reliability": reliability,
        "priority": priority
    }

    return canvas, report


def process_video(video_path, model_path, out_video, out_json, max_process=180):
    video_path = Path(video_path)
    model_path = Path(model_path)
    out_video = Path(out_video)
    out_json = Path(out_json)

    out_video.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)

    helmet_out = Path("outputs/helmet_plate")
    showcase_helmet_dir = Path("outputs/FINAL_SHOWCASE/helmet_plate")
    helmet_best_dir = Path("outputs/final_best/helmet_plate_best")

    helmet_out.mkdir(parents=True, exist_ok=True)
    showcase_helmet_dir.mkdir(parents=True, exist_ok=True)
    helmet_best_dir.mkdir(parents=True, exist_ok=True)

    helmet_model = YOLO(str(model_path))

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise RuntimeError("Could not open video: " + str(video_path))

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 25

    frame_step = 2
    output_fps = max(5, min(10, fps / frame_step))

    final_frames = []
    final_reports = []

    frame_id = 0
    processed = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        if frame_id % frame_step == 0:
            dets = collect_helmet_dets_clean(frame, helmet_model)
            rider_info = analyze_rider_status_clean(dets)
            annotated, report = draw_final_helmet_layout(frame, rider_info, frame_id)

            save_path = helmet_out / f"final_clean_uploaded_bike_frame_{frame_id}.jpg"
            cv2.imwrite(str(save_path), annotated)

            report["frame_path"] = str(save_path).replace("\\", "/")

            final_frames.append(annotated)
            final_reports.append(report)

            processed += 1

            if processed >= max_process:
                break

        frame_id += 1

    cap.release()

    if len(final_frames) == 0:
        raise RuntimeError("No frames were processed.")

    h, w = final_frames[0].shape[:2]

    writer = cv2.VideoWriter(
        str(out_video),
        cv2.VideoWriter_fourcc(*"mp4v"),
        output_fps,
        (w, h)
    )

    for fr in final_frames:
        writer.write(fr)

    writer.release()

    best = None
    best_score = -1

    for r in final_reports:
        score = 0
        score += r["no_helmet"] * 80
        score += r["improper_helmet"] * 50
        score += r["helmet_ok"] * 8
        score += r["total_riders"] * 5
        score -= r["manual_review"] * 8

        if score > best_score:
            best_score = score
            best = r

    best_img_path = None

    if best is not None:
        best_img_path = helmet_best_dir / "uploaded_bike_helmet_best_frame_final_clean.jpg"
        shutil.copy(best["frame_path"], best_img_path)
        shutil.copy(best_img_path, showcase_helmet_dir / "uploaded_bike_helmet_best_frame_final_clean.jpg")

    summary = {
        "module": "helmet_video_demo",
        "input_video": str(video_path).replace("\\", "/"),
        "output_video": str(out_video).replace("\\", "/"),
        "processed_frames": len(final_reports),
        "best_frame": best,
        "best_frame_path": str(best_img_path).replace("\\", "/") if best_img_path else None,
        "status": "Kaggle notebook style processed helmet demo generated",
        "safety": "Manual review is required before challan or legal action."
    }

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    print("Final clean uploaded bike helmet demo completed")
    print("Input video:", video_path)
    print("Output video:", out_video)
    print("Best frame:", best_img_path)
    print("Report:", out_json)
    print(json.dumps(summary, indent=4))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", default="data/sample_videos/violationiq_bike_helmet_demo.mp4")
    parser.add_argument("--model", default="weights/helmet_yolo11s_best.pt")
    parser.add_argument("--out_video", default="outputs/FINAL_SHOWCASE/videos/helmet_video_demo_processed_1.mp4")
    parser.add_argument("--out_json", default="outputs/FINAL_SHOWCASE/videos/helmet_video_report_1.json")
    args = parser.parse_args()

    process_video(
        video_path=args.video,
        model_path=args.model,
        out_video=args.out_video,
        out_json=args.out_json
    )


if __name__ == "__main__":
    main()
