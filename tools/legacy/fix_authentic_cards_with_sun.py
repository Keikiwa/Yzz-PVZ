# -*- coding: utf-8 -*-
"""为大喷菇、魅惑菇、毁灭菇、杨桃、高坚果等卡牌添加正规原版阳光数值与小太阳徽章，
并将卡牌尺寸统一规范为原版标准的 (64, 89)。
"""
import os
import sys
from PIL import Image, ImageFont, ImageDraw

BASE_DIR = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz"
CARD_DIR = os.path.join(BASE_DIR, "assets", "cards")
CACHE_DIR = os.path.join(BASE_DIR, "download_cache")

FIX_LIST = [
    ("fumeshroom", 75),
    ("hypnoshroom", 75),
    ("doomshroom", 125),
    ("starfruit", 125),
    ("tallnut", 125),
]

def make_card(plant_key, cost):
    card_path = os.path.join(CARD_DIR, f"card_{plant_key}.png")
    if not os.path.exists(card_path):
        print(f"Card {card_path} not found!")
        return
        
    src_img = Image.open(card_path).convert("RGBA")
    
    # 统一高质量缩放到 64 x 89
    target_w, target_h = 64, 89
    resized = src_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # 贴小太阳图标
    sun_icon_path = os.path.join(CACHE_DIR, "extracted_card_sun_icon.png")
    if os.path.exists(sun_icon_path):
        sun_icon = Image.open(sun_icon_path).convert("RGBA")
        resized.paste(sun_icon, (46, 71), sun_icon)
        
    draw = ImageDraw.Draw(resized)
    
    # 寻找加粗英文字体
    font = None
    font_paths = [
        r"C:\Windows\Fonts\arialbd.ttf",   # Arial Bold
        r"C:\Windows\Fonts\segoeuib.ttf",  # Segoe UI Bold
        r"C:\Windows\Fonts\tahomabd.ttf",  # Tahoma Bold
        r"C:\Windows\Fonts\impact.ttf",
    ]
    font_size = 13 if cost < 100 else 11
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, font_size)
                break
            except Exception:
                pass
    if font is None:
        font = ImageFont.load_default()
        
    cost_str = str(cost)
    # 计算文字宽度与高度，居中偏左放置在 (6..44, 71..84)
    bbox = draw.textbbox((0, 0), cost_str, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    area_cx = (6 + 45) // 2
    area_cy = (71 + 84) // 2
    
    tx = area_cx - tw // 2
    ty = area_cy - th // 2 - 1
    
    # 绘制深灰/黑色原版文字
    draw.text((tx, ty), cost_str, fill=(0, 0, 0, 255), font=font)
    
    # 保存覆盖
    resized.save(card_path)
    print(f"Updated card_{plant_key}.png with cost {cost} at size (64, 89)")

def main():
    for plant_key, cost in FIX_LIST:
        make_card(plant_key, cost)

if __name__ == "__main__":
    main()
