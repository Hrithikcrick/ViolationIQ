# 🚦 ViolationIQ: Adaptive Multi-Expert AI Evidence Copilot for Traffic Enforcement

<p align="center">
  <b>Safety-first AI framework for traffic violation evidence generation</b><br>
  Helmet Detection • Number Plate Evidence • Red-Light Video Evidence • Signboard Context
</p>

<p align="center">
  <b>Built for automated photo/video-based traffic violation identification using Computer Vision</b>
</p>

<p align="center">
  <a href="demo/violationiq_bike_helmet_demo.mp4"><b>🎥 Watch Processed Helmet Violation Demo</b></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue">
  <img src="https://img.shields.io/badge/YOLO-Detection-brightgreen">
  <img src="https://img.shields.io/badge/OpenCV-Computer%20Vision-orange">
  <img src="https://img.shields.io/badge/EasyOCR-ANPR-red">
  <img src="https://img.shields.io/badge/Status-Implemented-success">
</p>

---
## 1. Project Overview

**ViolationIQ** is an adaptive computer-vision based traffic enforcement evidence system.

The goal of this project is not to blindly generate challans. Instead, ViolationIQ works as an **AI Evidence Copilot** that detects possible traffic violations, prepares clean review-ready evidence, attaches number plate information only when reliable, and sends uncertain cases to manual review.

The system is designed for real-world traffic scenes where false challans can happen because of blurry images, wrong OCR, unclear traffic signs, poor lighting, occlusion, camera angle issues, and road-specific geometry.

---

## 2. Problem Statement Alignment

This project is aligned with:

> **Automated Photo Identification and Classification for Traffic Violations Using Computer Vision**

The system focuses on traffic violation evidence generation from images and videos, including:

- helmet violation detection,
- rider-wise evidence generation,
- number plate detection,
- safe OCR / ANPR,
- red-light video evidence,
- signboard context detection,
- structured reports,
- final showcase outputs.

---

## 3. Motivation

Traffic enforcement using cameras is challenging because:

- number plates can be small, blurred, tilted, or partially visible,
- OCR can produce wrong or incomplete plate numbers,
- red-light violation needs temporal evidence, not only one frame,
- a wrong automatic challan can reduce public trust.

Therefore, ViolationIQ uses a **multi-expert, safety-first architecture** instead of a single detector.

---


## 4. Datasets Used

ViolationIQ uses separate datasets for separate evidence tasks. This keeps the system modular and avoids forcing one model to solve every traffic enforcement problem.

| Module | Dataset Used | Purpose |
|---|---|---|
| Traffic / Signboard Expert | `guisahanes/traffic-violation-detection-dataset` | Vehicles, traffic lights, traffic signs, no-entry, no-stopping, stop, and turn-context evidence |
| Helmet + Rider Expert | `aryanvaid13/indian-helmet-detection-dataset` | Rider detection and helmet / no-helmet classification |
| Dedicated Number Plate Expert | Large YOLO plate dataset with `10,125` images | Number plate localization and crop extraction |
| Red-Light Evidence Module | `farzadnekouei/license-plate-recognition-for-red-light-violation` | Red-light video evidence with signal color and stop-line crossing |
| Final Demo Video | Private uploaded dataset `Videofbike` | Final processed helmet violation MP4 demo |


## 5. Models Used and Results Summary

| Expert | Model / Method | Purpose |
|---|---|---|
| Traffic Expert | YOLO11s | Vehicles, traffic signs, traffic lights, traffic context |
| Helmet Expert | YOLO11s | Rider, helmet, no-helmet, bad helmet |
| Plate Expert | YOLO11s | Number plate localization |
| OCR | EasyOCR + validation rules | Plate text reading only when reliable |
| Reasoning Layer | Rule-based logic | Manual review, temporal voting, context decision |

### Experimental results recorded during development

