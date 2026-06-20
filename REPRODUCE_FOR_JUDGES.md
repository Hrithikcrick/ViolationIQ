# Reproduce ViolationIQ Judge Outputs

## 1. Clone repository

git clone https://github.com/Hrithikcrick/ViolationIQ.git
cd ViolationIQ

## 2. Create Python environment

Windows:

python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Linux / Mac:

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

## 3. Download judge assets

Automatic download:

python scripts/download_assets.py

If automatic download fails, manually download the Judge Asset Zip from Google Drive and extract it inside the repository root.

Judge Asset Zip:
https://drive.google.com/file/d/1XeJq1Afzw0hjd1gdzt1pjwlz6GvF4J2f/view?usp=sharing

After extraction, the repository should contain:

weights/traffic_yolo11s_best.pt
weights/helmet_yolo11s_best.pt
weights/large_plate_yolo11s_best.pt
weights/yolo26n.pt
data/sample_images/ocr_showcase/
data/sample_images/signboard_showcase/
data/sample_videos/violationiq_bike_helmet_demo.mp4

## 4. Check source code

python -m compileall -f src scripts

## 5. Run final reproduction

Windows:

python scripts\reproduce_pipeline.py --traffic_model weights\traffic_yolo11s_best.pt --helmet_model weights\helmet_yolo11s_best.pt --plate_model weights\large_plate_yolo11s_best.pt --vehicle_model weights\yolo26n.pt

Linux / Mac:

python scripts/reproduce_pipeline.py --traffic_model weights/traffic_yolo11s_best.pt --helmet_model weights/helmet_yolo11s_best.pt --plate_model weights/large_plate_yolo11s_best.pt --vehicle_model weights/yolo26n.pt

## 6. Expected output

Reproduction completed.
Helmet evidence images generated: 5
Signboard context images generated: 5
Safe OCR reports generated: 5
Helmet videos processed: 1
Summary saved: reports/reproduction_summary.json
Showcase index: outputs/FINAL_SHOWCASE/final_showcase_index.csv

## 7. Generated folders

outputs/FINAL_SHOWCASE/helmet_plate/
outputs/FINAL_SHOWCASE/plate_ocr/
outputs/FINAL_SHOWCASE/signboard_context/
outputs/FINAL_SHOWCASE/videos/
outputs/FINAL_SHOWCASE/final_showcase_index.csv
reports/reproduction_summary.json

ViolationIQ is an AI evidence copilot. Manual review is required before challan or legal action.
