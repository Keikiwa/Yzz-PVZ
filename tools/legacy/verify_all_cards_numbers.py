import os, sys
sys.path.insert(0, r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz")
import pvz_ten_levels as game
from PIL import Image

card_dir = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\assets\cards"

print("=== CARD SUN NUMBER RE-AUDIT ===")
all_passed = True
for k, v in game.PLANTS.items():
    cpath = os.path.join(card_dir, f"card_{k}.png")
    img = Image.open(cpath).convert("RGB")
    w, h = img.size
    badge = img.crop((int(w * 0.08), int(h * 0.78), int(w * 0.75), int(h * 0.98)))
    pixels = list(badge.getdata())
    dark_pixels = sum(1 for r, g, b in pixels if (0.299*r + 0.587*g + 0.114*b) < 110)
    has_text = dark_pixels >= 15
    if not has_text:
        all_passed = False
    print(f"{k:18} | Cost: {v.get('cost'):3} | Size: {str(img.size):10} | Dark pixels: {dark_pixels:4} | Has number: {has_text}")

print("-" * 70)
print("All 34 cards passed sun number audit:", all_passed)
