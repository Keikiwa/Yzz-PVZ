# -*- coding: utf-8 -*-
"""深度性能分析脚本
模拟在有数十棵植物、几十只僵尸、子弹、特效的典型战场环境下运行，
利用 cProfile 定位到底是什么导致了卡顿和低帧率。
"""
import os, sys, time, cProfile, pstats
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
sys.path.insert(0, r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz")

import pvz_ten_levels as pvz
import pvz_graphics

pygame.init()
screen = pygame.display.set_mode((pvz.WIDTH, pvz.HEIGHT))
game = pvz.Game(screen, headless=True)

# 模拟真实战场场景：泳池关卡，满场植物与大量僵尸
game.start_level(10)
game.mode = "playing"
game.sun = 9999

# 种植 25 棵植物
for r in range(6):
    for c in range(4):
        if r in (2, 3):
            # 水面
            game.plants.append(pvz.Plant("lilypad", c, r, 300, 300, is_pool=True))
            game.plants.append(pvz.Plant("cattail" if c == 0 else "tallnut", c, r, 300, 300, is_pool=True))
        else:
            game.plants.append(pvz.Plant("peashooter" if c == 0 else "repeater", c, r, 300, 300, is_pool=True))

# 刷入 30 只僵尸
for i in range(30):
    z = pvz.Zombie(
        ztype="normal" if i % 3 == 0 else ("bucket" if i % 3 == 1 else "cone"),
        row=i % 6,
        x=800 + (i * 20),
        hp=270,
        max_hp=270,
        speed=24.0,
        damage=100.0,
        is_pool=True
    )
    game.zombies.append(z)

# 产生 50 颗子弹
for i in range(50):
    proj = pvz.Projectile(
        bullet_type="pea",
        x=200 + i * 15,
        y=150 + (i % 6) * 90,
        damage=20.0,
        speed=360.0,
        row=i % 6
    )
    game.projectiles.append(proj)

# 预热几帧
for _ in range(5):
    game.time_value += 0.016
    game.update(0.016)
    game.draw()

print("=== 开始 cProfile 性能热点采样 (运行 120 帧) ===")
pr = cProfile.Profile()
pr.enable()

start_t = time.perf_counter()
frame_times = []
for frame in range(120):
    t0 = time.perf_counter()
    game.time_value += 0.016
    game.update(0.016)
    game.draw()
    t1 = time.perf_counter()
    frame_times.append((t1 - t0) * 1000.0)

total_t = time.perf_counter() - start_t
pr.disable()

avg_frame_ms = sum(frame_times) / len(frame_times)
max_frame_ms = max(frame_times)
min_frame_ms = min(frame_times)
est_fps = 1000.0 / avg_frame_ms if avg_frame_ms > 0 else 9999

print(f"总耗时: {total_t:.3f}s | 平均每帧: {avg_frame_ms:.2f}ms (折合 FPS: {est_fps:.1f})")
print(f"最大帧耗时: {max_frame_ms:.2f}ms | 最小帧耗时: {min_frame_ms:.2f}ms")

print("\n--- 耗时最高的前 25 个函数调用 ---")
stats = pstats.Stats(pr)
stats.sort_stats("cumulative")
stats.print_stats(25)

print("\n--- 自身纯耗时 (tottime) 最高的前 20 个函数 ---")
stats.sort_stats("tottime")
stats.print_stats(20)
