# Source Code

This folder contains the reusable ViolationIQ modules.

| File | Role |
|---|---|
| adaptive_router.py | Routes image/video input to the correct module |
| helmet_plate_module.py | Rider-wise helmet evidence and plate crop safety |
| redlight_module.py | Red-light video evidence logic |
| signboard_context_module.py | Traffic sign context logic |
| safety_utils.py | OCR validation, quality checks, NMS helpers |

The code can produce outputs when trained YOLO weights are provided at runtime.