| Module | Result |
|---|---|
| Traffic model | mAP50 around `0.928`, mAP50-95 around `0.808` |
| Helmet/rider model | mAP50 around `0.701`, mAP50-95 around `0.32` |
| Dedicated plate model | Validation mAP50 around `0.924`, mAP50-95 around `0.548` |
| Plate dataset | `10,125` images total: `7057` train, `2048` validation, `1020` test |
| Red-light video evidence | Signal color + vehicle crossing + virtual stop-line + temporal/manual-review safety |

Model weights are not committed to GitHub because they are large. The repository documents expected model names and paths in `models_info/`, `config/`, and the source modules.

---

## 6. Implemented Deliverables

| No. | Implemented Deliverable | What it Produces |
|---|---|---|
| 1 | Adaptive Multi-Expert Router | Routes image/video input toward the suitable evidence module |
| 2 | Helmet + Rider Detection | Detects riders and classifies helmet / no-helmet status |
| 3 | Rider-wise Evidence Panel | Generates clean R1, R2, R3 style rider evidence |
| 4 | Dedicated Number Plate Detection | Detects plate region using a separate trained plate detector |
| 5 | Safe OCR / ANPR Fallback | Shows plate number only when reliable; otherwise marks manual review |
| 6 | Red-Light Video Evidence | Detects signal color, vehicle presence, and stop-line crossing evidence |
| 7 | Signboard Context Evidence | Detects traffic sign context such as no-entry, no-stopping, stop, and turn signs |
| 8 | Final Demo Videos | Stores processed MP4 demo videos inside `demo/` and `outputs/video/` |
| 9 | JSON / CSV Reports | Saves structured evidence reports for review |
| 10 | Architecture and Documentation | Includes architecture diagram, modular source code, config, reports, and README |

---

## 7. System Approach

ViolationIQ follows a modular pipeline:

```text
Input Image / Video
        |
        v
Adaptive Router
        |
        |-- Helmet + Plate Module
        |-- Red-Light Video Module
        |-- Signboard Context Module
        |
        v
Evidence Reasoning Layer
        |
        |-- Helmet compliance decision
        |-- Safe plate OCR validation
        |-- Traffic signal + stop-line reasoning
        |-- Signboard context reasoning
        |-- Temporal voting
        |
        v
Safety Layer
        |
        |-- No forced OCR
        |-- Manual review fallback
        |-- Camera calibration requirement
        |-- No unsafe automatic challan
        |
        v
Clean Evidence Panel + JSON/CSV Report
```

---

## 8. Architecture Used

ViolationIQ uses an **Adaptive Multi-Expert Architecture**.

A single object detection model is not sufficient for traffic enforcement because each violation needs a different kind of evidence.

| Violation Type | Why separate handling is needed |
|---|---|
| Helmet violation | Needs rider-wise association between rider and helmet/face. |
| Number plate | Needs dedicated plate localization and OCR validation. |
| Red-light violation | Needs video, signal color, stop-line, and temporal voting. |
| Signboard violation context | Needs traffic sign detection and rule-based context reasoning. |

So ViolationIQ separates the system into expert modules and connects them through an adaptive router.

---

## 9. Advanced Architecture Diagram

```text
Input Image / Video
        |
        v
+--------------------------------+
| Adaptive Multi-Expert Router   |
+--------------------------------+
        |
        |-- Helmet + Rider Expert
        |-- Number Plate Expert
        |-- Red-Light Video Expert
        |-- Signboard Context Expert
        |-- Manual Review for uncertain cases
        |
        v
+--------------------------------+
| Evidence Reasoning Layer       |
+--------------------------------+
| Helmet compliance              |
| Safe OCR validation            |
| Signal + stop-line crossing    |
| Signboard context reasoning    |
| Temporal voting                |
+--------------------------------+
        |
        v
+--------------------------------+
| Safety Layer                   |
+--------------------------------+
| No forced OCR                  |
| Manual review fallback         |
| Camera calibration required    |
| No unsafe automatic challan    |
+--------------------------------+
        |
        v
Clean Evidence Panel + JSON/CSV Report
```

