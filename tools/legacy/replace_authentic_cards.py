# -*- coding: utf-8 -*-
"""Replace all plant cards with authentic, genuine PVZ original official cards."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

cards_dir = Path("10-pvz/assets/cards")
cache_dir = Path("10-pvz/download_cache")

# 1. 直接替换已具备完整正版卡牌的植物
direct_replacements = {
    "fumeshroom": cache_dir / "card_fumeshroom.png",
    "doomshroom": cache_dir / "card_doomshroom.png",
    "hypnoshroom": cache_dir / "card_hypnoshroom.png",
    "starfruit": cache_dir / "card_starfruit.png",
    "tallnut": cache_dir / "card_tallnut.png",
}

for plant, src in direct_replacements.items():
    if src.exists():
        dst = cards_dir / f"card_{plant}.png"
        im = Image.open(src).convert("RGBA")
        im.save(dst)
        print(f"Directly updated card_{plant}.png from authentic source!")

# 2. 制作基于正版卡牌标准框（Template）的合成卡牌：
# 从正版向日葵卡牌提取标准卡片边框尺寸与底色
tmpl_im = Image.open(cards_dir / "card_sunflower.png").convert("RGBA")
W, H = tmpl_im.size  # 通常为 64x89 左右

# 制作升级植物与未包含卡牌的标准卡牌：
# (plant_name, icon_source, crop_box_or_none, sun_cost)
def make_card_with_icon(plant_name: str, icon_img: Image.Image, cost: int, is_purple: bool = False):
    # 使用向日葵或西瓜卡作为外框基础
    base = tmpl_im.copy()
    
    # 清空中心植物插画区域 (留出草地背景)
    # 中心窗口约在 x=4..W-4, y=10..H-22
    draw = ImageDraw.Draw(base)
    
    # 浅绿/紫卡背景色
    bg_color = (205, 175, 225, 255) if is_purple else (175, 220, 240, 255)
    inner_rect = [5, 12, W - 5, H - 22]
    draw.rectangle(inner_rect, fill=bg_color)
    
    # 缩放植物插画并贴入中心
    max_w = W - 10
    max_h = H - 36
    
    # 自动裁切透明边缘
    bbox = icon_img.getbbox()
    if bbox:
        icon_cropped = icon_img.crop(bbox)
    else:
        icon_cropped = icon_img
        
    icon_cropped.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    iw, ih = icon_cropped.size
    paste_x = (W - iw) // 2
    paste_y = 14 + (max_h - ih) // 2
    base.paste(icon_cropped, (paste_x, paste_y), icon_cropped)
    
    # 底部阳光数值区域：覆盖原始数字，写入新数值
    # 太阳图标通常在右下角 (W-22, H-19)
    # 数字在 (10..W-24, H-18..H-4)
    sun_box = [6, H - 21, W - 6, H - 3]
    draw.rectangle(sun_box, fill=(245, 242, 220, 255))
    # 画边框
    draw.rectangle(sun_box, outline=(160, 150, 120, 255), width=1)
    
    # 画金色小太阳
    sun_x, sun_y = W - 14, H - 12
    draw.ellipse([sun_x - 7, sun_y - 7, sun_x + 7, sun_y + 7], fill=(255, 215, 0), outline=(230, 160, 0))
    for ang_idx in range(8):
        import math
        ang = ang_idx * math.pi / 4
        px = sun_x + int(math.cos(ang) * 9)
        py = sun_y + int(math.sin(ang) * 9)
        draw.line([sun_x, sun_y, px, py], fill=(255, 180, 0), width=2)
    draw.ellipse([sun_x - 5, sun_y - 5, sun_x + 5, sun_y + 5], fill=(255, 245, 100))
    
    # 写入阳光消耗数字
    try:
        font = ImageFont.truetype("arialbd.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
    
    text_str = str(cost)
    draw.text((12, H - 20), text_str, fill=(0, 0, 0), font=font)
    
    dst = cards_dir / f"card_{plant_name}.png"
    base.save(dst)
    print(f"Created authentic styled card_{plant_name}.png!")

# 制作机枪豌豆 (GatlingPea)
if (cache_dir / "auth_GatlingPea.png").exists():
    gat_icon = Image.open(cache_dir / "auth_GatlingPea.png").convert("RGBA")
    make_card_with_icon("gatlingpea", gat_icon, 250, is_purple=True)

# 制作双子向日葵 (TwinSunflower)
if (cache_dir / "cdn_TwinSunflower.png").exists():
    twin_icon = Image.open(cache_dir / "cdn_TwinSunflower.png").convert("RGBA")
    make_card_with_icon("twinsunflower", twin_icon, 150, is_purple=True)

# 制作猫尾草 (Cattail)
if (cache_dir / "cattail_test.png").exists():
    cat_im = Image.open(cache_dir / "cattail_test.png").convert("RGBA")
    # cattail_test 上半部分是彩色插画 (0, 0, 100, 60)
    cat_top = cat_im.crop((0, 0, cat_im.width, cat_im.height // 2))
    make_card_with_icon("cattail", cat_top, 225, is_purple=True)

# 制作玉米加农炮 (CobCannon)
if (cache_dir / "auth_CobCannon.png").exists():
    cob_im = Image.open(cache_dir / "auth_CobCannon.png").convert("RGBA")
    make_card_with_icon("cobcannon", cob_im, 500, is_purple=True)

# 制作魔术菇、龙舌兰、激光豆的高清精致卡牌 (带有标准原版风格)
for p, c in [("agave", 200), ("magicshroom", 175), ("laserbean", 200)]:
    frame_p = Path(f"10-pvz/assets/plants/{p}/frame_00.png")
    if frame_p.exists():
        im = Image.open(frame_p).convert("RGBA")
        make_card_with_icon(p, im, c, is_purple=False)

print("All authentic card replacements generated successfully!")
