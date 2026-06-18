import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

os.makedirs("architecture", exist_ok=True)

def add_box(ax, x, y, w, h, title, lines, face, edge, title_size=14, text_size=10):
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.03,rounding_size=0.08",
        linewidth=2,
        edgecolor=edge,
        facecolor=face
    )
    ax.add_patch(rect)

    ax.text(
        x + w/2, y + h - 0.18,
        title,
        ha="center", va="top",
        fontsize=title_size, fontweight="bold",
        color="#111827"
    )

    yy = y + h - 0.52
    for line in lines:
        ax.text(
            x + 0.18, yy,
            line,
            ha="left", va="top",
            fontsize=text_size,
            color="#374151"
        )
        yy -= 0.22

def add_arrow(ax, x1, y1, x2, y2, color="#374151", lw=1.8):
    arr = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="->",
        mutation_scale=15,
        linewidth=lw,
        color=color
    )
    ax.add_patch(arr)

# =========================================================
# 1) CLEAN MAIN ARCHITECTURE
# =========================================================
fig, ax = plt.subplots(figsize=(16, 10))
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
ax.axis("off")

ax.text(
    8, 9.65,
    "ViolationIQ Architecture",
    ha="center", va="center",
    fontsize=24, fontweight="bold", color="#111827"
)

ax.text(
    8, 9.3,
    "Adaptive Multi-Expert AI Evidence Copilot for Traffic Enforcement",
    ha="center", va="center",
    fontsize=12, color="#4b5563"
)

add_box(ax, 5.3, 8.35, 5.4, 0.7, "Input Layer",
        ["Image / Video / CCTV Frame"], "#e0f2fe", "#0284c7", 13, 10)

add_box(ax, 4.5, 7.2, 7.0, 0.85, "Adaptive Multi-Expert Router",
        ["Routes the input to the most suitable module"], "#fef3c7", "#d97706", 14, 10)

add_arrow(ax, 8, 8.35, 8, 8.02)
add_arrow(ax, 8, 7.2, 2.55, 6.7)
add_arrow(ax, 8, 7.2, 5.85, 6.7)
add_arrow(ax, 8, 7.2, 10.15, 6.7)
add_arrow(ax, 8, 7.2, 13.45, 6.7)

add_box(ax, 0.6, 5.6, 3.9, 1.0, "Helmet + Rider Expert",
        ["Rider detection", "Helmet / no-helmet decision"], "#dcfce7", "#16a34a", 13, 10)

add_box(ax, 4.9, 5.6, 3.9, 1.0, "Number Plate Expert",
        ["Dedicated plate detection", "Plate crop + OCR validation"], "#ede9fe", "#7c3aed", 13, 10)

add_box(ax, 9.2, 5.6, 3.9, 1.0, "Red-Light Video Expert",
        ["Signal status", "Stop-line crossing evidence"], "#fee2e2", "#dc2626", 13, 10)

add_box(ax, 12.0, 4.35, 3.4, 1.0, "Signboard Context Expert",
        ["No-entry / stop / turn signs", "Speed-limit context"], "#e0e7ff", "#4f46e5", 12, 9)

add_box(ax, 12.0, 5.6, 3.4, 1.0, "Speed Estimation Prototype",
        ["Tracking-based speed demo", "Calibration-dependent"], "#fce7f3", "#db2777", 12, 9)

add_arrow(ax, 2.55, 5.6, 5.9, 4.55)
add_arrow(ax, 6.85, 5.6, 7.0, 4.55)
add_arrow(ax, 11.15, 5.6, 8.1, 4.55)
add_arrow(ax, 13.7, 5.35, 8.9, 4.55)
add_arrow(ax, 13.7, 4.35, 9.8, 4.55)

add_box(ax, 3.7, 3.5, 8.6, 0.85, "Evidence Reasoning Layer",
        ["Combines vision outputs into structured, review-ready evidence"], "#f3f4f6", "#4b5563", 14, 10)

add_arrow(ax, 8, 3.5, 8, 3.05)

add_box(ax, 3.7, 2.2, 8.6, 0.85, "Safety Layer",
        ["No forced OCR  |  Manual review fallback  |  No unsafe automatic challan"], "#fff7ed", "#ea580c", 14, 10)

add_arrow(ax, 8, 2.2, 8, 1.75)

add_box(ax, 3.2, 0.65, 9.6, 0.95, "Final Outputs",
        ["Evidence panels  |  JSON / CSV reports  |  Demo images / videos  |  Final showcase"], "#ecfeff", "#0891b2", 14, 10)

plt.tight_layout()
plt.savefig("architecture/violationiq_architecture.png", dpi=300, bbox_inches="tight")
plt.savefig("architecture/violationiq_architecture.svg", bbox_inches="tight")
plt.close()

# =========================================================
# 2) EXPLAINED ARCHITECTURE
# =========================================================
fig, ax = plt.subplots(figsize=(18, 12))
ax.set_xlim(0, 18)
ax.set_ylim(0, 12)
ax.axis("off")

ax.text(
    9, 11.55,
    "ViolationIQ Explained Architecture",
    ha="center", va="center",
    fontsize=25, fontweight="bold", color="#111827"
)

