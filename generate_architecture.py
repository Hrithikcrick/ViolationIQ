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
        x + w/2, y + h - 0.14,
        title,
        ha="center", va="top",
        fontsize=title_size, fontweight="bold",
        color="#111827"
    )

    yy = y + h - 0.42
    for line in lines:
        ax.text(
            x + 0.14, yy,
            line,
            ha="left", va="top",
            fontsize=text_size,
            color="#374151"
        )
        yy -= 0.18

def add_arrow(ax, x1, y1, x2, y2, color="#374151", lw=1.8):
    arr = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="->",
        mutation_scale=14,
        linewidth=lw,
        color=color
    )
    ax.add_patch(arr)

# =========================================================
# MAIN ARCHITECTURE IMAGE
# =========================================================
fig, ax = plt.subplots(figsize=(15, 9))
ax.set_xlim(0, 15)
ax.set_ylim(0, 9)
ax.axis("off")

ax.text(7.5, 8.6, "ViolationIQ Architecture", ha="center", va="center",
        fontsize=24, fontweight="bold", color="#111827")
ax.text(7.5, 8.25, "Adaptive Multi-Expert AI Evidence Copilot for Traffic Enforcement",
        ha="center", va="center", fontsize=12, color="#4b5563")

add_box(ax, 5.0, 7.3, 5.0, 0.7, "Input Layer",
        ["Image / Video / CCTV Frame"], "#e0f2fe", "#0284c7", 13, 10)

add_box(ax, 4.1, 6.15, 6.8, 0.8, "Adaptive Multi-Expert Router",
        ["Routes each input to the most suitable evidence module"], "#fef3c7", "#d97706", 14, 10)

add_arrow(ax, 7.5, 7.3, 7.5, 6.95)

add_box(ax, 0.7, 4.9, 3.2, 1.0, "Helmet + Rider Expert",
        ["Rider detection", "Helmet / no-helmet status"], "#dcfce7", "#16a34a", 13, 10)

add_box(ax, 4.2, 4.9, 3.2, 1.0, "Number Plate Expert",
        ["Plate detection", "OCR only when reliable"], "#ede9fe", "#7c3aed", 13, 10)

add_box(ax, 7.8, 4.9, 3.2, 1.0, "Red-Light Video Expert",
        ["Signal status", "Stop-line crossing"], "#fee2e2", "#dc2626", 13, 10)

add_box(ax, 11.2, 4.9, 3.1, 1.0, "Signboard Context Expert",
        ["Traffic sign context", "No unsafe overclaiming"], "#e0e7ff", "#4f46e5", 12, 9)

add_box(ax, 11.2, 3.65, 3.1, 0.9, "Speed Prototype",
        ["Tracking demo only", "Needs calibration"], "#fce7f3", "#db2777", 12, 9)

add_arrow(ax, 7.5, 6.15, 2.3, 5.9)
add_arrow(ax, 7.5, 6.15, 5.8, 5.9)
add_arrow(ax, 7.5, 6.15, 9.4, 5.9)
add_arrow(ax, 7.5, 6.15, 12.75, 5.9)

add_box(ax, 3.0, 2.55, 9.0, 0.9, "Evidence Reasoning Layer",
        ["Combines module outputs into structured, review-ready evidence"], "#f3f4f6", "#4b5563", 14, 10)

add_arrow(ax, 2.3, 4.9, 5.2, 3.45)
add_arrow(ax, 5.8, 4.9, 6.5, 3.45)
add_arrow(ax, 9.4, 4.9, 8.0, 3.45)
add_arrow(ax, 12.75, 4.9, 9.6, 3.45)
add_arrow(ax, 12.75, 3.65, 9.8, 3.45)

add_box(ax, 3.0, 1.35, 9.0, 0.8, "Safety Layer",
        ["No forced OCR  |  Manual review fallback  |  No blind challan"], "#fff7ed", "#ea580c", 14, 10)

add_arrow(ax, 7.5, 2.55, 7.5, 2.15)

add_box(ax, 2.5, 0.25, 10.0, 0.8, "Final Outputs",
        ["Evidence panels  |  JSON / CSV reports  |  Demo images / videos  |  Final showcase"], "#ecfeff", "#0891b2", 14, 10)

add_arrow(ax, 7.5, 1.35, 7.5, 1.05)

plt.tight_layout()
plt.savefig("architecture/violationiq_architecture_main.png", dpi=300, bbox_inches="tight")
plt.close()

# =========================================================
# EXPLAINED ARCHITECTURE IMAGE
# =========================================================
fig, ax = plt.subplots(figsize=(16, 11))
ax.set_xlim(0, 16)
ax.set_ylim(0, 11)
ax.axis("off")

