<!-- COLOR_HEADER_START -->

<div align="center">

# 🚦 ViolationIQ

### Adaptive Multi-Expert AI Evidence Copilot for Traffic Enforcement

<b>Helmet Detection • Safe Plate OCR • Signboard Context • Evidence Reports • Helmet Video Demo</b>

<br>

<img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python">
<img src="https://img.shields.io/badge/YOLO11s-Detection-brightgreen?style=for-the-badge">
<img src="https://img.shields.io/badge/OpenCV-Computer%20Vision-orange?style=for-the-badge&logo=opencv">
<img src="https://img.shields.io/badge/EasyOCR-Safe%20ANPR-red?style=for-the-badge">
<img src="https://img.shields.io/badge/Status-Judge%20Reproducible-success?style=for-the-badge">

<br><br>

### 🎥 Helmet Violation Demo

<a href="demo/violationiq_bike_helmet_demo.mp4"><b>▶ Watch Processed Helmet Violation Demo</b></a>

<br><br>

<a href="https://drive.google.com/file/d/1XeJq1Afzw0hjd1gdzt1pjwlz6GvF4J2f/view?usp=sharing"><b>📦 Download Judge Assets</b></a>
&nbsp;&nbsp;|&nbsp;&nbsp;
<a href="#judge-reproduction-guide"><b>⚙️ Reproduce Outputs</b></a>
&nbsp;&nbsp;|&nbsp;&nbsp;
<a href="reports/ViolationIQ_IEEE_Report.pdf"><b>📄 Project Report</b></a>

</div>

---

<!-- COLOR_HEADER_END -->
Safety-first AI framework for traffic violation evidence generation using Computer Vision.

ViolationIQ is designed as an AI evidence copilot, not as an automatic challan generator. It prepares review-ready traffic evidence and sends uncertain cases to manual review.

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

## Problem Statement

Automated Photo Identification and Classification for Traffic Violations Using Computer Vision

The project focuses on creating reliable evidence outputs from traffic images and videos. It avoids unsafe automatic enforcement decisions by using confidence checks, safe OCR, evidence formatting, and manual-review fallback.

## Key Idea

Traffic violations need different types of evidence. A helmet violation needs rider-wise association. A number plate module needs plate localization and OCR validation. A signboard module gives traffic-rule context. Therefore, ViolationIQ uses an adaptive multi-expert architecture instead of one single detector for every task.

## Final Judge-Reproducible Outputs

The final judge reproduction script generates:

- helmet and rider evidence image
- rider-wise helmet/no-helmet JSON report
- safe plate OCR evidence panel
- plate OCR/manual-review JSON report
- signboard context evidence image
- signboard context JSON report
- best helmet video demo copied into final showcase
- final showcase CSV index
- reproduction summary JSON

Generated folders:

    outputs/FINAL_SHOWCASE/helmet_plate/
    outputs/FINAL_SHOWCASE/plate_ocr/
    outputs/FINAL_SHOWCASE/signboard_context/
    outputs/FINAL_SHOWCASE/videos/
    outputs/FINAL_SHOWCASE/final_showcase_index.csv
    reports/reproduction_summary.json

## Models Used

| Module | Model / Method | Purpose |
|---|---|---|
| Traffic / Signboard Expert | YOLO11s | Traffic signs, traffic lights, vehicles, sign context |
| Helmet Expert | YOLO11s | Rider, helmet, no-helmet, bad helmet detection |
| Plate Expert | YOLO11s | Number plate localization |
| OCR Layer | EasyOCR + validation rules | Plate reading only when reliable |
| Reasoning Layer | Rule-based logic | Manual review, safety, evidence priority |

## Results Recorded During Development

| Module | Recorded Result |
|---|---|
| Traffic YOLO11s model | mAP50 around 0.928, mAP50-95 around 0.808 |
| Helmet/Rider YOLO11s model | mAP50 around 0.701, mAP50-95 around 0.32 |
| Dedicated Plate YOLO11s model | Validation mAP50 around 0.924, mAP50-95 around 0.548 |
| Plate dataset split | 7057 train, 2048 validation, 1020 test |

These training metrics were obtained during Kaggle training. The GitHub judge reproduction reproduces final inference/demo outputs using trained weights and sample inputs.

## Repository Structure

    ViolationIQ/
    |-- README.md
    |-- requirements.txt
    |-- REPRODUCE_FOR_JUDGES.md
    |-- REPRODUCIBILITY_SCOPE.md
    |
    |-- src/
    |   |-- adaptive_router.py
    |   |-- helmet_plate_module.py
    |   |-- signboard_context_module.py
    |   |-- safety_utils.py
    |
    |-- scripts/
    |   |-- download_assets.py
    |   |-- reproduce_pipeline.py
    |   |-- run_helmet_image.py
    |   |-- train_yolo.py
    |
    |-- config/
    |-- architecture/
    |-- reports/
    |-- outputs/
    |   |-- FINAL_SHOWCASE/
    |
    |-- models_info/
    |-- demo/

