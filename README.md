# ViolationIQ: Adaptive Multi-Expert AI Evidence Copilot for Traffic Enforcement

ViolationIQ is an adaptive AI evidence copilot for traffic enforcement. It detects possible traffic violations from images and videos, generates clean review-ready evidence, and avoids false challans by using manual review and safety checks.

## One-Line Pitch

ViolationIQ is not a blind challan generator. It is a multi-expert AI evidence copilot that detects traffic violations, validates evidence quality, links plate information only when reliable, and sends uncertain cases to manual review.

## Core Architecture

Input Image / Video
        |
        v
Adaptive Router
        |
        |-- Helmet + Rider Expert
        |-- Number Plate Expert
        |-- Traffic Sign / Signal Expert
        |-- Red-Light Video Expert
        |
        v
Evidence Reasoning Layer
        |
        |-- Helmet decision
        |-- Safe plate OCR
        |-- Signboard context
        |-- Red signal + stop-line crossing
        |
        v
Safety Layer
        |
        |-- Manual review fallback
        |-- Temporal voting
        |-- No forced OCR
        |-- Camera calibration
        |
        v
Clean Evidence Panel + JSON/CSV Report

## Main Modules

### 1. Helmet + Rider Evidence Module

- Detects riders
- Detects helmet compliance
- Produces clean rider-wise evidence panel
- Generates JSON report
- Links number plate evidence when reliable

### 2. Dedicated Number Plate Module

- Uses separate YOLO plate detector
- Crops detected plate
- Applies OCR only after readability checks
- Displays plate number only when reliable
- Routes weak OCR cases to manual review

### 3. Red-Light Video Module

- Detects traffic signal color
- Detects vehicles
- Uses virtual stop-line crossing
- Uses temporal multi-frame voting
- Generates evidence frames and demo video

### 4. Signboard Context Module

- Detects traffic signs such as no-entry, no-stopping, stop sign, red light, green light, speed limit, no u-turn, no left turn, no right turn
- Produces context evidence
- Routes tracking-dependent cases to manual review

## Adaptive Router

| Input / Context | Selected Module |
|---|---|
| Video input | Red-light video module |
| Rider / helmet / two-wheeler scene | Helmet + plate module |
| Traffic sign scene | Signboard context module |
| Unclear scene | Multi-module review / manual review |

## Model Summary

| Module | Model | Purpose |
|---|---|---|
| Traffic Expert | YOLO11s | Vehicles, signs, traffic lights, traffic context |
| Helmet Expert | YOLO11s | Rider, helmet, no-helmet, bad helmet |
| Plate Expert | YOLO11s | Number plate localization |

Known experimental results:

- Traffic model mAP50 around 0.928
- Helmet/rider model mAP50 around 0.701
- Plate model fine-tuned on 10,125-image plate dataset

## Deliverable Status

| Feature | Status |
|---|---|
| Helmet violation detection | Implemented |
| Rider-wise evidence | Implemented |
| Number plate detection | Implemented |
| Safe plate OCR | Implemented with manual review fallback |
| Red-light video evidence | Implemented |
| Signboard context detection | Implemented |
| No-entry context | Implemented as context/manual review |
| No-stopping context | Implemented as context/manual review |
| Speed-limit violation | Framework only; needs speed tracking |
| Wrong-side driving | Framework only; needs direction tracking |
| Illegal parking | Framework only; needs duration tracking |
| Seatbelt violation | Not implemented; needs cabin-view dataset |
| Triple riding | Not reliable yet; needs stronger rider/person dataset |

## Safety Policy

ViolationIQ does not automatically issue challans when evidence is weak.

It sends cases to manual review when:

- OCR is weak
- Plate is unreadable
- Signal is unclear
- Only single-frame evidence exists
- Camera calibration is missing
- Violation needs duration or direction tracking

## Repository Structure

ViolationIQ/
|-- README.md
|-- requirements.txt
|-- src/
|   |-- adaptive_router.py
|   |-- helmet_plate_module.py
|   |-- redlight_module.py
|   |-- signboard_context_module.py
|   |-- safety_utils.py
|-- config/
|-- architecture/
|-- reports/
|-- outputs/
|   |-- helmet_plate/
|   |-- redlight/
|   |-- signboard_context/
|   |-- video/
|-- models_info/
|-- demo/

## Final Message

ViolationIQ is built as a practical enforcement-support system, not an unsafe automation system. It combines computer vision, OCR, temporal reasoning, and manual review to generate reliable traffic violation evidence.

## Speed Estimation Prototype

ViolationIQ includes a demo speed-estimation prototype for video. It tracks detected vehicles across frames and estimates speed from pixel displacement.

Important:
This is not used for final challan unless camera calibration is available.

Real deployment requires:
- camera calibration
- pixel-to-meter mapping
- homography / perspective correction
- lane-wise tracking
- timestamp/FPS verification

So speed-limit sign detection is treated as context evidence, while speed violation enforcement is calibration-dependent.

## Final Showcase

The final selected outputs are stored in:

```text
outputs/FINAL_SHOWCASE/
```

This folder contains the best selected examples for:

- Helmet + plate evidence
- Signboard context evidence
- Red-light vehicle crossing evidence
- Speed estimation prototype
- Demo videos

## Final Safety Statement

ViolationIQ is an evidence copilot, not a blind challan generator.
It supports traffic enforcement teams by producing clear evidence panels and structured reports while keeping manual review for uncertain cases.
