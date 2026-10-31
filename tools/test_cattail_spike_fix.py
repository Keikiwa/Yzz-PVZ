# -*- coding: utf-8 -*-
"""Comprehensive verification of cattail spike retargeting & no residual bug."""

import os
import sys
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
sys.path.insert(0, str(Path(r"10-pvz")))

import pvz_ten_levels as pvz

pygame.init()
screen = pygame.display.set_mode((pvz.WIDTH, pvz.HEIGHT))
game = pvz.Game(screen, headless=True)

print("=" * 60)
print(">>> TESTING CATTAIL SPIKE RETARGETING & RESIDUAL FIX <<<")
print("=" * 60)

game.start_level(10)  # Pool level
game.mode = "playing"
game.zombies.clear()
game.plants.clear()
game.projectiles.clear()

# 1. 种一棵猫尾草
cattail = pvz.Plant("cattail", 1, 2, 300, 300, cell_h=game.cell_h, is_pool=True)
game.plants.append(cattail)

# 2. 放置两只僵尸：z1（前排近处），z2（后排远处）
z1 = pvz.Zombie("basic", 2, 500, 200, 200, 18.0, 28.0, cell_h=game.cell_h)
z2 = pvz.Zombie("cone", 1, 800, 290, 290, 17.0, 30.0, cell_h=game.cell_h)
game.zombies = [z1, z2]

# 3. 模拟猫尾草发射尖刺 (两枚尖刺瞄准 z1)
cattail.action_timer = 2.0
game._update_plants(0.1)
assert len(game.projectiles) == 2, f"Expected 2 cattail spikes, got {len(game.projectiles)}"
p1, p2 = game.projectiles[0], game.projectiles[1]
assert p1.target_zombie == z1, "Spike should initially target z1"

# 4. 让尖刺飞行一小段 (0.1秒)
game._update_projectiles(0.1)
initial_p1_x = p1.x
initial_p1_y = p1.y
print(f"Spike 1 in flight at ({initial_p1_x:.1f}, {initial_p1_y:.1f}) targeting z1")

# 5. 【核心测试点】：在尖刺击中 z1 之前，z1 突然被其他伤害击杀死亡！
z1.dead = True
print("Target z1 died suddenly in mid-flight!")

# 6. 继续更新游戏帧，验证尖刺是否智能重定向到存活的 z2，绝不停留！
game._update_projectiles(0.1)
assert p1.alive is True, "Spike should stay alive and seek new target"
assert p1.target_zombie == z2, "Spike should automatically retarget to z2!"
assert (p1.x != initial_p1_x or p1.y != initial_p1_y), "Spike MUST NOT freeze in place!"
print(f"-> Spike retargeted to z2 at ({p1.x:.1f}, {p1.y:.1f}) with angle {p1.angle:.1f}deg [PASS]")

# 7. 【核心测试点2】：若场上所有僵尸全部死亡，尖刺顺畅飞出屏幕自然消亡，绝不残留！
z2.dead = True
print("All remaining zombies killed!")
# 连续更新多次，尖刺必须继续飞行并飞出屏幕销毁
for step in range(50):
    game._update_projectiles(0.05)
    game._remove_dead()
    if not game.projectiles:
        break

assert len(game.projectiles) == 0, "Spikes should fly off screen and be cleanly destroyed, NOT residual!"
print("-> Spikes cleanly exited screen when no zombies left (Zero residuals!) [PASS]")

# 8. 【核心测试点3】：生存时间兜底保护
stray_spike = pvz.Projectile(500, 300, 2, 20.0, bullet_type="cattail_spike", is_homing=True)
game.projectiles = [stray_spike]
# 模拟经过 4.6 秒
for _ in range(50):
    stray_spike.update(0.1, game)
assert stray_spike.alive is False, "Stray spike should die after max lifespan (4.5s)!"
print("-> Max lifespan timeout protection verified! [PASS]")

# 9. 【核心测试点4】：气球僵尸击破测试
balloon_z = pvz.Zombie("balloon", 3, 700, 140, 140, 17.0, 28.0, cell_h=game.cell_h)
assert balloon_z.flying is True
game.zombies = [balloon_z]
test_spike = pvz.Projectile(680, balloon_z.y, 3, 20.0, bullet_type="cattail_spike", is_homing=True, target_zombie=balloon_z)
game.projectiles = [test_spike]
game._update_projectiles(0.05)
assert balloon_z.flying is False, "Cattail spike should pop balloon zombie!"
assert test_spike.alive is False, "Spike should be consumed on impact!"
print("-> Cattail spike successfully pops balloon zombie! [PASS]")

print("\n" + "=" * 60)
print(">>> ALL CATTAIL SPIKE TESTS PASSED 100%! NO RESIDUAL BUG! <<<")
print("=" * 60)