## Judge Reproduction Guide

Use these steps to reproduce the final outputs from a fresh machine.

### 1. Clone repository

    git clone https://github.com/Hrithikcrick/ViolationIQ.git
    cd ViolationIQ

### 2. Create environment

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

### 3. Download judge assets

The trained weights and sample input files are provided separately because model weights and videos are large.

Judge asset zip:

https://drive.google.com/file/d/1XeJq1Afzw0hjd1gdzt1pjwlz6GvF4J2f/view?usp=sharing

Automatic download:

    python scripts/download_assets.py

If automatic download fails, manually download the zip from Google Drive and extract it inside the repository root.

After extraction, the repository should contain:

    weights/traffic_yolo11s_best.pt
    weights/helmet_yolo11s_best.pt
    weights/large_plate_yolo11s_best.pt
    weights/yolo26n.pt
    data/sample_images/
    data/sample_videos/

### 4. Check source code

    python -m compileall -f src scripts

### 5. Run final reproduction

Windows:

    python scripts\reproduce_pipeline.py --traffic_model weights\traffic_yolo11s_best.pt --helmet_model weights\helmet_yolo11s_best.pt --plate_model weights\large_plate_yolo11s_best.pt --vehicle_model weights\yolo26n.pt

Linux / Mac:

    python scripts/reproduce_pipeline.py --traffic_model weights/traffic_yolo11s_best.pt --helmet_model weights/helmet_yolo11s_best.pt --plate_model weights/large_plate_yolo11s_best.pt --vehicle_model weights/yolo26n.pt

Expected output:

    Reproduction completed.
    Images processed: 1
    Helmet videos processed: 1
    Safe OCR reports generated: 1
    Summary saved: reports/reproduction_summary.json
    Showcase index: outputs/FINAL_SHOWCASE/final_showcase_index.csv

### 6. Check generated outputs

Windows:

    dir outputs\FINAL_SHOWCASE
    dir outputs\FINAL_SHOWCASE\helmet_plate
    dir outputs\FINAL_SHOWCASE\plate_ocr
    dir outputs\FINAL_SHOWCASE\signboard_context
    dir outputs\FINAL_SHOWCASE\videos
    dir reports

Linux / Mac:

    ls outputs/FINAL_SHOWCASE
    ls outputs/FINAL_SHOWCASE/helmet_plate
    ls outputs/FINAL_SHOWCASE/plate_ocr
    ls outputs/FINAL_SHOWCASE/signboard_context
    ls outputs/FINAL_SHOWCASE/videos
    ls reports

## What Judges Can Reproduce

Judges can reproduce the final inference/demo deliverables:

- helmet image evidence
- safe plate OCR evidence
- signboard context evidence
- best helmet video demo copied into final showcase
- JSON reports
- CSV showcase index
- reproduction summary

Full model retraining is not part of the judge reproduction package. To reproduce training metrics from scratch, the original Kaggle datasets, Kaggle training notebook, GPU environment, and full training commands are required.

## Important Safety Note

ViolationIQ is a decision-support system. It does not automatically issue challans.

The system marks uncertain cases for manual review when:

- OCR confidence is weak
- plate is unreadable
- visual evidence is unclear
- scene context is ambiguous
- camera calibration or temporal tracking is required

Manual verification is required before any challan or legal action.

## Project Report

The IEEE-style project report is available in the reports folder:

    reports/ViolationIQ_IEEE_Report.pdf
    reports/ViolationIQ_IEEE_Report.tex

## Final Claim

ViolationIQ is an adaptive multi-expert AI evidence copilot for traffic enforcement. It produces clean, review-ready, safety-aware evidence for helmet violations, number plate evidence, signboard context, and final demo review outputs.

<!-- OCR_SECTION_START -->

## Safe Plate OCR / ANPR Evidence

ViolationIQ includes a dedicated number plate localization and safe OCR fallback module.

The OCR module does not force a plate number when the plate is unclear. If the crop is blurred, partial, unreadable, or OCR confidence is weak, the result is marked for manual review.

Judge-reproducible OCR outputs:

    outputs/FINAL_SHOWCASE/plate_ocr/
    outputs/FINAL_SHOWCASE/plate_ocr/plate_ocr_evidence_1.jpg
    outputs/FINAL_SHOWCASE/plate_ocr/plate_ocr_report_1.json

The OCR report includes:

- detected plate candidate boxes
- plate crop readability score
- OCR confidence
- cleaned OCR text
- safe OCR status
- manual-review flag

Safe OCR policy:

    Reliable OCR      -> show plate candidate
    Weak OCR          -> mark UNREADABLE
    Unclear plate     -> manual review
    Low readability   -> manual review

This prevents wrong challans due to forced or incorrect number plate reading.

<!-- OCR_SECTION_END -->

