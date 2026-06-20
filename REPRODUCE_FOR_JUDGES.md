# ViolationIQ Judge Reproduction Guide

## Repository

```bash
git clone https://github.com/Hrithikcrick/ViolationIQ.git
cd ViolationIQ
```

## Asset Zip

Download link:

https://drive.google.com/file/d/1XeJq1Afzw0hjd1gdzt1pjwlz6GvF4J2f/view?usp=sharing

The asset zip contains trained YOLO weights and sample input files needed to reproduce the reported outputs.

Expected extracted structure:

```text
weights/
  traffic_yolo11s_best.pt
  helmet_yolo11s_best.pt
  large_plate_yolo11s_best.pt
  yolo26n.pt

data/
  sample_images/
  sample_videos/
```

## Create Environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Linux/Mac:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Download Assets Automatically

```bash
python scripts/download_assets.py
```

If automatic download fails, manually download the Google Drive zip and extract it inside the repository root.

## Check Source Code

```bash
python -m compileall -f src scripts
```

## Reproduce Final Results

Windows:

```bash
python scripts\reproduce_pipeline.py --traffic_model weights\traffic_yolo11s_best.pt --helmet_model weights\helmet_yolo11s_best.pt --plate_model weights\large_plate_yolo11s_best.pt --vehicle_model weights\yolo26n.pt
```

Linux/Mac:

```bash
python scripts/reproduce_pipeline.py --traffic_model weights/traffic_yolo11s_best.pt --helmet_model weights/helmet_yolo11s_best.pt --plate_model weights/large_plate_yolo11s_best.pt --vehicle_model weights/yolo26n.pt
```

Expected console output:

```text
Reproduction completed.
Images processed: 1
Videos processed: 2
Summary saved: reports/reproduction_summary.json
Showcase index: outputs/FINAL_SHOWCASE/final_showcase_index.csv
```

## Generated Deliverables

```text
outputs/FINAL_SHOWCASE/helmet_plate/
outputs/FINAL_SHOWCASE/redlight/
outputs/FINAL_SHOWCASE/signboard_context/
outputs/FINAL_SHOWCASE/final_showcase_index.csv
reports/reproduction_summary.json
```

## Important Note

The .pt model weights are not committed to GitHub because they are large. They are provided separately through the Google Drive asset zip.

The system generates evidence and review candidates. Manual verification is required before any challan or legal action.

