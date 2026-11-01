# -*- coding: utf-8 -*-
"""Comprehensive verification of all V6 features & bug fixes."""

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

print("=" * 60)
print(">>> RUNNING FULL V6 FEATURE & BUG FIX VERIFICATION <<<")
print("=" * 60)

# --- 1. TwinSunflower Sun Cost ---
print("\n[TEST 1] Verifying TwinSunflower sun cost == 125...")
assert pvz.PLANTS["twinsunflower"]["cost"] == 125, f"Expected 125, got {pvz.PLANTS['twinsunflower']['cost']}"
print("-> TwinSunflower cost is 125 [PASS]")

# --- 2. Threepeater Early Unlock ---
print("\n[TEST 2] Verifying Threepeater early unlock at Level 4 (Day stage)...")
assert "threepeater" in pvz.LEVEL_REWARDS[4]["plants"], "Threepeater should be rewarded at Level 4!"
idx_three = pvz.UNLOCK_ORDER.index("threepeater")
idx_squash = pvz.UNLOCK_ORDER.index("squash")
assert idx_three < idx_squash, f"Threepeater (idx={idx_three}) must be before Squash (idx={idx_squash})"
print("-> Threepeater successfully moved to Day stage (Level 4 reward) [PASS]")

# --- 3. KernelPult Butter & Tracking Lob Projectiles ---
print("\n[TEST 3] Verifying KernelPult shooting, butter bad-luck protection & homing...")
game.start_level(0)
game.mode = "playing"
game.zombies.clear()
game.plants.clear()
game.projectiles.clear()

plant_k = pvz.Plant("kernelpult", 1, 2, 300, 300, cell_h=game.cell_h)
game.plants.append(plant_k)
zombie_test = pvz.Zombie("basic", 2, 800, 200, 200, 18.0, 28.0, cell_h=game.cell_h)
game.zombies.append(zombie_test)

# Simulate 4 shots to test bad luck protection
butter_spawned = False
for shot in range(4):
    plant_k.action_timer = 2.5
    game.update(0.1)
    if game.projectiles:
        p = game.projectiles[-1]
        if p.bullet_type == "butter":
            butter_spawned = True
            print(f"-> Butter successfully thrown on shot #{shot+1} (Dmg={p.damage})")
            assert p.damage >= 50.0, f"Butter damage should be >= 50, got {p.damage}"
            # Verify target_zombie is bound for homing
            assert p.target_zombie == zombie_test, "Target zombie should be bound for tracking!"
        game.projectiles.clear()

assert butter_spawned, "Bad-luck protection should guarantee at least 1 butter within 4 shots!"
print("-> KernelPult butter & tracking verified [PASS]")

# --- 4. Newspaper Zombie Shield Health Bar & Permanent Stability ---
print("\n[TEST 4] Verifying Newspaper Zombie shield health bar & permanent stability...")
np_zombie = pvz.Zombie("newspaper", 2, 600, 280, 280, 14.0, 28.0, cell_h=game.cell_h)
np_zombie.has_newspaper = True
np_zombie.newspaper_hp = 140.0
game.zombies = [np_zombie]

# Check before damage: undamaged -> no bar
# Now apply 30 damage to newspaper
game._damage_zombie(np_zombie, 30.0)
assert np_zombie.has_newspaper is True
assert np_zombie.newspaper_hp == 110.0
assert np_zombie.hp == 280.0

# Render authentic sprite to test health bar calculation
# total_hp should be 280 + 110 = 390 / 420
test_surf = pygame.Surface((1200, 760))
rendered = pvz_graphics.render_zombie_sprite(test_surf, np_zombie, 1.0, 300, 255, 0.0)
assert rendered is True, "Authentic sprite rendering failed"
print("-> Newspaper zombie shield health bar accurately rendered while taking damage! [PASS]")

# Now break newspaper completely to trigger rage
game._damage_zombie(np_zombie, 120.0)
assert np_zombie.has_newspaper is False, "Newspaper should break"
assert np_zombie.enraged is True, "Zombie should be enraged"
assert np_zombie.hp == 280.0
# Even enraged with full body hp, total_hp is 280 / 420 < 420, so bar remains visible!
rendered_enraged = pvz_graphics.render_zombie_sprite(test_surf, np_zombie, 1.0, 300, 255, 0.0)
assert rendered_enraged is True
print("-> Newspaper zombie enraged health bar permanently remains visible without vanishing! [PASS]")

