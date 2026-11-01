# -*- coding: utf-8 -*-
import urllib.request
from pathlib import Path
from PIL import Image

cache_dir = Path("10-pvz/download_cache")
cache_dir.mkdir(parents=True, exist_ok=True)

# 1. 从 TheLazyCodernothacker/typescript-v1d8vn 下载官方卡片
raw_base = "https://raw.githubusercontent.com/TheLazyCodernothacker/typescript-v1d8vn/master/"
cards_to_fetch = {
    "gatlingpea": "GatlingPea.png",
    "twinsunflower": "TwinSunflower.png",
    "tallnut": "TallNut.png",
    "starfruit": "Starfruit.png",
    "doomshroom": "DoomShroom.png",
    "fumeshroom": "FumeShroom.png",
    "hypnoshroom": "HypnoShroom.png",
    "garlic": "Garlic.png",
    "spikeweed": "Spikeweed.png",
    "repeater": "Repeater.png",
}

for plant_key, filename in cards_to_fetch.items():
    url = raw_base + filename
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            out_file = cache_dir / f"auth_{filename}"
            out_file.write_bytes(data)
            print(f"Downloaded {filename}: {len(data)} bytes")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

print("Phase 1 complete.")
