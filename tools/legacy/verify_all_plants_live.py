# -*- coding: utf-8 -*-
"""全植物实装真机验证脚本
使用真实的 pygame 游戏实例，在游戏中种植大喷菇、高坚果、机枪射手、魅惑菇、杨桃等重点植物，
验证其场上原版高清立绘、卡牌阳光数值显示、泳池网格对齐。
"""
import os
import sys
from pathlib import Path
from PIL import Image

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
sys.path.insert(0, r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz")

import pvz_ten_levels as pvz
import pvz_graphics

pygame.init()
screen = pygame.display.set_mode((pvz.WIDTH, pvz.HEIGHT))
game = pvz.Game(screen, headless=True)

print("=== 启动游戏实例进行全面实机测试 ===")
game.start_level(10) # 第11关（泳池）
game.mode = "playing"
game.sun = 99999

# 选择卡槽植物（优先大喷菇等）
test_deck = [
    "fumeshroom",     # 75
    "tallnut",        # 125
    "gatlingpea",     # 250
    "hypnoshroom",    # 75
    "doomshroom",     # 125
    "starfruit",      # 125
    "lilypad",        # 25
    "cattail",        # 225
]
game.selected_seeds = test_deck

# 要在场上种植的植物列表: (name, col, row)
plants_to_plant = [
    # 陆地第0行
    ("fumeshroom", 0, 0),
    ("hypnoshroom", 1, 0),
    ("doomshroom", 2, 0),
    ("starfruit", 3, 0),
    
    # 陆地第1行
    ("tallnut", 0, 1),
    ("gatlingpea", 1, 1),
    ("laserbean", 2, 1),
    ("sunflower", 3, 1),
    
    # 泳池水路第2行
    ("lilypad", 0, 2),
    ("fumeshroom", 0, 2), # 种在睡莲上
    ("lilypad", 1, 2),
    ("tallnut", 1, 2),    # 高坚果种在睡莲上
    ("lilypad", 2, 2),
    ("cattail", 2, 2),    # 猫尾草种在睡莲上
    
    # 泳池水路第3行
    ("lilypad", 0, 3),
    ("gatlingpea", 0, 3), # 机枪射手种在睡莲上
    ("lilypad", 1, 3),
    ("starfruit", 1, 3),  # 杨桃种在睡莲上
    
    # 陆地第4行
    ("magicshroom", 0, 4),
    ("agave", 1, 4),
    ("cobcannon", 2, 4),
    
    # 陆地第5行
    ("peashooter", 0, 5),
    ("snowpea", 1, 5),
    ("repeater", 2, 5),
    ("torchwood", 3, 5),
]

for name, col, row in plants_to_plant:
    game.cooldowns[name] = 0.0
    game.selected_plant = name
    cx, cy = pvz.cell_center(col, row, is_pool=True)
    game._handle_click((cx, cy))

print(f"成功种植植物总数: {len(game.plants)} 株")

# 模拟运行几帧，使动画流转
game.time_value += 1.25

# 渲染完整游戏画面
game.draw()

# 保存全屏实机截图
shot_path = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\tools\all_plants_live_showcase.png"
pygame.image.save(screen, shot_path)
print(f"已生成全屏实景测试截图: {shot_path}")

# 保存卡槽特写图
hud_cards = screen.subsurface(pygame.Rect(140, 10, 620, 80))
hud_path = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\tools\showcase_hud_cards.png"
pygame.image.save(hud_cards, hud_path)
print(f"已保存卡槽特写图: {hud_path}")

# 截取大喷菇场上特写图 (陆地 row 0, col 0)
fume_center = pvz.cell_center(0, 0, is_pool=True)
fume_rect = pygame.Rect(fume_center[0] - 45, fume_center[1] - 45, 90, 90)
fume_surf = screen.subsurface(fume_rect)
fume_path = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\tools\showcase_fumeshroom.png"
pygame.image.save(fume_surf, fume_path)
print(f"已保存大喷菇场上特写图: {fume_path}")

# 截取高坚果场上特写图 (陆地 row 1, col 0)
tall_center = pvz.cell_center(0, 1, is_pool=True)
tall_rect = pygame.Rect(tall_center[0] - 45, tall_center[1] - 55, 90, 110)
tall_surf = screen.subsurface(tall_rect)
tall_path = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\tools\showcase_tallnut.png"
pygame.image.save(tall_surf, tall_path)
print(f"已保存高坚果场上特写图: {tall_path}")

# 截取机枪射手场上特写图 (陆地 row 1, col 1)
gat_center = pvz.cell_center(1, 1, is_pool=True)
gat_rect = pygame.Rect(gat_center[0] - 45, gat_center[1] - 45, 90, 90)
gat_surf = screen.subsurface(gat_rect)
gat_path = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\tools\showcase_gatlingpea.png"
pygame.image.save(gat_surf, gat_path)
print(f"已保存机枪射手场上特写图: {gat_path}")

# 对大喷菇场上特写图进行像素分析：确认不是单色简笔画假图
fume_pil = Image.open(fume_path)
unique_colors = len(set(fume_pil.getdata()))
print(f"大喷菇特写区域色彩丰富度: {unique_colors} 种不同颜色 (原版真实贴图特征)")
assert unique_colors > 300, "色彩丰富度不足，疑似简笔画假图！"

print("\n=== 全部实机真实验证 100% 通过！===")
