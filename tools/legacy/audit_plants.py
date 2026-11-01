import os, sys
sys.path.insert(0, r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz")
import pvz_ten_levels as game
from PIL import Image

print(f"Total plants defined: {len(game.PLANTS)}")
print("-" * 80)
print(f"{'Key':18} | {'CN Name':8} | {'Cost':4} | {'Card Exists':11} | {'Frames':6} | {'Sample Frame Size':17} | {'Card Size':10}")
print("-" * 80)

base_dir = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz"
card_dir = os.path.join(base_dir, "assets", "cards")
plant_dir = os.path.join(base_dir, "assets", "plants")

for k, v in game.PLANTS.items():
    name = v.get("name", "")
    cost = v.get("cost", 0)
    
    card_file = os.path.join(card_dir, f"card_{k}.png")
    card_exists = os.path.exists(card_file)
    card_size = ""
    if card_exists:
        cimg = Image.open(card_file)
        card_size = f"{cimg.size[0]}x{cimg.size[1]}"
        
    pdir = os.path.join(plant_dir, k)
    frame_count = 0
    sample_size = "None"
    if os.path.exists(pdir):
        files = [f for f in os.listdir(pdir) if f.endswith(".png")]
        frame_count = len(files)
        if files:
            pimg = Image.open(os.path.join(pdir, files[0]))
            sample_size = f"{pimg.size[0]}x{pimg.size[1]}"
            
    print(f"{k:18} | {name:8} | {cost:4} | {str(card_exists):11} | {frame_count:6} | {sample_size:17} | {card_size:10}")
