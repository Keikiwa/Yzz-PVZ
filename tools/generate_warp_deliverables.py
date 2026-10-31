# -*- coding: utf-8 -*-
import os
import shutil
import sys
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
sys.path.insert(0, str(Path(r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz")))
import pvz_ten_levels as pvz

pygame.init()
screen = pygame.display.set_mode((pvz.WIDTH, pvz.HEIGHT))
game = pvz.Game(screen, headless=True)

out_img_dir = Path(r"F:\Desktop\.DeskBox\文件夹\反重力产出\图片")
out_img_dir.mkdir(parents=True, exist_ok=True)

# 1. 右上角清爽控制按钮特写
game.start_level(0)
game.mode = "playing"
game.draw()
topright_crop = screen.subsurface(pygame.Rect(900, 0, 300, 100)).copy()
p_topright = out_img_dir / "植物大战僵尸_右上角清爽控制按钮特写.png"
pygame.image.save(topright_crop, str(p_topright))
print(f"Saved: {p_topright}")

# 2. 时空穿梭·任意跳关传送门界面
game.overlay = "warp"
game.draw()
p_warp = out_img_dir / "植物大战僵尸_时空跳关传送门实机.png"
pygame.image.save(screen, str(p_warp))
print(f"Saved: {p_warp}")

# 3. 泳池关卡（第 11 关）实机截图
game.overlay = ""
game.setup_preview(10)
for _ in range(60):
    game.time_value += 1 / 60.0
    game.update(1 / 60.0)
game.banner_timer = 0
game.draw()
p_pool = out_img_dir / "植物大战僵尸_泳池水面水生实战实机.png"
pygame.image.save(screen, str(p_pool))
print(f"Saved: {p_pool}")

# 4. 第 16 关无尽挑战实机截图
game.start_level(15)
game.mode = "playing"
game.setup_preview(15)
for _ in range(60):
    game.time_value += 1 / 60.0
    game.update(1 / 60.0)
game.banner_timer = 0
game.draw()
p_endless = out_img_dir / "植物大战僵尸_第16关水陆无尽实机.png"
pygame.image.save(screen, str(p_endless))
print(f"Saved: {p_endless}")

print("All delivery screenshots generated successfully!")
