import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ultralytics import YOLO

from src.redlight_module import RedLightModule


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--vehicle_model", required=True)
    parser.add_argument("--out_json", default="outputs/FINAL_SHOWCASE/redlight/report.json")
    parser.add_argument("--evidence_dir", default="outputs/FINAL_SHOWCASE/redlight")

    args = parser.parse_args()

    vehicle_model = YOLO(args.vehicle_model)
    module = RedLightModule(vehicle_model=vehicle_model)

    report = module.run_video(
        video_path=args.video,
        output_json_path=args.out_json,
        evidence_dir=args.evidence_dir,
    )

    print(report)


if __name__ == "__main__":
    main()