Architecture files:

```text
architecture/violationiq_architecture_main.png
architecture/architecture_mermaid.md
```

---

## 10. Adaptive Router

The adaptive router decides which module should run.

| Input Type / Scene | Selected Module |
|---|---|
| Video input | Red-Light Video Module |
| Image with riders / helmets / two-wheelers | Helmet + Plate Module |
| Image with traffic signs | Signboard Context Module |
| Unknown or unclear scene | Manual Review / Multi-module review |

Implemented in:

```text
src/adaptive_router.py
config/adaptive_router_config.json
```

---

## 11. Module 1: Helmet + Plate Evidence

This module detects riders and helmet compliance.

It generates:

- total rider count,
- helmet OK count,
- violation count,
- manual review count,
- rider-wise bounding boxes,
- helmet / no-helmet decision,
- plate information if reliable,
- JSON evidence report.

Output folders:

```text
outputs/helmet_plate/
outputs/final_best/helmet_plate_best/
outputs/FINAL_SHOWCASE/helmet_plate/
```

---

## 12. Module 2: Dedicated Number Plate + Safe OCR

ViolationIQ uses a separate number plate detector.

OCR is not forced.

```text
If OCR is reliable:
    Display plate number

If OCR is weak / partial / unreadable:
    Plate: UNREADABLE
    Action: Manual Review
```

This avoids false challans due to wrong plate reading.

The OCR system uses:

- plate crop extraction,
- crop enhancement,
- OCR reading,
- plate text cleaning,
- format validation,
- confidence threshold,
- manual-review fallback.

---

## 13. Module 3: Red-Light Video Evidence

This module works on video evidence.

It detects:

- traffic signal color,
- vehicle objects,
- virtual stop-line crossing,
- possible red-light violation,
- temporal multi-frame evidence.

Output folders:

```text
outputs/redlight/
outputs/final_best/redlight_best/
outputs/video/
outputs/FINAL_SHOWCASE/redlight/
```

Important enforcement rule:

> Final challan should not be generated from one frame only. Temporal voting and manual review are required.

---

## 14. Module 4: Signboard Context Evidence

This module detects traffic signs and generates context evidence.

Supported contexts:

- no entry,
- no stopping,
- stop sign,
- no left turn,
- no right turn,
- no u-turn,
- no overtaking,
- red / green signal context,

Output folders:

```text
outputs/signboard_context/
outputs/final_best/signboard_best/
outputs/FINAL_SHOWCASE/signboard_context/
```

Important:


---


## 15. Repository Structure

```text
ViolationIQ/
|-- README.md
|-- requirements.txt
|
|-- src/
|   |-- adaptive_router.py
|   |-- helmet_plate_module.py
|   |-- redlight_module.py
|   |-- signboard_context_module.py
|   |-- safety_utils.py
|
|-- config/
|   |-- adaptive_router_config.json
|   |-- camera_config.json
|
|-- architecture/
|   |-- violationiq_architecture.png
|   |-- architecture_mermaid.md
|
|-- reports/
|   |-- deliverable_matrix.json
|   |-- final_manifest.json
|   |-- implementation_notes.md
|
|-- outputs/
|   |-- FINAL_SHOWCASE/
|   |-- helmet_plate/
|   |-- redlight/
|   |-- signboard_context/
|   |-- video/
|
|-- models_info/
|-- demo/
```

---

## 16. How to Use This Repository

### Step 1: Clone the repository

