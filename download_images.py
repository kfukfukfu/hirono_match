"""
download_images.py
------------------
Wikimedia Commons から洋野町関連の写真を取得し、
static/images/ 以下に配置する。
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).parent / "static" / "images"
API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "hirono-match/1.0 (education project)"

# (保存先パス, Wikimedia Commons ファイル名)
DOWNLOADS = [
    ("hero.jpg", "Taneichi Seaside Park 1.jpg"),
    ("features/star.jpg", "Hironomakiba Astronomical Observatory.jpg"),
    ("features/sea.jpg", "Taneichi, Natural Paradise - Flickr - fo.ol.jpg"),
    ("features/food.jpg", "はまなす亭.jpg"),
    ("spots/observatory.jpg", "Hironomakiba Astronomical Observatory.jpg"),
    ("spots/kaihin.jpg", "Taneichi Seaside Park 1.jpg"),
    ("spots/hamanasu.jpg", "はまなす亭.jpg"),
    ("spots/mokko.jpg", "Michinoeki Oono in Iwate.JPG"),
    ("spots/coast.jpg", "Taneichi, Natural Paradise - Flickr - fo.ol.jpg"),
    ("spots/souvenir.jpg", "Michinoeki Oono in Iwate.JPG"),
    ("spots/cafe.jpg", "Route 45 Taneichi By-Pass Iwate Prefecture Hirono Town 1.jpg"),
    ("spots/minshuku.jpg", "Taneichi Seaside Park 1.jpg"),
    ("spots/hotel.jpg", "E45SANRIKU-EXP Hirono-Taneichi IC Hirono Iwate.jpg"),
    ("spots/trail.jpg", "091025中野白滝（秋） - panoramio.jpg"),
    ("types/star.jpg", "Hironomakiba Astronomical Observatory.jpg"),
    ("types/food.jpg", "特製生ウニ丼と天然ほや刺（はまなす亭）.jpg"),
    ("types/sea.jpg", "Taneichi Seaside Park 1.jpg"),
    ("types/photo.jpg", "Taneichi, Natural Paradise - Flickr - fo.ol.jpg"),
    ("types/outdoor.jpg", "090329中野白滝（晩冬） - panoramio.jpg"),
    ("types/experience.jpg", "Michinoeki Oono in Iwate.JPG"),
    ("types/walk.jpg", "小子内付近の風景 - panoramio.jpg"),
    ("types/cafe.jpg", "はまなす亭.jpg"),
]


def fetch_image_url(filename: str, width: int = 1200) -> str:
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "titles": f"File:{filename}",
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": str(width),
            "format": "json",
        }
    )
    req = urllib.request.Request(f"{API}?{params}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)

    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    if "missing" in page:
        raise FileNotFoundError(f"Commons file not found: {filename}")

    info = page["imageinfo"][0]
    return info.get("thumburl") or info["url"]


def download_file(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())


def main() -> None:
    for rel_path, commons_name in DOWNLOADS:
        dest = BASE / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.stat().st_size > 0:
            print(f"Skip existing: {rel_path}")
            continue

        print(f"Downloading {commons_name} -> {rel_path}")
        for attempt in range(5):
            try:
                url = fetch_image_url(commons_name)
                download_file(url, dest)
                break
            except urllib.error.HTTPError as exc:
                if exc.code == 429 and attempt < 4:
                    wait = 5 * (attempt + 1)
                    print(f"  Rate limited, retry in {wait}s...")
                    time.sleep(wait)
                    continue
                raise
        time.sleep(2)
    print("Done.")


if __name__ == "__main__":
    main()
