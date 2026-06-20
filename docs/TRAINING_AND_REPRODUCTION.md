# Training and Reproduction Notes

This repository contains clean source modules for the ViolationIQ submission.

## Training Commands

```bash
python scripts/train_yolo.py --data path/to/traffic_data.yaml --model yolo11s.pt --epochs 30 --imgsz 768 --name traffic_yolo11s
python scripts/train_yolo.py --data path/to/helmet_data.yaml --model yolo11s.pt --epochs 60 --imgsz 768 --name helmet_yolo11s
python scripts/train_yolo.py --data path/to/plate_data.yaml --model yolo11s.pt --epochs 30 --imgsz 768 --name plate_yolo11s
```

## Required Weights

- traffic_yolo11s_best.pt
- helmet_yolo11s_best.pt
- plate_yolo11s_best.pt

Large weights should not be pushed to GitHub.

## Final Outputs Covered

- helmet and rider evidence
- safe plate OCR/manual-review interface
- red-light video evidence JSON
- signboard context report
- final showcase index
