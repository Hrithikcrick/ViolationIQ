# ViolationIQ Final Architecture

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

ViolationIQ does not generate automatic challans.
Weak OCR, unclear detections, and ambiguous evidence are routed to manual review.
