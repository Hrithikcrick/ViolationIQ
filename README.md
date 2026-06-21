# ViolationIQ

<p align="center">
  <b>Adaptive Multi-Expert AI Evidence Copilot for Traffic Enforcement</b>
</p>

<p align="center">
  <b>Helmet Detection • Safe Plate OCR • Signboard Context • Evidence Reports • Helmet Video Demo</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue" />
  <img src="https://img.shields.io/badge/YOLO11s-Detection-green" />
  <img src="https://img.shields.io/badge/OpenCV-Computer%20Vision-orange" />
  <img src="https://img.shields.io/badge/EasyOCR-Safe%20ANPR-red" />
</p>

<p align="center">
  <a href="https://drive.google.com/file/d/1LWZj-UicQOj7A8Tgj7nxW3Cm-2gn7EOJ/view?usp=sharing"><b>📦 Download Judge Assets</b></a>
  &nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="https://github.com/Hrithikcrick/ViolationIQ/archive/refs/heads/main.zip"><b>💻 Download Source Code</b></a>
  &nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="#judge-reproduction-guide"><b>⚙️ Reproduce Outputs</b></a>
  &nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="reports/ViolationIQ_IEEE_Report.pdf"><b>📄 Project Report</b></a>
</p>

---

## Overview

ViolationIQ is a safety-first AI framework for traffic violation evidence generation using Computer Vision.

It is designed as an **AI evidence copilot**, not as an automatic challan generator. The system prepares review-ready traffic evidence and routes uncertain cases to manual review.

---

## Project Focus

ViolationIQ supports:

- helmet and rider evidence generation
- rider-wise helmet or no-helmet detection
- dedicated number plate localization
- safe OCR / ANPR fallback
- signboard context evidence
- structured JSON and CSV reporting
- processed helmet video demo
- final showcase outputs for review

---

## Problem Statement

**Automated Photo Identification and Classification for Traffic Violations Using Computer Vision**

The project focuses on creating reliable evidence outputs from traffic images and videos. It avoids unsafe automatic enforcement decisions by using confidence checks, safe OCR, evidence formatting, and manual-review fallback.

---

## Key Idea

Traffic violations need different types of evidence.

- A helmet violation needs rider-wise association.
- A number plate module needs plate localization and OCR validation.
- A signboard module gives traffic-rule context.
- A video module generates processed helmet evidence from a raw bike video.

Therefore, ViolationIQ uses an adaptive multi-expert architecture instead of one single detector for every task.

---

## System Architecture

ViolationIQ follows the final adaptive multi-expert architecture:

```text
Input Traffic Image / Video
        |
        v
Adaptive Multi-Expert Router
        |
        +--> Helmet + Rider Expert
        |       -> rider-wise helmet/no-helmet evidence
        |
        +--> Plate + Safe OCR Expert
        |       -> plate localization, OCR, validation, manual review
        |
        +--> Signboard Context Expert
        |       -> signboard context evidence using real samples and XML
        |
        +--> Helmet Video Expert
                -> processed helmet violation demo video

All outputs go through:

Evidence Reasoning Layer
        |
        v
Safety Layer
        |
        v
Review-ready evidence panels + JSON reports + CSV index
```

The system does not generate automatic challans. Unclear OCR, weak detections, and ambiguous evidence are routed to manual review.

---

## Final Judge-Reproducible Outputs

The final judge reproduction script generates:

- 5 helmet and rider evidence images
- 5 safe plate OCR evidence panels
- 5 signboard context evidence images
- 1 processed helmet violation demo video
- helmet, OCR, signboard, and video JSON reports
- final showcase CSV index
- reproduction summary JSON

Generated folders:

```text
outputs/FINAL_SHOWCASE/helmet_plate/
outputs/FINAL_SHOWCASE/plate_ocr/
outputs/FINAL_SHOWCASE/signboard_context/
outputs/FINAL_SHOWCASE/videos/
outputs/FINAL_SHOWCASE/final_showcase_index.csv
reports/reproduction_summary.json
```

---

## Models Used

| Module | Model / Method | Purpose |
|---|---|---|
| Helmet Expert | YOLO11s | Rider, helmet, no-helmet, bad helmet detection |
| Plate Expert | YOLO11s | Number plate localization |
| OCR Layer | EasyOCR + validation rules | Plate reading only when reliable |
| Signboard Context Expert | XML annotations + rule context | Signboard evidence using real samples |
| Helmet Video Expert | YOLO11s + OpenCV | Processed helmet violation demo video |
| Safety Layer | Rule-based logic | Manual review, safety, evidence priority |

---

## Results Recorded During Development

| Module | Recorded Result |
|---|---|
| Traffic YOLO11s model | mAP50 around 0.928, mAP50-95 around 0.808 |
| Helmet/Rider YOLO11s model | mAP50 around 0.701, mAP50-95 around 0.32 |
| Dedicated Plate YOLO11s model | Validation mAP50 around 0.924, mAP50-95 around 0.548 |
| Plate dataset split | 7057 train, 2048 validation, 1020 test |

These training metrics were obtained during Kaggle training. The GitHub judge reproduction reproduces final inference/demo outputs using trained weights and selected sample inputs.

---

## Repository Structure

