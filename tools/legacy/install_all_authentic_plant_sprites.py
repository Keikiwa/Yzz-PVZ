# -*- coding: utf-8 -*-
"""下载并安装所有原版正规植物立绘序列帧
替换掉旧有简笔画，补齐缺失的高坚果、机枪射手、大喷菇、魅惑菇、毁灭菇、杨桃、激光豆等正版动画帧。
"""
import os
import shutil
import urllib.request
from PIL import Image, ImageSequence

BASE_URL = "https://cdn.jsdelivr.net/gh/Plants-vs-Zombies-MODDED/game@main/"
CACHE_DIR = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\download_cache"
PLANTS_DIR = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\assets\plants"

DOWNLOADS = [
    # (rel_url, local_gif_name, plant_key, anim_prefix)
    ("game/images/Plants/FumeShroom/FumeShroom.gif", "FumeShroom.gif", "fumeshroom", "idle"),
    ("game/images/Plants/FumeShroom/FumeShroomAttack.gif", "FumeShroomAttack.gif", "fumeshroom", "attack"),
    ("game/images/Plants/TallNut/TallNut.gif", "TallNut.gif", "tallnut", "idle"),
    ("game/images/Plants/TallNut/TallnutCracked1.gif", "TallnutCracked1.gif", "tallnut", "cracked1"),
    ("game/images/Plants/TallNut/TallnutCracked2.gif", "TallnutCracked2.gif", "tallnut", "cracked2"),
    ("game/images/Plants/GatlingPea/GatlingPea.gif", "GatlingPea.gif", "gatlingpea", "idle"),
    ("game/images/Plants/HypnoShroom/HypnoShroom.gif", "HypnoShroom.gif", "hypnoshroom", "idle"),
    ("game/images/Plants/DoomShroom/DoomShroom.gif", "DoomShroom.gif", "doomshroom", "idle"),
    ("game/images/Plants/DoomShroom/BeginBoom.gif", "DoomShroomBeginBoom.gif", "doomshroom", "explode"),
    ("game/images/Plants/Starfruit/Starfruit.gif", "Starfruit.gif", "starfruit", "idle"),
    ("game/images/Plants/LaserPea/LaserPea.gif", "LaserPea.gif", "laserbean", "idle"),
    ("game/images/Plants/LaserPea/LaserPeaAttack.gif", "LaserPeaAttack.gif", "laserbean", "attack"),
]

def download_file(rel_url, local_name):
    url = BASE_URL + rel_url
    path = os.path.join(CACHE_DIR, local_name)
    if os.path.exists(path) and os.path.getsize(path) > 100:
        return path
    print(f"Downloading {local_name}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        with open(path, "wb") as f:
            f.write(resp.read())
    return path

def extract_frames(gif_path, out_dir, prefix):
    os.makedirs(out_dir, exist_ok=True)
    im = Image.open(gif_path)
    count = 0
    for idx, frame in enumerate(ImageSequence.Iterator(im)):
        frame_rgba = frame.convert("RGBA")
        out_path = os.path.join(out_dir, f"{prefix}_{idx}.png")
        frame_rgba.save(out_path)
        count += 1
    print(f"  -> Extracted {count} frames ({prefix}) to {os.path.basename(out_dir)}")

def main():
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # 记录需要清空简笔画旧目录的植物
    cleared_dirs = set()

    for rel_url, local_name, plant_key, prefix in DOWNLOADS:
        target_dir = os.path.join(PLANTS_DIR, plant_key)
        
        # 如果是首次遇到该植物，清空旧简笔画
        if plant_key not in cleared_dirs:
            if os.path.exists(target_dir):
                for f in os.listdir(target_dir):
                    if f.endswith(".png"):
                        os.remove(os.path.join(target_dir, f))
            else:
                os.makedirs(target_dir, exist_ok=True)
            cleared_dirs.add(plant_key)
            
        gif_path = download_file(rel_url, local_name)
        extract_frames(gif_path, target_dir, prefix)

    print("\nAll target plant sprites downloaded and installed successfully!")

if __name__ == "__main__":
    main()
