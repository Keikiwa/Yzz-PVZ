# -*- coding: utf-8 -*-
"""Test warp portal system, level jumping mechanics, and top-right control HUD cleanliness."""

import os
import sys
from pathlib import Path

# 设置无头环境
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
sys.path.insert(0, str(Path(r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz")))

import pvz_ten_levels as pvz

pygame.init()
screen = pygame.display.set_mode((pvz.WIDTH, pvz.HEIGHT))
game = pvz.Game(screen, headless=True)

print("=== 开始测试任意跳关系统与右上角控制面板 ===")

# --- 1. 验证右上角 5 个控制按钮布局 ---
print("\n--- 1. 检查右上角控制按钮布局 ---")
print(f"Top-right panel rect: {game.topright_panel_rect}")
print(f"Speed rect:  {game.speed_rect}")
print(f"Pause rect:  {game.pause_rect}")
print(f"Shovel rect: {game.shovel_rect}")
print(f"Audio rect:  {game.audio_rect}")
print(f"Skip rect:   {game.skip_rect}")

# 校验所有按钮均在面板内
assert game.topright_panel_rect.contains(game.speed_rect), "Speed rect not in panel!"
assert game.topright_panel_rect.contains(game.pause_rect), "Pause rect not in panel!"
assert game.topright_panel_rect.contains(game.shovel_rect), "Shovel rect not in panel!"
assert game.topright_panel_rect.contains(game.audio_rect), "Audio rect not in panel!"
assert game.topright_panel_rect.contains(game.skip_rect), "Skip rect not in panel!"

# 校验各个按钮互不重叠
btn_list = [game.speed_rect, game.pause_rect, game.shovel_rect, game.audio_rect, game.skip_rect]
for i in range(len(btn_list)):
    for j in range(i + 1, len(btn_list)):
        assert not btn_list[i].colliderect(btn_list[j]), f"Buttons {i} and {j} overlap!"
print("右上角 5 个按钮整齐对齐，完全在面板内且互不重叠！(PASS)")

# --- 2. 测试点击跳关按钮弹出传送门 ---
print("\n--- 2. 测试点击 [跳关] 按钮 ---")
game.start_level(0)
game.mode = "playing"
assert game.overlay == ""
# 模拟点击 skip_rect 中心
game._handle_click(game.skip_rect.center)
assert game.overlay == "warp", f"Expected overlay == 'warp', got {game.overlay}"
print(f"点击跳关按钮成功呼出传送门 overlay: {game.overlay} (PASS)")

# --- 3. 测试传送门渲染与关卡直达 ---
print("\n--- 3. 测试时空传送门 16 关卡直达 ---")
# 渲染一帧触发 warp_buttons 布局生成
game.draw()
assert len(game.warp_buttons) == 16, f"Expected 16 warp buttons, got {len(game.warp_buttons)}"
print(f"成功生成 16 个关卡穿梭按钮: {len(game.warp_buttons)} (PASS)")

# 模拟点击第 11 关（index=10，泳池关卡）
btn_rect_lvl11, idx11 = game.warp_buttons[10]
game._handle_click(btn_rect_lvl11.center)
assert game.level_index == 10, f"Expected level_index == 10, got {game.level_index}"
assert game.overlay == "", f"Expected overlay closed after warp, got {game.overlay}"
assert game.is_pool is True, "Level 11 should be pool environment!"

# 验证跳关后的植物战力自动补齐：包含睡莲等前置关卡战利品
avail = game.available_plants()
print(f"跳至第 11 关自动享有植物 ({len(avail)}种): {avail}")
assert "lilypad" in avail, "Jump to level 11 should automatically unlock lilypad!"
# 跳至第 12 关检验通关第 11 关战利品卷心菜投手
game.start_level(11)
avail12 = game.available_plants()
assert "cabbagepult" in avail12, "Level 12 should include cabbagepult!"
print("跳关自动补全对应关卡所需植物战利品验证通过！(PASS)")

# --- 4. 测试快捷键跳关 (Tab / N / P / L) ---
print("\n--- 4. 测试快捷键跳关 ---")
game.start_level(9) # 设定在第 10 关
assert game.level_index == 9

# 按 Tab: 9 -> 10 (第 11 关)
game._handle_key(pygame.K_TAB)
assert game.level_index == 10, f"Expected level 10, got {game.level_index}"
print(f"[Tab] 快捷键跳到下一关: 第 {game.level_index + 1} 关 (PASS)")

# 按 N: 10 -> 11 (第 12 关)
game._handle_key(pygame.K_n)
assert game.level_index == 11, f"Expected level 11, got {game.level_index}"
print(f"[N] 快捷键跳到下一关: 第 {game.level_index + 1} 关 (PASS)")

# 按 P: 11 -> 10 (第 11 关)
game._handle_key(pygame.K_p)
assert game.level_index == 10, f"Expected level 10, got {game.level_index}"
print(f"[P] 快捷键跳到上一关: 第 {game.level_index + 1} 关 (PASS)")

# 按 L: 打开传送门
game._handle_key(pygame.K_l)
assert game.overlay == "warp", f"Expected overlay == 'warp', got {game.overlay}"
print("[L] 快捷键成功呼出跳关传送门 (PASS)")

# 再次按 L: 关闭传送门
game._handle_key(pygame.K_l)
assert game.overlay == "", f"Expected overlay closed, got {game.overlay}"
print("[L] 快捷键再次按下成功关闭传送门 (PASS)")

# --- 5. 测试跳关至第 16 关无尽挑战 ---
print("\n--- 5. 测试跳关至第 16 关无尽挑战 ---")
game.start_level(15)
avail16 = game.available_plants()
print(f"第 16 关无尽挑战解锁植物数量: {len(avail16)} 种")
assert len(avail16) >= 34, f"Endless should have all plants, got {len(avail16)}"
assert "cobcannon" in avail16, "Cobcannon should be available in endless!"
assert "magicshroom" in avail16, "Magicshroom should be available in endless!"
assert "agave" in avail16, "Agave should be available in endless!"
assert "laserbean" in avail16, "Laserbean should be available in endless!"
assert "master_belt" in game.artifacts, "Master belt should be unlocked in endless!"
print("跳至第 16 关全植物与神器大满贯验证通过！(PASS)")

# --- 6. 生成视觉验证截图 ---
print("\n--- 6. 生成视觉截图 ---")
# a. 普通战斗中的右上角面板
game.start_level(0)
game.mode = "playing"
game.draw()
topright_crop = screen.subsurface(pygame.Rect(900, 0, 300, 100)).copy()
pygame.image.save(topright_crop, r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\tools\inspect_clean_topright.png")
print("右上角清晰面板特写已保存: inspect_clean_topright.png")

# b. 传送门全屏界面
game.overlay = "warp"
game.draw()
pygame.image.save(screen, r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\tools\inspect_warp_portal.png")
print("跳关传送门全屏截图已保存: inspect_warp_portal.png")

print("\n=== 所有跳关功能与右上角清晰度验证 100% PASS！ ===")
