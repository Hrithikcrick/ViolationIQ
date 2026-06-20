import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ultralytics import YOLO
from src.helmet_plate_module import HelmetPlateModule


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--helmet_model", required=True)
    parser.add_argument("--plate_model", default=None)
    parser.add_argument("--out_image", default="outputs/FINAL_SHOWCASE/helmet_plate/evidence.jpg")
    parser.add_argument("--out_json", default="outputs/FINAL_SHOWCASE/helmet_plate/report.json")
    args = parser.parse_args()

    helmet_model = YOLO(args.helmet_model)
    plate_model = YOLO(args.plate_model) if args.plate_model else None

    module = HelmetPlateModule(
        helmet_model=helmet_model,
        plate_model=plate_model,
    )

    report = module.run_image(
        image_path=args.image,
        output_image_path=args.out_image,
        output_json_path=args.out_json,
    )

    print(report)


if __name__ == "__main__":
    main()
