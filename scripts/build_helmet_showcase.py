import json
import shutil
from pathlib import Path


def build_helmet_showcase_from_frames(src_dir="outputs/helmet_plate", out_dir="outputs/FINAL_SHOWCASE/helmet_plate"):
    src_dir = Path(src_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    frames = sorted(src_dir.glob("final_clean_uploaded_bike_frame_*.jpg"))

    if len(frames) == 0:
        frames = sorted(src_dir.glob("*.jpg"))

    selected = []

    if len(frames) <= 5:
        selected = frames
    else:
        idxs = [0, len(frames)//4, len(frames)//2, (len(frames)*3)//4, len(frames)-1]
        for idx in idxs:
            selected.append(frames[idx])

    reports = []

    for i, src in enumerate(selected[:5], 1):
        out_img = out_dir / f"helmet_evidence_{i}.jpg"
        out_json = out_dir / f"helmet_report_{i}.json"

        shutil.copy(src, out_img)

        report = {
            "module": "helmet_plate",
            "input_frame": str(src).replace("\\", "/"),
            "output_image": str(out_img).replace("\\", "/"),
            "status": "Helmet/rider evidence frame generated from processed demo video",
            "safety": "Manual review is required before challan or legal action."
        }

        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)

        reports.append(report)

    with open(out_dir / "helmet_summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "module": "helmet_plate",
            "images_processed": len(reports),
            "safety": "Helmet evidence frames are generated for reviewer support."
        }, f, indent=4)

    print("Helmet image outputs:", len(reports))
    return len(reports)


if __name__ == "__main__":
    build_helmet_showcase_from_frames()
