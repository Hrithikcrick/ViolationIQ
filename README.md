# 🚦 ViolationIQ: Adaptive Multi-Expert AI Evidence Copilot for Traffic Enforcement

<p align="center">
  <b>Safety-first AI framework for traffic violation evidence generation</b><br>
  Helmet Detection • Number Plate Evidence • Red-Light Video Evidence • Signboard Context • Speed Estimation Prototype
</p>

<p align="center">
  <b>Built for automated photo/video-based traffic violation identification using Computer Vision</b>
</p>

---

## 1. Project Overview

**ViolationIQ** is an adaptive computer-vision based traffic enforcement evidence system.

The goal of this project is not to blindly generate challans. Instead, ViolationIQ works as an **AI Evidence Copilot** that detects possible traffic violations, prepares clean review-ready evidence, attaches number plate information only when reliable, and sends uncertain cases to manual review.

The system is designed for real-world traffic scenes where false challans can happen because of blurry images, wrong OCR, unclear traffic signs, poor lighting, occlusion, and camera-specific road geometry.

---

## 2. Problem Statement Alignment

This project is aligned with:

> **Automated Photo Identification and Classification for Traffic Violations Using Computer Vision**

The system focuses on traffic violation evidence generation from images and videos, including helmet violation detection, rider-wise evidence, number plate detection, safe OCR, red-light video evidence, signboard context detection, speed-estimation prototype, structured reports, and final showcase outputs.

---

## 3. Motivation

Traffic enforcement using cameras is challenging because:

- Number plates can be small, blurred, tilted, or partially visible.
- OCR can produce wrong or incomplete plate numbers.
- A single image may show a speed-limit sign, but cannot prove overspeeding.
- Red-light violation needs temporal evidence, not only one frame.
- Wrong-side driving and illegal parking require tracking over time.
- Real CCTV cameras need calibration for stop-lines, signal ROI, direction, zones, and speed estimation.
- A wrong automatic challan can reduce public trust.

Therefore, ViolationIQ uses a **multi-expert, safety-first architecture** instead of a single detector.

---

## 4. Final Project Outcome

ViolationIQ delivers a complete prototype package containing:

| Output | Description |
|---|---|
| Helmet evidence panels | Rider-wise helmet / no-helmet detection outputs |
| Plate evidence | Dedicated number plate detection with safe OCR |
| Red-light evidence | Signal color + vehicle crossing virtual stop-line |
| Signboard context evidence | No-entry, no-stopping, stop sign, turn restriction, speed-limit context |
| Speed estimation prototype | Vehicle speed estimation demo from video with calibration warning |
| Adaptive router | Routes image/video input to the correct module |
| Reports | JSON and CSV evidence reports |
| Architecture | Visual and Mermaid architecture diagrams |
| Final showcase | Best selected outputs for demo and GitHub |
| Source code | Modular source code inside `src/` |

Final selected outputs are available in:

```text
outputs/FINAL_SHOWCASE/

Key Deliverables

| No. | Deliverable                              | Status                  | Description                                                                                                       |
| --- | ---------------------------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 1   | Adaptive Multi-Expert Router             | Implemented             | Routes input to the correct module based on image/video type and detected scene context.                          |
| 2   | Helmet + Rider Detection                 | Implemented             | Detects riders and classifies helmet compliance in rider-wise format.                                             |
| 3   | Rider-wise Evidence Generation           | Implemented             | Generates R1, R2, R3 style evidence panels with rider-specific status.                                            |
| 4   | Dedicated Number Plate Detection         | Implemented             | Uses a separate trained plate detector for plate localization.                                                    |
| 5   | Safe OCR / ANPR Pipeline                 | Implemented with safety | Displays plate number only when OCR is reliable; otherwise marks it as manual review.                             |
| 6   | Red-Light Video Evidence Module          | Implemented             | Detects signal color, vehicles, virtual stop-line crossing, and temporal evidence.                                |
| 7   | Signboard Context Module                 | Implemented             | Detects traffic signs such as no-entry, no-stopping, stop sign, speed-limit, and turn restriction signs.          |
| 8   | Speed Estimation Prototype               | Prototype               | Tracks vehicles across frames and estimates speed as a calibration-dependent demo.                                |
| 9   | Final Showcase Outputs                   | Implemented             | Stores best selected images and videos inside `outputs/FINAL_SHOWCASE/` for demo and GitHub presentation.         |
| 10  | Reports, Architecture, and Documentation | Implemented             | Includes JSON/CSV reports, architecture diagram, Mermaid diagram, README, config files, and implementation notes.

 |
Architecture Diagram

Input Image / Video
        |
        v
Adaptive Router
        |
        |-- Helmet + Plate Module
        |-- Red-Light Video Module
        |-- Signboard Context Module
        |-- Speed Estimation Prototype
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




| Violation Type               | Why separate handling is needed                                         |
| ---------------------------- | ----------------------------------------------------------------------- |
| Helmet violation             | Needs rider-wise association between rider and helmet/face.             |
| Number plate                 | Needs dedicated plate localization and OCR validation.                  |
| Red-light violation          | Needs video, signal color, stop-line, and temporal voting.              |
| Signboard violation context  | Needs traffic sign detection and rule-based context reasoning.          |
| Speed violation              | Needs tracking and real-world camera calibration.                       |
| Wrong-side / illegal parking | Needs temporal tracking and camera-specific zone/direction calibration. |
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
        |-- Speed Estimation Prototype
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
| Speed estimation framework     |
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

| Expert          | Model / Method   | Purpose                                          |
| --------------- | ---------------- | ------------------------------------------------ |
| Traffic Expert  | YOLO11s          | Vehicles, signs, traffic lights                  |
| Helmet Expert   | YOLO11s          | Rider, helmet, no-helmet, bad helmet             |
| Plate Expert    | YOLO11s          | Number plate localization                        |
| OCR             | EasyOCR          | Plate text reading                               |
| Reasoning Layer | Rule-based logic | Manual review, temporal voting, context decision |

Repository Structure

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
|   |-- speed_estimation_note.json
|
|-- outputs/
|   |-- FINAL_SHOWCASE/
|   |-- helmet_plate/
|   |-- redlight/
|   |-- signboard_context/
|   |-- speed_estimation_demo/
|   |-- video/
|
|-- models_info/
|-- demo/

How to Use This Repository


Step 1: Clone the repository
git clone https://github.com/Hrithikcrick/ViolationIQ.git
cd ViolationIQ
Step 2: Install dependencies
pip install -r requirements.txt
Step 3: Check adaptive router demo
python demo/run_demo.py
Step 4: View final outputs

Open:

outputs/FINAL_SHOWCASE/

This folder contains best selected outputs for:

Helmet + plate evidence
Signboard context evidence
Red-light evidence
Speed estimation prototype
Demo videos

View reports

Open:

reports/

Important files:

reports/final_manifest.json
reports/deliverable_matrix.json
reports/implementation_notes.md
reports/speed_estimation_note.json

. How to Reproduce the Same Pipeline

To reproduce this project from scratch:

Prepare datasets for helmet/rider, traffic signs, red-light video, and number plates.
Train or load YOLO models for traffic, helmet/rider, and number plate detection.
Use the adaptive router to select the correct module.
Run helmet + plate module for rider images.
Run red-light module for traffic signal videos.
Run signboard context module for traffic sign images.
Run speed-estimation prototype only when video is available.
Generate evidence images, JSON reports, CSV reports, and demo videos.
Select best outputs into outputs/FINAL_SHOWCASE/.
Use manual review for uncertain cases.