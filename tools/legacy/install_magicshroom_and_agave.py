# -*- coding: utf-8 -*-
"""处理并安装魔术菇与龙舌兰官方超清立绘序列帧
"""
import os
import math
from PIL import Image

BASE_DIR = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz"
CACHE_DIR = os.path.join(BASE_DIR, "download_cache")
PLANTS_DIR = os.path.join(BASE_DIR, "assets", "plants")

def generate_breathing_frames(src_img, target_dir, target_size=(100, 100), num_frames=12, prefix="idle"):
    os.makedirs(target_dir, exist_ok=True)
    # clean old files
    for f in os.listdir(target_dir):
        if f.endswith(".png"):
            os.remove(os.path.join(target_dir, f))
            
    # Base resize
    base = src_img.resize(target_size, Image.Resampling.LANCZOS)
    
    for i in range(num_frames):
        theta = 2 * math.pi * (i / num_frames)
        # Subtle squash & stretch breathing: 1.0 +- 0.03
        sy = 1.0 + 0.035 * math.sin(theta)
        sx = 1.0 - 0.02 * math.sin(theta)
        
        cur_w = max(10, int(target_size[0] * sx))
        cur_h = max(10, int(target_size[1] * sy))
        
        scaled = base.resize((cur_w, cur_h), Image.Resampling.BILINEAR)
        canvas = Image.new("RGBA", (target_size[0] + 10, target_size[1] + 10), (0, 0, 0, 0))
        
        # Bottom-center align so plant stays grounded while breathing
        cx = canvas.width // 2
        bottom_y = canvas.height - 4
        px = cx - cur_w // 2
        py = bottom_y - cur_h
        
        canvas.paste(scaled, (px, py), scaled)
        out_path = os.path.join(target_dir, f"{prefix}_{i}.png")
        canvas.save(out_path)
        
    print(f"Generated {num_frames} breathing frames in {target_dir}")

def main():
    m_path = os.path.join(CACHE_DIR, "magicshroom_hd.png")
    a_path = os.path.join(CACHE_DIR, "agave_hd.png")
    
    im_m = Image.open(m_path).convert("RGBA")
    im_a = Image.open(a_path).convert("RGBA")
    
    generate_breathing_frames(im_m, os.path.join(PLANTS_DIR, "magicshroom"), target_size=(90, 95))
    generate_breathing_frames(im_a, os.path.join(PLANTS_DIR, "agave"), target_size=(95, 100))

if __name__ == "__main__":
    main()