```bash
git clone https://github.com/Hrithikcrick/ViolationIQ.git
cd ViolationIQ
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Check adaptive router demo

```bash
python demo/run_demo.py
```

### Step 4: View final outputs

Open:

```text
outputs/FINAL_SHOWCASE/
```

This folder contains best selected outputs for:

- helmet + plate evidence,
- signboard context evidence,
- red-light evidence,
- demo videos.

### Step 5: View reports

Open:

```text
reports/
```

Important files:

```text
reports/final_manifest.json
reports/deliverable_matrix.json
reports/implementation_notes.md
```

### Step 6: View architecture

Open:

```text
architecture/violationiq_architecture_main.png
architecture/architecture_mermaid.md
```

---

## 17. How to Reproduce the Same Pipeline

To reproduce this project from scratch:

1. Prepare datasets for helmet/rider, traffic signs, red-light video, and number plates.
2. Train or load YOLO models for traffic, helmet/rider, and number plate detection.
3. Use the adaptive router to select the correct module.
4. Run helmet + plate module for rider images.
5. Run red-light module for traffic signal videos.
6. Run signboard context module for traffic sign images.
8. Generate evidence images, JSON reports, CSV reports, and demo videos.
9. Select best outputs into `outputs/FINAL_SHOWCASE/`.
10. Use manual review for uncertain cases.

---

## 18. Model Weights

Model weights are not pushed directly to GitHub because they are large.

Required trained models:

```text
traffic_yolo11s_best.pt
helmet_yolo11s_best.pt
large_plate_yolo11s_best.pt
```

Recommended storage:

- Kaggle Model,
- Google Drive,
- GitHub Release,
- Hugging Face.

Update model paths in the runtime notebook or inference script before running inference.

---

## 19. Reports Generated

ViolationIQ generates structured outputs for review and analysis.

Report examples:

```text
reports/final_manifest.json
reports/deliverable_matrix.json
reports/implementation_notes.md
```

These reports help explain:

- which evidence was generated,
- which module was used,
- whether OCR was reliable,
- whether manual review is required,
- which outputs are selected for final demo.

---

## 20. Why This Project Is Different

ViolationIQ is not just a YOLO detection project.

It adds:

- adaptive expert routing,
- rider-wise evidence,
- safe OCR fallback,
- red-light temporal reasoning,
- signboard context reasoning,
- clean reports,
- final showcase packaging,
- safety-first decision logic.

This makes the project more practical for real traffic enforcement scenarios.

---

## 21. Safety and Ethics

ViolationIQ is a decision-support system, not an automatic punishment system.

It does not issue direct challans when:

- OCR is weak,
- plate is unreadable,
- signal is unclear,
- only single-frame evidence exists,
- camera calibration is missing,
- additional tracking or camera calibration is required.

Uncertain evidence is routed to:

```text
Manual Review
```

---

## 22. Final Deliverable Summary

This repository contains:

- source code,
- adaptive router,
- config files,
- architecture diagram,
- final showcase outputs,
- red-light demo video,
- helmet + plate evidence examples,
- signboard context examples,
- JSON / CSV reports,
- model documentation,
- implementation notes.

---

---

## 23. Project Report

The complete IEEE-style project report is available in the `reports/` folder.

| File | Link |
|---|---|
| LaTeX Source | [`reports/ViolationIQ_IEEE_Report.tex`](reports/ViolationIQ_IEEE_Report.tex) |
| Compiled PDF | [`reports/ViolationIQ_IEEE_Report.pdf`](reports/ViolationIQ_IEEE_Report.pdf) |

The report explains the full ViolationIQ approach, architecture, datasets, model results, implemented modules, evidence-generation pipeline, and safety/manual-review design.

---

## 24. Final Claim

**ViolationIQ is an adaptive multi-expert AI evidence copilot for traffic enforcement that produces clean, review-ready, safety-aware evidence for helmet violations, number plate evidence, red-light video evidence, and traffic sign context.**

It is designed to support enforcement teams with stronger evidence generation while reducing unsafe automatic decisions.

---

## Safe Plate OCR Evidence

ViolationIQ includes a dedicated number plate localization and safe OCR fallback module.

Final safe OCR snapshot:

```text
outputs/FINAL_SHOWCASE/plate_ocr/dedicated_plate_safe_ocr_snapshot.png
```

The system displays plate text only when OCR confidence and crop readability are reliable. If the OCR is weak, partial, or unreadable, the case is routed to manual review instead of forcing an incorrect plate number.