ax.text(
    9, 11.15,
    "Detailed system flow, expert modules, safety policy, and deliverable outputs",
    ha="center", va="center",
    fontsize=12, color="#4b5563"
)

add_box(ax, 6.4, 10.0, 5.2, 0.8, "1. Input Layer",
        ["Accepts image, video, CCTV frame, or demo traffic input"], "#e0f2fe", "#0284c7", 14, 10)

add_box(ax, 5.4, 8.8, 7.2, 0.95, "2. Adaptive Multi-Expert Router",
        [
            "Checks whether the input is rider-centric, signal/video-centric, sign-centric, or unclear",
            "Then routes it to the best module instead of forcing one model everywhere"
        ], "#fef3c7", "#d97706", 14, 9)

add_arrow(ax, 9, 10.0, 9, 9.75)

add_box(ax, 0.6, 7.1, 4.0, 1.4, "3A. Helmet + Rider Module",
        [
            "Detects riders in two-wheeler scenes",
            "Checks helmet compliance",
            "Builds rider-wise evidence panels like R1, R2, R3"
        ], "#dcfce7", "#16a34a", 13, 9)

add_box(ax, 4.9, 7.1, 4.0, 1.4, "3B. Number Plate Module",
        [
            "Uses a dedicated trained plate detector",
            "Extracts plate crop",
            "Runs OCR only when the plate is readable enough"
        ], "#ede9fe", "#7c3aed", 13, 9)

add_box(ax, 9.2, 7.1, 4.0, 1.4, "3C. Red-Light Video Module",
        [
            "Detects signal color",
            "Uses virtual stop-line crossing",
            "Supports temporal multi-frame reasoning"
        ], "#fee2e2", "#dc2626", 13, 9)

add_box(ax, 13.5, 7.1, 3.9, 1.4, "3D. Signboard Context Module",
        [
            "Detects no-entry, stop, turn restriction, and speed-limit signs",
            "Provides enforcement context instead of unsafe overclaiming"
        ], "#e0e7ff", "#4f46e5", 12, 9)

add_arrow(ax, 9, 8.8, 2.6, 8.5)
add_arrow(ax, 9, 8.8, 6.9, 8.5)
add_arrow(ax, 9, 8.8, 11.2, 8.5)
add_arrow(ax, 9, 8.8, 15.4, 8.5)

add_box(ax, 13.5, 5.55, 3.9, 1.1, "3E. Speed Estimation Prototype",
        [
            "Tracks vehicle motion across frames",
            "Prototype only; real deployment needs calibration"
        ], "#fce7f3", "#db2777", 12, 9)

add_arrow(ax, 15.4, 7.1, 15.4, 6.65)

add_box(ax, 3.1, 4.25, 11.8, 1.0, "4. Evidence Reasoning Layer",
        [
            "Combines module outputs into structured decisions:",
            "helmet status, safe OCR decision, stop-line crossing evidence, sign context, and temporal voting"
        ], "#f3f4f6", "#4b5563", 14, 9)

add_arrow(ax, 2.6, 7.1, 5.1, 5.25)
add_arrow(ax, 6.9, 7.1, 6.9, 5.25)
add_arrow(ax, 11.2, 7.1, 9.2, 5.25)
add_arrow(ax, 15.4, 7.1, 12.4, 5.25)
add_arrow(ax, 15.4, 5.55, 13.2, 5.25)

add_box(ax, 3.1, 2.8, 11.8, 1.0, "5. Safety Layer",
        [
            "No forced OCR  |  Weak evidence -> manual review  |  No blind challan generation",
            "Calibration warning for speed-related claims"
        ], "#fff7ed", "#ea580c", 14, 9)

add_arrow(ax, 9, 4.25, 9, 3.8)

add_box(ax, 3.1, 1.2, 11.8, 1.1, "6. Final Deliverables",
        [
            "Clean evidence panels, best selected outputs, demo images, demo video, JSON/CSV reports, and GitHub-ready project structure"
        ], "#ecfeff", "#0891b2", 14, 9)

add_arrow(ax, 9, 2.8, 9, 2.3)

add_box(ax, 0.7, 1.2, 1.8, 2.6, "Model Stack",
        ["YOLO11s", "EasyOCR", "OpenCV", "Python", "Rule Logic"], "#f8fafc", "#64748b", 12, 10)

add_box(ax, 15.3, 1.2, 2.0, 2.6, "Manual Review Policy",
        ["Unreadable plate", "Weak OCR", "Unclear signal", "Tracking-dependent cases"], "#f8fafc", "#64748b", 12, 10)

ax.text(
    9, 0.45,
    "Recommended README image: architecture/violationiq_architecture.png   |   Detailed reference: architecture/violationiq_architecture_explained.png",
    ha="center", va="center",
    fontsize=11, color="#4b5563"
)

plt.tight_layout()
plt.savefig("architecture/violationiq_architecture_explained.png", dpi=300, bbox_inches="tight")
plt.savefig("architecture/violationiq_architecture_explained.svg", bbox_inches="tight")
plt.close()

print("Generated:")
print("architecture/violationiq_architecture.png")
print("architecture/violationiq_architecture.svg")
print("architecture/violationiq_architecture_explained.png")
print("architecture/violationiq_architecture_explained.svg")
