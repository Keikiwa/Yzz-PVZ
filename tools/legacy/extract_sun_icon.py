# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageFont, ImageDraw

BASE_DIR = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz"
CARD_DIR = os.path.join(BASE_DIR, "assets", "cards")
CACHE_DIR = os.path.join(BASE_DIR, "download_cache")

# Extract the sun icon from card_sunflower.png
sunflower = Image.open(os.path.join(CARD_DIR, "card_sunflower.png")).convert("RGBA")
# Sunflower card size is (64, 89). The sun icon is around (45..60, 71..84)
sun_icon = sunflower.crop((46, 70, 60, 84))
sun_icon.save(os.path.join(CACHE_DIR, "extracted_card_sun_icon.png"))

print("Extracted sun icon saved.")