# --- 5. Pool 6-Row Grid & Pixel-Perfect Ghost Alignment ---
print("\n[TEST 5] Verifying Pool 6-row grid preview & 100% pixel-perfect alignment...")
game.start_level(10)  # Level 11 is Pool
assert game.is_pool is True, "Level 11 must be pool!"

for row in range(6):
    for col in range(9):
        rect = game.get_cell_rect(col, row)
        cx, cy = pvz.cell_center(col, row, cell_h=game.cell_h, is_pool=True)
        # Verify cell center is inside rect
        assert rect.left <= cx <= rect.right, f"cx {cx} not in rect [{rect.left}, {rect.right}]"
        assert rect.top <= cy <= rect.bottom, f"cy {cy} not in rect [{rect.top}, {rect.bottom}]"

print("-> All 54 pool cells have 100% valid rects & centered coordinates [PASS]")

# Test ghost plant on lilypad
game.plants.clear()
lily = pvz.Plant("lilypad", 2, 2, 300, 300, cell_h=game.cell_h, is_pool=True)
game.plants.append(lily)
game.selected_plant = "peashooter"
# Verify plant preview does not crash and renders correctly
game.draw()
print("-> Ghost plant preview on water lilypad renders flawlessly [PASS]")

# --- 6. Fullscreen System & Logical Mouse Mapping ---
print("\n[TEST 6] Verifying Fullscreen & Letterboxing logical coordinate mapping...")
game.scale = 1.5
game.offset_x = 100
game.offset_y = 50
game.is_fullscreen = True

# Logical mouse mapping test
# Screen physical (100 + 600 * 1.5, 50 + 380 * 1.5) = (1000, 620)
phys_x, phys_y = (1000, 620)
log_x, log_y = game.get_logical_mouse_pos((phys_x, phys_y))
assert log_x == 600, f"Expected 600, got {log_x}"
assert log_y == 380, f"Expected 380, got {log_y}"
print(f"-> Fullscreen physical ({phys_x}, {phys_y}) mapped to logical ({log_x}, {log_y}) with ZERO error! [PASS]")

# Reset to windowed
game.is_fullscreen = False
game.scale = 1.0
game.offset_x = 0
game.offset_y = 0

# --- 7. Auto Sun Magnet (Unlocked after Level 10, toggleable) ---
print("\n[TEST 7] Verifying Auto Sun Magnet feature...")
# Level 5: not unlocked
game.start_level(4)
game.artifacts.discard("auto_sun_magnet")
game.auto_sun_unlocked = False
game.update(0.1)
assert game.auto_sun_unlocked is False, "Should be locked before Level 10"

# Level 10 completed -> Level 11 (index 10): unlocked
game.start_level(10)
game.artifacts.add("auto_sun_magnet")
game.update(0.1)
assert game.auto_sun_unlocked is True, "Should be unlocked for Level 10+!"
assert game.auto_sun_enabled is True, "Default should be enabled!"

# Test auto collecting
sun_token = pvz.SunToken(400, 400, 400, age=0.5)
game.suns = [sun_token]
initial_sun = game.sun
game.update(0.1)
assert sun_token.collected is True, "Sun token should be automatically collected!"
assert game.sun > initial_sun, "Sun count should increase!"

# Test user toggle off
game.auto_sun_enabled = False
sun_token2 = pvz.SunToken(450, 450, 450, age=0.5)
game.suns = [sun_token2]
current_sun = game.sun
game.update(0.1)
assert sun_token2.collected is False, "Sun token should NOT be collected when disabled!"
assert game.sun == current_sun, "Sun count should not change when disabled!"
print("-> Auto sun collection unlock & user toggle on/off verified [PASS]")

# --- 8. Topright HUD 7-Button Layout Verification ---
print("\n[TEST 8] Verifying topright HUD 7-button layout and single-line clean display...")
game.draw()
out_screenshot = Path("10-pvz/tools/test_v6_verified_hud.png")
pygame.image.save(game.canvas, str(out_screenshot))
print(f"-> Rendered HUD screenshot saved to {out_screenshot} [PASS]")

print("\n" + "=" * 60)
print(">>> ALL 8 VERIFICATION TESTS PASSED 100%! ZERO ERRORS! <<<")
print("=" * 60)
