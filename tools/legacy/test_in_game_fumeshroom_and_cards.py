# -*- coding: utf-8 -*-
"""在无头模式下启动真实游戏实例，选择大喷菇、高坚果、机枪射手、魅惑菇等重点植物，
种入草地和泳池中，截取游戏运行时的完整 1200x760 画面，验证卡槽阳光数值与场上立绘。
"""
import os, sys
sys.path.insert(0, r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz")
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
pygame.init()
pygame.display.set_mode((1200, 760))

import pvz_ten_levels as game

# 实例化游戏
app = game.Game()
app.state = "playing"
app.level_index = 10  # 泳池关卡（第11关）
app.sun = 9999        # 充沛阳光
app.selected_seeds = [
    "fumeshroom",     # 大喷菇 (75)
    "tallnut",        # 高坚果 (125)
    "gatlingpea",     # 机枪射手 (250)
    "hypnoshroom",    # 魅惑菇 (75)
    "doomshroom",     # 毁灭菇 (125)
    "starfruit",      # 杨桃 (125)
    "lilypad",        # 睡莲 (25)
    "cattail",        # 猫尾草 (225)
    "cobcannon",      # 玉米加农炮 (500)
    "laserbean"       # 激光豆 (200)
]
for k in app.selected_seeds:
    app.cooldowns[k] = 0.0

# 清空并初始化场地植物
app.plants.clear()

# 种植大喷菇在草地 (row 0, col 2)
p_fume = game.Plant("fumeshroom", 0, 2)
app.plants.append(p_fume)

# 种植高坚果在草地 (row 1, col 4)
p_tall = game.Plant("tallnut", 1, 4)
app.plants.append(p_tall)

# 种植机枪射手在草地 (row 4, col 2)
p_gat = game.Plant("gatlingpea", 4, 2)
app.plants.append(p_gat)

# 种植魅惑菇在草地 (row 5, col 3)
p_hypno = game.Plant("hypnoshroom", 5, 3)
app.plants.append(p_hypno)

# 种植杨桃在草地 (row 0, col 3)
p_star = game.Plant("starfruit", 0, 3)
app.plants.append(p_star)

# 种植睡莲与猫尾草在水面 (row 2, col 2)
p_lily1 = game.Plant("lilypad", 2, 2)
app.plants.append(p_lily1)
p_cat = game.Plant("cattail", 2, 2)
app.plants.append(p_cat)

# 种植睡莲与高坚果在水面 (row 3, col 3)
p_lily2 = game.Plant("lilypad", 3, 3)
app.plants.append(p_lily2)
p_tall2 = game.Plant("tallnut", 3, 3)
app.plants.append(p_tall2)

# 更新几帧以流转动画
for _ in range(10):
    app.time_value += 0.1
    for p in app.plants:
        p.update(0.1, app)

# 渲染画面
app.draw()

# 保存测试截图
out_shot = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\tools\test_fumeshroom_ingame_shot.png"
pygame.image.save(app.screen, out_shot)
print(f"Game rendered and screenshot saved to: {out_shot}")

# 重点切片检查：顶部卡牌区域 (y: 12..90, x: 140..900)
top_cards = app.screen.subsurface(pygame.Rect(140, 10, 760, 80))
pygame.image.save(top_cards, r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\tools\inspect_hud_cards_sun.png")

# 重点切片检查：大喷菇场上立绘区域
# fumeshroom at row 0, col 2:
grid = app.grid
cell_rect = app.cell_rect(0, 2)
print("Fumeshroom cell rect:", cell_rect)
fume_crop = app.screen.subsurface(cell_rect.inflate(20, 20))
pygame.image.save(fume_crop, r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\tools\inspect_ingame_fumeshroom.png")

print("All inspection crops saved successfully!")
