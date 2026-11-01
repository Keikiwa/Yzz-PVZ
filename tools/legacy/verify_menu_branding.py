# -*- coding: utf-8 -*-
"""测试主菜单渲染并截图，确保主界面标题文案更新为谦逊客观的复刻版标注。
"""
import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
sys.path.insert(0, r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz")

import pvz_ten_levels as pvz

pygame.init()
screen = pygame.display.set_mode((pvz.WIDTH, pvz.HEIGHT))
game = pvz.Game(screen, headless=True)

# 确保在主菜单状态
game.mode = "menu"
game.time_value = 1.0

# 绘制主菜单
game._draw_menu()

# 保存主菜单全屏截图
out_shot = r"F:\Desktop\.DeskBox\文件夹\反重力产出\图片\植物大战僵尸_主菜单界面.png"
pygame.image.save(screen, out_shot)
print(f"Saved main menu screenshot to: {out_shot}")

# 重点截取中央大字标题区域 (x: 200..1000, y: 20..130)
title_crop = screen.subsurface(pygame.Rect(200, 20, 800, 110))
crop_shot = r"F:\Desktop\.DeskBox\文件夹\反重力产出\图片\植物大战僵尸_主菜单标题特写.png"
pygame.image.save(title_crop, crop_shot)
print(f"Saved menu title crop to: {crop_shot}")

print("Menu verification complete!")
