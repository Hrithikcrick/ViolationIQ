import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

out_dir = Path("data/sample_images/signboard_showcase")
out_dir.mkdir(parents=True, exist_ok=True)

queries = [
    "real traffic stop sign road",
    "real no entry traffic sign road",
    "real speed limit traffic sign road",
    "real no parking traffic sign road",
    "real turn traffic sign road"
]

headers = {
    "User-Agent": "ViolationIQ-Hackathon/1.0"
}

def urlopen(url):
    req = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(req, timeout=30)

def search_commons(query):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": "10",
        "prop": "imageinfo",
        "iiprop": "url|mime",
        "format": "json"
    }

    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)

    with urlopen(url) as r:
        data = json.loads(r.read().decode("utf-8"))

    pages = data.get("query", {}).get("pages", {})

    for _, page in pages.items():
        info = page.get("imageinfo", [])

        if not info:
            continue

        item = info[0]
        image_url = item.get("url", "")
        mime = item.get("mime", "")

        if mime in ["image/jpeg", "image/png"] and image_url.lower().split("?")[0].endswith((".jpg", ".jpeg", ".png")):
            return image_url

    return None

downloaded = []

for i, query in enumerate(queries, 1):
    print("Searching:", query)
    image_url = search_commons(query)

    if image_url is None:
        print("No image found for:", query)
        continue

    ext = ".jpg"

    if image_url.lower().split("?")[0].endswith(".png"):
        ext = ".png"

    out_path = out_dir / f"signboard_showcase_{i:02d}{ext}"

    print("Downloading:", image_url)

    with urlopen(image_url) as r:
        content = r.read()

    out_path.write_bytes(content)
    downloaded.append(str(out_path))

    time.sleep(1)

print("")
print("Downloaded signboard images:")
for p in downloaded:
    print(p)

print("Total:", len(downloaded))
