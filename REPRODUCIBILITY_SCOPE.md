# ViolationIQ Reproducibility Scope

This repository reproduces the final inference/demo deliverables of ViolationIQ using the provided trained weights and sample input files.

## Reproduced by Judge Script

Running the judge reproduction command generates:

- helmet and rider evidence outputs
- rider-wise helmet/no-helmet JSON reports
- number plate localization and safe OCR/manual-review structure
- signboard context reports
- signboard context reports
- final showcase index CSV
- reproduction summary JSON

## Required External Assets

The trained model weights and sample inputs are provided separately through the Google Drive asset zip:

https://drive.google.com/file/d/1XeJq1Afzw0hjd1gdzt1pjwlz6GvF4J2f/view?usp=sharing

These files are not committed to GitHub because model weights and videos are large.

## Important Clarification

The judge reproduction script reproduces final outputs and deliverables, not full model retraining.

The reported training metrics such as traffic YOLO11s mAP50 around 0.928, helmet/rider mAP50 around 0.701, and plate model mAP50 around 0.924 were obtained during Kaggle training and are documented in the project report.

To reproduce training metrics from scratch, the original Kaggle datasets, training notebook, GPU environment, and full training commands are required.

