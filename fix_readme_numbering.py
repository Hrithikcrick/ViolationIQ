from pathlib import Path
import re

path = Path("README.md")
text = path.read_text(encoding="utf-8").replace("\r\n", "\n")

# -----------------------------
# 1. Remove broken incomplete speed fragment if present
# -----------------------------
text = re.sub(
    r"\n---\s*\n\s*It tracks detected vehicles across video frames.*?Important:\s*\n\s*\n---",
    "\n---",
    text,
    flags=re.S
)

# -----------------------------
# 2. Extract and remove any existing Models Used section
# -----------------------------
model_pattern = r"\n##\s*\d+\.\s*Models Used and Results Summary\s*\n.*?(?=\n##\s*\d+\.\s|\n<!-- PROJECT_REPORT_START -->|\Z)"
model_blocks = re.findall(model_pattern, text, flags=re.S)

text = re.sub(model_pattern, "\n", text, flags=re.S)

models_section = """
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
"""

# -----------------------------
# 3. Insert Models section before Implemented Deliverables
# -----------------------------
text = re.sub(
    r"\n##\s*\d+\.\s*Implemented Deliverables",
    "\n" + models_section + "\n## 6. Implemented Deliverables",
    text,
    count=1
)

# -----------------------------
# 4. Fix missing blank line after deliverables table
# -----------------------------
text = text.replace(
    "| 10 | Architecture and Documentation | Includes architecture diagram, modular source code, config, reports, and README |\n##",
    "| 10 | Architecture and Documentation | Includes architecture diagram, modular source code, config, reports, and README |\n\n---\n\n##"
)

# -----------------------------
# 5. Fix old architecture filename references if present
# -----------------------------
text = text.replace(
    "architecture/violationiq_architecture.png",
    "architecture/violationiq_architecture_main.png"
)

# -----------------------------
# 6. Remove old Final Claim block and Project Report block
# -----------------------------
text = re.sub(
    r"\n##\s*\d+\.\s*Final Claim\s*\n.*?(?=\n<!-- PROJECT_REPORT_START -->|\Z)",
    "\n",
    text,
    flags=re.S
)

text = re.sub(
    r"\n<!-- PROJECT_REPORT_START -->.*?<!-- PROJECT_REPORT_END -->",
    "\n",
    text,
    flags=re.S
)

# -----------------------------
# 7. Add clean Project Report and Final Claim at the end
# -----------------------------
appendix = """

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
"""

text = text.strip() + appendix

# -----------------------------
# 8. Renumber all numbered H2 sections consistently
# -----------------------------
count = 0

def renumber(match):
    global count
    count += 1
    title = match.group(1).strip()
    return f"## {count}. {title}"

text = re.sub(r"^##\s*\d+\.\s*(.+)$", renumber, text, flags=re.M)

# -----------------------------
# 9. Fix accidental multiple blank lines
# -----------------------------
text = re.sub(r"\n{4,}", "\n\n\n", text)

path.write_text(text, encoding="utf-8")

print("README fixed successfully.")
print("Total numbered sections:", count)
