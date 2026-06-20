# Implementation Notes

## Fully Implemented

1. Helmet + plate evidence pipeline
2. Safe plate OCR policy
3. Red-light video evidence pipeline
4. Signboard context pipeline
5. Adaptive router design
6. Clean visual evidence outputs
7. JSON/CSV reports

## Framework / Future Extensions

1. Wrong-side driving needs object tracking and camera-wise road direction calibration.
2. Illegal parking needs zone calibration and vehicle duration tracking.
4. Seatbelt needs cabin/interior dataset.
5. Triple riding needs stronger multi-person rider dataset.

## Safety Choice

The project is intentionally designed as an evidence copilot, not a blind challan generator.
Uncertain cases are routed to manual review.
