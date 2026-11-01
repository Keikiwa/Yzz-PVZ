# -*- coding: utf-8 -*-
"""Battlefield Renderer.
Draws lawn maps, cell highlights, mowers, carriers, plants, zombies, projectiles,
suns, combat particles, screen shake, and floating damage numbers.
"""

import math
import random
import pygame
from typing import Optional
from domain.model.world import World
from domain.model.session import Session
from domain.spec.levels import LEVELS
from infra.sprites import get_sprites
from infra.pygame_fonts import get_font


def render_battle(
    surface: pygame.Surface,
    world: World,
    session: Session,
    mouse_pos: tuple[float, float],
) -> None:
    sprites = get_sprites()
    font_small = get_font(14, bold=True)
    font_bold = get_font(18, bold=True)

    level_idx = session.current_level_idx
    level_spec = LEVELS[level_idx] if 0 <= level_idx < len(LEVELS) else LEVELS[0]
    theme = level_spec.theme

    # 1. Screen Shake impulse
    ox, oy = world.shake.update(0.0)

    # 2. Lawn / Pool Map Background
    map_surf = sprites.get_map(theme)
    if map_surf:
        surface.blit(map_surf, (ox, oy))
    else:
        # Procedural grass & pool fallback
        surface.fill((48, 120, 52))
        if level_spec.is_pool:
            pool_y1 = world.layout.get_row_center_y(2) - 48
            pool_y2 = world.layout.get_row_center_y(3) + 48
            pygame.draw.rect(surface, (40, 110, 180), (world.layout.grid_x, pool_y1, world.layout.grid_w, pool_y2 - pool_y1))

    # 3. Cell Hover Highlight (Guaranteed Pixel-Perfect Alignment)
    mx, my = mouse_pos
    col, row = world.layout.pos_to_cell(mx, my)
    if col is not None and row is not None:
        if session.active_seed_idx is not None or session.active_shovel:
            cx, cy, cw, ch = world.layout.get_cell_rect(col, row)
            highlight_color = (255, 235, 60, 90) if session.active_seed_idx is not None else (255, 100, 80, 90)
            hs = pygame.Surface((cw, ch), pygame.SRCALPHA)
            hs.fill(highlight_color)
            surface.blit(hs, (cx + ox, cy + oy))
            pygame.draw.rect(surface, (255, 240, 100), (cx + ox, cy + oy, cw, ch), 2)

    # 4. Lawnmowers and Pool Cleaners
    for m in world.mowers:
        if m.active:
            m_surf = sprites.get_mower(is_pool=m.is_pool)
            if m_surf:
                surface.blit(m_surf, (m.x - 32 + ox, m.y - 26 + oy))
            else:
                pygame.draw.rect(surface, (200, 50, 40), (m.x - 25 + ox, m.y - 20 + oy, 50, 40), border_radius=6)

    # 5. Carriers (Lilypads)
    for (c, r), carrier in world.carriers.items():
        if carrier.is_alive:
            sprites.render_plant(
                surface, "lilypad", (carrier.x + ox, carrier.y + oy),
                scale=carrier.scale, time_val=world.game_time, hp_ratio=1.0, age=carrier.age, plant=carrier
            )

    # 6. Plants
    for (c, r), plant in world.plants.items():
        if not plant.is_alive:
            continue

        sprites.render_plant(
            surface, plant.spec_id, (plant.x + ox, plant.y + oy),
            scale=plant.scale, time_val=world.game_time,
            hp_ratio=plant.hp / plant.max_hp, age=plant.age, plant=plant
        )

        # Health bar if damaged
        if plant.hp < plant.max_hp:
            bar_w = 46
            bar_h = 6
            bx = plant.x - bar_w // 2 + ox
            by = plant.y - 48 + oy
            ratio = max(0.0, plant.hp / plant.max_hp)
            pygame.draw.rect(surface, (30, 30, 30), (bx, by, bar_w, bar_h))
            pygame.draw.rect(surface, (60, 220, 60), (bx, by, int(bar_w * ratio), bar_h))

    # 7. Zombies (Sorted by Row and X for Proper Depth Layering)
    sorted_zombies = sorted(world.zombies, key=lambda z: (z.row, -z.x))
    for z in sorted_zombies:
        if not z.is_alive:
            continue

        # Hypno glowing halo
        if z.hypnotized:
            pygame.draw.circle(surface, (200, 100, 255), (int(z.x + ox), int(z.y - 30 + oy)), 38, 3)

        sprites.render_zombie(surface, z, time_val=world.game_time, ground_y=z.y + oy)

        # Butter pat on head when butter-stunned!
        if z.butter_timer > 0:
            bx = z.x - 14 + ox
            by = z.y - 74 + oy
            pygame.draw.rect(surface, (255, 230, 80), (bx, by, 28, 14), border_radius=3)
            pygame.draw.rect(surface, (200, 170, 40), (bx, by, 28, 14), 2, border_radius=3)

        # Health Bar: ALWAYS VISIBLE when damaged, solves the disappearance bug!
        if z.health_ratio < 1.0:
            bar_w = 54
            bar_h = 7
            bx = z.x - bar_w // 2 + ox
            by = z.y - 88 + oy
            pygame.draw.rect(surface, (20, 20, 20), (bx - 1, by - 1, bar_w + 2, bar_h + 2), border_radius=2)
            pygame.draw.rect(surface, (180, 40, 30), (bx, by, bar_w, bar_h))
            pygame.draw.rect(surface, (60, 220, 70), (bx, by, int(bar_w * z.health_ratio), bar_h))

    # 8. Projectiles
    for p in world.projectiles:
        if not p.alive:
            continue

        if p.bullet_type == "butter":
            # Yellow butter chunk
            pygame.draw.rect(surface, (255, 235, 90), (p.x - 10 + ox, p.y - 8 + oy, 20, 16), border_radius=3)
            pygame.draw.rect(surface, (210, 180, 50), (p.x - 10 + ox, p.y - 8 + oy, 20, 16), 1, border_radius=3)
        elif p.bullet_type in ("melon", "wintermelon"):
            col = (140, 230, 255) if p.bullet_type == "wintermelon" else (70, 170, 60)
            pygame.draw.circle(surface, col, (int(p.x + ox), int(p.y + oy)), 15)
            pygame.draw.circle(surface, (30, 80, 25), (int(p.x + ox), int(p.y + oy)), 15, 2)
        elif p.bullet_type == "spike":
            # Cattail needle
            pygame.draw.line(surface, (220, 100, 140), (p.x - 8 + ox, p.y + oy), (p.x + 8 + ox, p.y + oy), 3)
        else:
            is_freeze = (p.bullet_type == "snowpea")
            b_surf = sprites.get_bullet(p.bullet_type, is_freeze=is_freeze, size=24)
            if b_surf:
                surface.blit(b_surf, (p.x - 12 + ox, p.y - 12 + oy))
            else:
                col = (120, 220, 255) if is_freeze else (255, 120, 30) if p.bullet_type == "firepea" else (140, 230, 60)
                pygame.draw.circle(surface, col, (int(p.x + ox), int(p.y + oy)), 8)

    # 9. Suns
    for s in world.suns:
        if s.state == "collected":
            continue
        sun_surf = sprites.get_sun(world.game_time + s.id, radius=s.radius)
        if sun_surf:
            surface.blit(sun_surf, (s.x - s.radius + ox, s.y - s.radius + oy))
        else:
            pygame.draw.circle(surface, (255, 235, 60), (int(s.x + ox), int(s.y + oy)), int(s.radius))

    # 10. Combat Particles & Floating Texts
    for pt in world.particles:
        if pt.alive:
            pygame.draw.circle(surface, pt.color, (int(pt.x + ox), int(pt.y + oy)), int(pt.size))

    for ft in world.floating_texts:
        if ft.alive:
            txt_surf = font_bold.render(ft.text, True, ft.color)
            txt_surf.set_alpha(ft.alpha)
            surface.blit(txt_surf, (ft.x + ox, ft.y + oy))
