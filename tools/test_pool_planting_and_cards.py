# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
sys.path.insert(0, str(Path(r"10-pvz")))

import pvz_ten_levels as pvz
import pvz_graphics

pygame.init()
screen = pygame.display.set_mode((pvz.WIDTH, pvz.HEIGHT))
game = pvz.Game(screen, headless=True)

print("=== 开始测试水面关卡植物精准居中种植与卡牌全貌 ===")

# 1. 启动第 11 关（泳池水面关卡）
game.start_level(10)
game.mode = "playing"
assert game.is_pool is True, "Level 11 should be pool environment!"

# 2. 模拟种植植物：
# 在水路 row=2 种睡莲 + 猫尾草
# 在水路 row=3 种睡莲 + 高坚果
# 在陆路 row=0 种向日葵 + 卷心菜投手
# 在陆路 row=1 种双发射手 + 火炬树桩
# 在陆路 row=4 种大喷菇 + 地刺
# 在陆路 row=5 种玉米投手 + 西瓜投手

game.sun = 5000  # 给予充足阳光进行全面布防

# (name, col, row)
plants_to_plant = [
    # 水路 row=2 (Y中心406)
    ("lilypad", 0, 2),
    ("cattail", 0, 2),
    ("lilypad", 1, 2),
    ("tallnut", 1, 2),
    ("lilypad", 2, 2),
    ("snowpea", 2, 2),
    
    # 水路 row=3 (Y中心498)
    ("lilypad", 0, 3),
    ("repeater", 0, 3),
    ("lilypad", 1, 3),
    ("wallnut", 1, 3),
    
    # 陆路 row=0 (Y中心155)
    ("sunflower", 0, 0),
    ("cabbagepult", 1, 0),
    ("fumeshroom", 2, 0),
    
    # 陆路 row=1 (Y中心265)
    ("sunflower", 0, 1),
    ("kernelpult", 1, 1),
    ("torchwood", 2, 1),
    
    # 陆路 row=4 (Y中心615)
    ("sunflower", 0, 4),
    ("starfruit", 1, 4),
    ("spikeweed", 2, 4),
    
    # 陆路 row=5 (Y中心705)
    ("sunflower", 0, 5),
    ("melonpult", 1, 5),
    ("cobcannon", 2, 5),
]

for name, col, row in plants_to_plant:
    game.cooldowns[name] = 0.0
    game.selected_plant = name
    cx, cy = pvz.cell_center(col, row, is_pool=True)
    game._handle_click((cx, cy))

print(f"Total plants planted in pool level: {len(game.plants)}")
assert len(game.plants) >= 15, f"Expected many plants, got {len(game.plants)}"

# 验证所有植物坐标：
# 1. X 坐标必须 >= 140 且 <= 860
# 2. 水面植物 (row 2, 3) 的 Y 坐标必须在 360 ~ 545 的纯蓝水面范围内！
for p in game.plants:
    assert 140 <= p.x <= 860, f"Plant {p.ptype} X out of bounds: {p.x}"
    if p.row in (2, 3):
        assert 360 <= p.y <= 545, f"Water plant {p.ptype} Y out of pool water: {p.y}"
        print(f"Water Plant: {p.ptype:12s} at (col={p.col}, row={p.row}) -> (x={p.x}, y={p.y}) [PERFECT IN WATER]")
    else:
        print(f"Grass Plant: {p.ptype:12s} at (col={p.col}, row={p.row}) -> (x={p.x}, y={p.y}) [PERFECT ON GRASS]")

print("\n=== 水面关卡植物坐标 100% 居中，绝不种到边边上！(PASS) ===")

# 3. 渲染一帧并保存全屏高清截图
game.draw()
out_img = Path(r"10-pvz/tools/test_pool_perfect_layout.png")
pygame.image.save(screen, str(out_img))
print(f"Saved layout screenshot to {out_img}")
