import zipfile
from pathlib import Path
import subprocess
import sys

FILE_ID = "1XeJq1Afzw0hjd1gdzt1pjwlz6GvF4J2f"
ZIP_NAME = "ViolationIQ_Judge_Assets.zip"

required_files = [
    "weights/traffic_yolo11s_best.pt",
    "weights/helmet_yolo11s_best.pt",
    "weights/large_plate_yolo11s_best.pt",
    "weights/yolo26n.pt",
]

def install_gdown():
    try:
        import gdown
        return gdown
    except Exception:
        print("Installing gdown...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown"])
        import gdown
        return gdown

def download_zip():
    gdown = install_gdown()
    url = f"https://drive.google.com/uc?id={FILE_ID}"
    print("Downloading judge assets from Google Drive...")
    gdown.download(url, ZIP_NAME, quiet=False, fuzzy=True)
    if not Path(ZIP_NAME).exists():
        raise FileNotFoundError("Asset zip was not downloaded.")
    print("Downloaded:", ZIP_NAME)

def extract_zip():
    print("Extracting assets...")
    with zipfile.ZipFile(ZIP_NAME, "r") as z:
        z.extractall(".")
    print("Extraction completed.")

def check_assets():
    missing = []
    for item in required_files:
        if not Path(item).exists():
            missing.append(item)
    if missing:
        print("Missing required files:")
        for item in missing:
            print("-", item)
        raise FileNotFoundError("Some required assets are missing.")
    print("All required weight files found.")
    if Path("data/sample_images").exists():
        print("Sample images found:", len([p for p in Path("data/sample_images").rglob("*") if p.is_file()]))
    if Path("data/sample_videos").exists():
        print("Sample videos found:", len([p for p in Path("data/sample_videos").rglob("*") if p.is_file()]))

if __name__ == "__main__":
    download_zip()
    extract_zip()
    check_assets()
    print()
    print("Assets are ready.")
    print("Now run:")
    print("python scripts/reproduce_pipeline.py --traffic_model weights/traffic_yolo11s_best.pt --helmet_model weights/helmet_yolo11s_best.pt --plate_model weights/large_plate_yolo11s_best.pt --vehicle_model weights/yolo26n.pt")
