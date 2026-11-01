# -*- coding: utf-8 -*-
"""Extract pure plant sprites from download_cache GIFs with high precision."""

from PIL import Image
from collections import deque
from pathlib import Path

def is_lawn_bg(r, g, b, a):
    if a < 15:
        return True
    # 典型草坪背景特征：极低饱和度或暗草绿
    # 草坪色值分布在 R: 0~90, G: 60~150, B: 0~45
    # 卷心菜植物主体是亮绿 (G > 180) 或亮黄/棕木头 (R > 130) 或植物黑色轮廓 (R<15, G<15, B<15)
    is_plant_feature = (
        (g > 175 and g > r * 1.2) or # 卷心菜亮嫩绿
        (r > 130 and g > 90) or      # 投石机木架黄褐
        (r > 150 and b > 150) or     # 冰瓜蓝冰晶
        (b > 180 and g > 150) or     # 冰瓜冰块
        (r < 18 and g < 18 and b < 18) # 植物黑色轮廓线
    )
    if is_plant_feature:
        return False
    # 草坪底色
    if (g > 35 and g > r and g > b and b < 50):
        return True
    return False

def clean_and_extract_gif(gif_path: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    gif = Image.open(gif_path)
    n_frames = min(16, gif.n_frames)
    
    # 首先找出所有帧的联合植物 bbox，保持动画连贯
    print(f"Processing {gif_path.name} ({n_frames} frames)...")
    cleaned_frames = []
    
    for f_idx in range(n_frames):
        gif.seek(f_idx)
        im = gif.convert("RGBA")
        w, h = im.size
        pixels = im.load()
        
        # BFS 泛洪：从四周边界出发
        visited = set()
        queue = deque()
        for x in range(w):
            for y in (0, h - 1):
                if (x, y) not in visited and is_lawn_bg(*pixels[x, y]):
                    visited.add((x, y))
                    queue.append((x, y))
        for y in range(h):
            for x in (0, w - 1):
                if (x, y) not in visited and is_lawn_bg(*pixels[x, y]):
                    visited.add((x, y))
                    queue.append((x, y))
                    
        while queue:
            cx, cy = queue.popleft()
            pixels[cx, cy] = (0, 0, 0, 0)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                    if is_lawn_bg(*pixels[nx, ny]):
                        visited.add((nx, ny))
                        queue.append((nx, ny))
                        
        cleaned_frames.append(im)
        
    # 计算所有帧的公共 bbox
    union_bbox = None
    for im in cleaned_frames:
        b = im.getbbox()
        if b:
            if union_bbox is None:
                union_bbox = list(b)
            else:
                union_bbox[0] = min(union_bbox[0], b[0])
                union_bbox[1] = min(union_bbox[1], b[1])
                union_bbox[2] = max(union_bbox[2], b[2])
                union_bbox[3] = max(union_bbox[3], b[3])
                
    if union_bbox:
        p_left = max(0, union_bbox[0] - 2)
        p_top = max(0, union_bbox[1] - 2)
        p_right = min(w, union_bbox[2] + 2)
        p_bottom = min(h, union_bbox[3] + 2)
        crop_box = (p_left, p_top, p_right, p_bottom)
        print(f"  Union bbox: {crop_box}, final size: {p_right - p_left}x{p_bottom - p_top}")
        for f_idx, im in enumerate(cleaned_frames):
            cropped = im.crop(crop_box)
            cropped.save(out_dir / f"idle_{f_idx}.png")
    else:
        for f_idx, im in enumerate(cleaned_frames):
            im.save(out_dir / f"idle_{f_idx}.png")
            
def run_all():
    clean_and_extract_gif(Path("10-pvz/download_cache/cabbagepult.gif"), Path("10-pvz/assets/plants/cabbagepult"))
    clean_and_extract_gif(Path("10-pvz/download_cache/wintermelon.gif"), Path("10-pvz/assets/plants/wintermelon"))
    clean_and_extract_gif(Path("10-pvz/download_cache/melonpult.gif"), Path("10-pvz/assets/plants/melonpult"))
    clean_and_extract_gif(Path("10-pvz/download_cache/kernelpult.gif"), Path("10-pvz/assets/plants/kernelpult"))
    clean_and_extract_gif(Path("10-pvz/download_cache/squash.gif") if Path("10-pvz/download_cache/squash.gif").exists() else Path("10-pvz/assets/plants/squash/idle_0.png"), Path("10-pvz/assets/plants/squash"))
    print("ALL_EXTRACTED_SUCCESSFULLY")

if __name__ == "__main__":
    run_all()
