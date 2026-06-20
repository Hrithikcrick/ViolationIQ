import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path("downloaded_signboard_dataset")
out = Path("data/sample_images/signboard_showcase")
out.mkdir(parents=True, exist_ok=True)

xmls = list(root.rglob("*.xml"))

wanted = {
    "stop": None,
    "speedlimit": None,
    "crosswalk": None,
    "trafficlight": None
}

extra = []

for xml_path in xmls:
    try:
        tree = ET.parse(xml_path)
        root_xml = tree.getroot()
        filename = root_xml.findtext("filename")
        labels = []

        for obj in root_xml.findall("object"):
            name = obj.findtext("name")
            if name:
                labels.append(name.lower().replace(" ", ""))

        img_path = None
        if filename:
            possible = list(root.rglob(filename))
            if possible:
                img_path = possible[0]

        if img_path is None:
            for ext in [".jpg", ".jpeg", ".png"]:
                possible = xml_path.with_suffix(ext)
                if possible.exists():
                    img_path = possible
                    break

        if img_path is None:
            continue

        for key in wanted:
            if wanted[key] is None and key in labels:
                wanted[key] = (img_path, xml_path)

        if labels:
            extra.append((img_path, xml_path))

    except Exception:
        pass

selected = []

for key in wanted:
    if wanted[key] is not None:
        selected.append(wanted[key])

for pair in extra:
    if len(selected) >= 5:
        break
    if pair not in selected:
        selected.append(pair)

selected = selected[:5]

for i, (img, xml) in enumerate(selected, 1):
    img_ext = img.suffix.lower()
    new_img = out / f"signboard_showcase_{i:02d}{img_ext}"
    new_xml = out / f"signboard_showcase_{i:02d}.xml"

    shutil.copy(img, new_img)
    shutil.copy(xml, new_xml)

print("Selected real signboard samples:", len(selected))
for p in sorted(out.glob("*")):
    print(p)
