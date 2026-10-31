# -*- coding: utf-8 -*-
"""High precision plant background cleaning and tight bounding box cropping."""

from PIL import Image
from collections import deque
from pathlib import Path

def is_green_bg(r, g, b, a):
    if a < 15:
        return True
    # 典型草地绿底特征: 绿色明显大于红色和蓝色，或者特定绿色系
    if g > 70 and g > r * 1.15 and g > b * 1.15:
        return True
    # 暗绿底特征
    if g > 40 and g > r and g > b and r < 80 and b < 80:
        return True
    return False

def clean_and_crop_plant(img_path: Path):
    im = Image.open(img_path).convert("RGBA")
    w, h = im.size
    pixels = im.load()

    # 1. BFS flood fill from all 4 borders
    visited = set()
    queue = deque()

    for x in range(w):
        for y in (0, h - 1):
            if (x, y) not in visited:
                r, g, b, a = pixels[x, y]
                if is_green_bg(r, g, b, a):
                    visited.add((x, y))
                    queue.append((x, y))

    for y in range(h):
        for x in (0, w - 1):
            if (x, y) not in visited:
                r, g, b, a = pixels[x, y]
                if is_green_bg(r, g, b, a):
                    visited.add((x, y))
                    queue.append((x, y))

    while queue:
        cx, cy = queue.popleft()
        pixels[cx, cy] = (0, 0, 0, 0)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                r, g, b, a = pixels[nx, ny]
                if is_green_bg(r, g, b, a):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    # 2. Tight crop
    bbox = im.getbbox()
    if bbox:
        # 裁剪出真正的植物主体，周围留 4px padding
        p_left = max(0, bbox[0] - 4)
        p_top = max(0, bbox[1] - 4)
        p_right = min(w, bbox[2] + 4)
        p_bottom = min(h, bbox[3] + 4)
        cropped = im.crop((p_left, p_top, p_right, p_bottom))
        cropped.save(img_path)
        return cropped.size
    else:
        im.save(img_path)
        return im.size

def batch_process():
    plants = ["cabbagepult", "wintermelon", "melonpult", "kernelpult", "squash"]
    for p in plants:
        p_dir = Path(f"10-pvz/assets/plants/{p}")
        files = list(p_dir.glob("*.png"))
        print(f"Cleaning {p}: {len(files)} frames...")
        for f in files:
            new_sz = clean_and_crop_plant(f)
        print(f"  -> {p} done, sample new size: {new_sz}")

if __name__ == "__main__":
    batch_process()
