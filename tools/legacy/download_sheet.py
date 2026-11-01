# -*- coding: utf-8 -*-
import urllib.request
import re
from pathlib import Path

urls = [
    "https://www.spriters-resource.com/pc_computer/pvz/sheet/26450/",
    "https://www.spriters-resource.com/mobile/plantsvszombies/sheet/46761/",
]

for url in urls:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            matches = re.findall(r'(/resources/sheets/\d+/\d+\.(?:png|gif))', html)
            print(f"URL: {url} -> matches: {matches}")
            if matches:
                img_url = "https://www.spriters-resource.com" + matches[0]
                print(f"Downloading sheet from {img_url}...")
                img_req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0", "Referer": url})
                with urllib.request.urlopen(img_req, timeout=15) as img_resp:
                    data = img_resp.read()
                    out_path = Path("10-pvz/download_cache/pvz_seed_sheet.png")
                    out_path.write_bytes(data)
                    print(f"Successfully downloaded {len(data)} bytes to {out_path}!")
                    break
    except Exception as e:
        print(f"Error on {url}: {e}")
