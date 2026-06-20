import base64
import gzip
import json
import subprocess
import sys
from pathlib import Path

BLOB = """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"""

files = json.loads(gzip.decompress(base64.b64decode(BLOB)).decode("utf-8"))

for rel, text in files:
    path = Path(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("Wrote:", path)

for folder in [
    "outputs/FINAL_SHOWCASE/traffic_evidence",
    "outputs/FINAL_SHOWCASE/helmet_plate",
    "outputs/FINAL_SHOWCASE/redlight",
    "outputs/FINAL_SHOWCASE/signboard_context",
    "outputs/FINAL_SHOWCASE/videos",
    "reports",
    "weights",
    "data/sample_images",
    "data/sample_videos",
]:
    Path(folder).mkdir(parents=True, exist_ok=True)

print("Checking Python files...")
result = subprocess.run([sys.executable, "-m", "compileall", "src", "scripts"], text=True)
print("Compile return code:", result.returncode)

print("""
Done.

Now put your trained weights here:
weights/traffic_yolo11s_best.pt
weights/helmet_yolo11s_best.pt
weights/large_plate_yolo11s_best.pt
weights/yolo11s.pt

Put sample images in:
data/sample_images

Put sample videos in:
data/sample_videos

Then run:
python scripts/reproduce_pipeline.py --traffic_model weights/traffic_yolo11s_best.pt --helmet_model weights/helmet_yolo11s_best.pt --plate_model weights/large_plate_yolo11s_best.pt --vehicle_model weights/yolo11s.pt
""")