ax.text(8, 10.55, "ViolationIQ Explained Architecture", ha="center", va="center",
        fontsize=24, fontweight="bold", color="#111827")
ax.text(8, 10.2, "Detailed module flow, safety logic, and project deliverables",
        ha="center", va="center", fontsize=12, color="#4b5563")

add_box(ax, 5.4, 9.2, 5.2, 0.75, "1. Input Layer",
        ["Accepts image, video, CCTV frame, or demo traffic input"], "#e0f2fe", "#0284c7", 14, 10)

add_box(ax, 4.5, 8.0, 7.0, 0.95, "2. Adaptive Multi-Expert Router",
        [
            "Checks scene type and input context",
            "Routes input to the correct module instead of forcing one model everywhere"
        ], "#fef3c7", "#d97706", 14, 9)

add_arrow(ax, 8, 9.2, 8, 8.95)

add_box(ax, 0.6, 6.3, 3.6, 1.2, "3A. Helmet + Rider Module",
        [
            "Detects riders",
            "Checks helmet compliance",
            "Creates rider-wise evidence panels"
        ], "#dcfce7", "#16a34a", 13, 9)

add_box(ax, 4.5, 6.3, 3.6, 1.2, "3B. Number Plate Module",
        [
            "Dedicated number plate detector",
            "Plate crop extraction",
            "OCR only when readable"
        ], "#ede9fe", "#7c3aed", 13, 9)

add_box(ax, 8.4, 6.3, 3.6, 1.2, "3C. Red-Light Video Module",
        [
            "Traffic light status detection",
            "Virtual stop-line crossing",
            "Temporal voting"
        ], "#fee2e2", "#dc2626", 13, 9)

add_box(ax, 12.3, 6.3, 3.1, 1.2, "3D. Signboard Context Module",
        [
            "No-entry / stop / turn signs",
            "Speed-limit context"
        ], "#e0e7ff", "#4f46e5", 12, 9)

add_box(ax, 12.3, 5.0, 3.1, 0.95, "3E. Speed Estimation Prototype",
        [
            "Tracking-based speed demo",
            "Calibration required for enforcement"
        ], "#fce7f3", "#db2777", 12, 9)

add_arrow(ax, 8, 8.0, 2.4, 7.5)
add_arrow(ax, 8, 8.0, 6.3, 7.5)
add_arrow(ax, 8, 8.0, 10.2, 7.5)
add_arrow(ax, 8, 8.0, 13.85, 7.5)

add_box(ax, 2.6, 3.8, 10.8, 0.95, "4. Evidence Reasoning Layer",
        [
            "Combines helmet evidence, safe OCR decisions, red-light reasoning, signboard context, and speed prototype outputs"
        ], "#f3f4f6", "#4b5563", 14, 9)

add_arrow(ax, 2.4, 6.3, 5.0, 4.75)
add_arrow(ax, 6.3, 6.3, 6.4, 4.75)
add_arrow(ax, 10.2, 6.3, 8.2, 4.75)
add_arrow(ax, 13.85, 6.3, 10.3, 4.75)
add_arrow(ax, 13.85, 5.0, 11.2, 4.75)

add_box(ax, 2.6, 2.35, 10.8, 0.95, "5. Safety Layer",
        [
            "No forced OCR  |  Weak evidence -> manual review  |  No unsafe automatic challan generation"
        ], "#fff7ed", "#ea580c", 14, 9)

add_arrow(ax, 8, 3.8, 8, 3.3)

add_box(ax, 2.6, 0.9, 10.8, 1.0, "6. Final Deliverables",
        [
            "Evidence panels, selected best outputs, reports, demo images, demo video, and GitHub-ready project structure"
        ], "#ecfeff", "#0891b2", 14, 9)

add_arrow(ax, 8, 2.35, 8, 1.9)

add_box(ax, 0.5, 0.9, 1.6, 2.4, "Model Stack",
        ["YOLO11s", "EasyOCR", "OpenCV", "Python"], "#f8fafc", "#64748b", 12, 10)

add_box(ax, 13.9, 0.9, 1.6, 2.4, "Review Policy",
        ["Unreadable plate", "Weak OCR", "Unclear signal", "Tracking-based cases"], "#f8fafc", "#64748b", 12, 10)

plt.tight_layout()
plt.savefig("architecture/violationiq_architecture_explained.png", dpi=300, bbox_inches="tight")
plt.close()

print("Done:")
print("architecture/violationiq_architecture_main.png")
print("architecture/violationiq_architecture_explained.png")
