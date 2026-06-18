import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

os.makedirs("architecture", exist_ok=True)

fig, ax = plt.subplots(figsize=(20, 12))
ax.set_xlim(0, 20)
ax.set_ylim(0, 12)
ax.axis("off")

def add_box(x, y, w, h, title, lines, color, edge):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.05,rounding_size=0.12",
        linewidth=2.2,
        edgecolor=edge,
        facecolor=color
    )
    ax.add_patch(box)

    ax.text(
        x + w / 2, y + h - 0.28,
        title,
        ha="center",
        va="top",
        fontsize=13,
        fontweight="bold",
        color="#111827"
    )

    yy = y + h - 0.72
    for line in lines:
        ax.text(
            x + 0.25, yy,
            line,
            ha="left",
            va="top",
            fontsize=10,
            color="#1f2937"
        )
        yy -= 0.31

def add_arrow(x1, y1, x2, y2):
    arrow = FancyArrowPatch(
        (x1, y1),
        (x2, y2),
        arrowstyle="->",
        mutation_scale=18,
        linewidth=2,
        color="#374151"
    )
    ax.add_patch(arrow)

ax.text(
    10, 11.55,
    "ViolationIQ: Adaptive Multi-Expert AI Evidence Copilot",
    ha="center",
    va="center",
    fontsize=24,
    fontweight="bold",
    color="#111827"
)

ax.text(
    10, 11.12,
    "Traffic violation evidence generation with routing, expert models, safety checks, and review-ready outputs",
    ha="center",
    va="center",
    fontsize=13,
    color="#4b5563"
)

add_box(
    7.5, 10.1, 5.0, 0.7,
    "Input Layer",
    ["Image / Video / CCTV Frame"],
    "#e0f2fe",
    "#0284c7"
)

add_box(
    6.8, 8.95, 6.4, 0.85,
    "Adaptive Multi-Expert Router",
    [
        "Detects input type and scene context",
        "Routes to the most suitable evidence module"
    ],
    "#fef3c7",
    "#d97706"
)

add_arrow(10, 10.1, 10, 9.8)

add_box(
    0.6, 6.95, 4.1, 1.35,
    "Helmet + Rider Expert",
    [
        "Rider detection",
        "Helmet / no-helmet status",
        "Rider-wise panel: R1, R2, R3"
    ],
    "#dcfce7",
    "#16a34a"
)

add_box(
    5.3, 6.95, 4.1, 1.35,
    "Number Plate Expert",
    [
        "Dedicated plate detection",
        "Plate crop extraction",
        "OCR only when reliable"
    ],
    "#ede9fe",
    "#7c3aed"
)

add_box(
    10.0, 6.95, 4.1, 1.35,
    "Red-Light Video Expert",
    [
        "Signal color detection",
        "Virtual stop-line crossing",
        "Temporal multi-frame evidence"
    ],
    "#fee2e2",
    "#dc2626"
)

add_box(
    14.7, 6.95, 4.1, 1.35,
    "Signboard Context Expert",
    [
        "No-entry / no-stopping",
        "Stop / turn restriction signs",
        "Speed-limit context"
    ],
    "#e0e7ff",
    "#4f46e5"
)

add_arrow(8.6, 8.95, 2.65, 8.3)
add_arrow(9.4, 8.95, 7.35, 8.3)
add_arrow(10.6, 8.95, 12.05, 8.3)
add_arrow(11.4, 8.95, 16.75, 8.3)

add_box(
    14.7, 5.35, 4.1, 1.05,
    "Speed Estimation Prototype",
    [
        "Vehicle tracking across frames",
        "Pixel displacement based speed demo",
        "Calibration required for enforcement"
    ],
    "#fce7f3",
    "#db2777"
)

add_arrow(16.75, 6.95, 16.75, 6.4)

add_box(
    3.2, 4.15, 13.6, 1.05,
    "Evidence Reasoning Layer",
    [
        "Helmet compliance  |  Plate OCR reliability  |  Signal + stop-line crossing",
        "Signboard context reasoning  |  Temporal voting  |  Speed prototype reasoning"
    ],
    "#f3f4f6",
    "#374151"
)

add_arrow(2.65, 6.95, 5.0, 5.2)
add_arrow(7.35, 6.95, 7.7, 5.2)
add_arrow(12.05, 6.95, 12.0, 5.2)
add_arrow(16.75, 6.95, 14.8, 5.2)
add_arrow(16.75, 5.35, 14.8, 5.2)

add_box(
    3.2, 2.72, 13.6, 0.95,
    "Safety Layer",
    [
        "No forced OCR  |  Manual review fallback  |  Camera calibration warning",
        "No unsafe automatic challan generation"
    ],
    "#fff7ed",
    "#ea580c"
)

add_arrow(10, 4.15, 10, 3.67)

add_box(
    3.2, 1.22, 13.6, 1.0,
    "Final Outputs",
    [
        "Clean evidence panels  |  JSON / CSV reports  |  Final showcase images",
        "Red-light demo video  |  Speed-estimation demo video"
    ],
    "#ecfeff",
    "#0891b2"
)

add_arrow(10, 2.72, 10, 2.22)

add_box(
    0.6, 1.22, 2.05, 2.45,
    "Model Stack",
    [
        "YOLO11s",
        "EasyOCR",
        "OpenCV",
        "Rule Logic",
        "Temporal Voting"
    ],
    "#f8fafc",
    "#64748b"
)

add_box(
    17.25, 1.22, 1.55, 2.45,
    "Review",
    [
        "No blind",
        "challan",
        "",
        "Weak cases",
        "go to",
        "manual review"
    ],
    "#f8fafc",
    "#64748b"
)

ax.text(
    10, 0.45,
    "Repository outputs: outputs/FINAL_SHOWCASE/  |  Reports: reports/  |  Architecture: architecture/",
    ha="center",
    va="center",
    fontsize=11,
    color="#4b5563"
)

plt.tight_layout()

png_path = "architecture/violationiq_architecture.png"
svg_path = "architecture/violationiq_architecture.svg"

plt.savefig(png_path, dpi=300, bbox_inches="tight")
plt.savefig(svg_path, bbox_inches="tight")
plt.close()

print("Professional architecture diagram saved:")
print(png_path)
print(svg_path)