```text
ViolationIQ/
|-- README.md
|-- requirements.txt
|-- REPRODUCE_FOR_JUDGES.md
|-- REPRODUCIBILITY_SCOPE.md
|-- src/
|   |-- adaptive_router.py
|   |-- helmet_plate_module.py
|   |-- signboard_context_module.py
|   |-- safety_utils.py
|-- scripts/
|   |-- download_assets.py
|   |-- reproduce_pipeline.py
|   |-- process_ocr_samples.py
|   |-- process_helmet_video_demo.py
|   |-- process_signboard_showcase.py
|-- reports/
|   |-- ViolationIQ_IEEE_Report.pdf
|   |-- reproduction_summary.json
|-- outputs/
|   |-- FINAL_SHOWCASE/
|-- architecture/
```

---

## Judge Reproduction Guide

Use these steps to reproduce the final outputs from a fresh machine.

### 1. Clone repository

```bash
git clone https://github.com/Hrithikcrick/ViolationIQ.git
cd ViolationIQ
```

### 2. Create environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Linux / Mac:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Download judge assets

The trained weights and sample input files are provided separately because model weights and videos are large.

Judge Asset Zip:

https://drive.google.com/file/d/1LWZj-UicQOj7A8Tgj7nxW3Cm-2gn7EOJ/view?usp=sharing

Automatic download:

```bash
python scripts/download_assets.py
```

If automatic download fails, manually download the zip from Google Drive and extract it inside the repository root.

After extraction, the repository should contain:

```text
weights/traffic_yolo11s_best.pt
weights/helmet_yolo11s_best.pt
weights/large_plate_yolo11s_best.pt
weights/yolo26n.pt
data/sample_images/ocr_showcase/
data/sample_images/signboard_showcase/
data/sample_videos/violationiq_bike_helmet_demo.mp4
```

### 4. Check source code

```bash
python -m compileall -f src scripts
```

### 5. Run final reproduction

Windows:

```powershell
python scripts\reproduce_pipeline.py --traffic_model weights\traffic_yolo11s_best.pt --helmet_model weights\helmet_yolo11s_best.pt --plate_model weights\large_plate_yolo11s_best.pt --vehicle_model weights\yolo26n.pt
```

Linux / Mac:

```bash
python scripts/reproduce_pipeline.py --traffic_model weights/traffic_yolo11s_best.pt --helmet_model weights/helmet_yolo11s_best.pt --plate_model weights/large_plate_yolo11s_best.pt --vehicle_model weights/yolo26n.pt
```

Expected output:

```text
Reproduction completed.
Helmet evidence images generated: 5
Signboard context images generated: 5
Safe OCR reports generated: 5
Helmet videos processed: 1
Summary saved: reports/reproduction_summary.json
Showcase index: outputs/FINAL_SHOWCASE/final_showcase_index.csv
```

### 6. Check generated outputs

Windows:

```powershell
dir outputs\FINAL_SHOWCASE
dir outputs\FINAL_SHOWCASE\helmet_plate
dir outputs\FINAL_SHOWCASE\plate_ocr
dir outputs\FINAL_SHOWCASE\signboard_context
dir outputs\FINAL_SHOWCASE\videos
dir reports
```

Linux / Mac:

```bash
ls outputs/FINAL_SHOWCASE
ls outputs/FINAL_SHOWCASE/helmet_plate
ls outputs/FINAL_SHOWCASE/plate_ocr
ls outputs/FINAL_SHOWCASE/signboard_context
ls outputs/FINAL_SHOWCASE/videos
ls reports
```

---

## Safe Plate OCR / ANPR Evidence

ViolationIQ includes a dedicated number plate localization and safe OCR fallback module.

The OCR module does not force a plate number when the plate is unclear. If the crop is blurred, partial, unreadable, or OCR confidence is weak, the result is marked for manual review.

Judge-reproducible OCR outputs:

```text
outputs/FINAL_SHOWCASE/plate_ocr/plate_ocr_evidence_1.jpg
outputs/FINAL_SHOWCASE/plate_ocr/plate_ocr_evidence_2.jpg
outputs/FINAL_SHOWCASE/plate_ocr/plate_ocr_evidence_3.jpg
outputs/FINAL_SHOWCASE/plate_ocr/plate_ocr_evidence_4.jpg
outputs/FINAL_SHOWCASE/plate_ocr/plate_ocr_evidence_5.jpg
outputs/FINAL_SHOWCASE/plate_ocr/plate_ocr_summary.json
```

This prevents wrong challans due to forced or incorrect number plate reading.

---

## What Judges Can Reproduce

Judges can reproduce the final inference/demo deliverables:

- 5 helmet and rider evidence images
- 5 safe plate OCR evidence panels
- 5 signboard context evidence images
- 1 processed helmet video demo
- JSON reports
- CSV showcase index
- reproduction summary

Full model retraining is not part of the judge reproduction package. To reproduce training metrics from scratch, the original Kaggle datasets, Kaggle training notebook, GPU environment, and full training commands are required.

---

## Important Safety Note

ViolationIQ is a decision-support system. It does not automatically issue challans.

The system marks uncertain cases for manual review when:

- OCR confidence is weak
- plate is unreadable
- visual evidence is unclear
- scene context is ambiguous
- camera calibration or temporal tracking is required

Manual verification is required before any challan or legal action.

---

## Project Report

The IEEE-style project report is available here:

```text
reports/ViolationIQ_IEEE_Report.pdf
```

---

## Final Claim

ViolationIQ is an adaptive multi-expert AI evidence copilot for traffic enforcement. It produces clean, review-ready, safety-aware evidence for helmet violations, number plate evidence, signboard context, and final demo review outputs.
