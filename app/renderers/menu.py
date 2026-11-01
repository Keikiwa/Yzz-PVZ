# -*- coding: utf-8 -*-
"""Main Menu and Level Selection Renderer."""

import pygame
from domain.model.session import Session
from domain.spec.levels import LEVELS
from infra.pygame_fonts import get_font


def render_menu(surface: pygame.Surface, session: Session, mouse_pos: tuple[float, float]) -> dict[str, pygame.Rect]:
    """Renders main menu and returns clickable button rects."""
    surface.fill((28, 42, 24))

    font_huge = get_font(42, bold=True)
    font_large = get_font(26, bold=True)
    font_mid = get_font(18, bold=True)
    font_small = get_font(14, bold=True)

    # Title Banner
    title_surf = font_huge.render("植物大战僵尸 · 全新重构增强版", True, (245, 220, 100))
    surface.blit(title_surf, (1200 // 2 - title_surf.get_width() // 2, 45))

    sub_surf = font_small.render("Clean Architecture · 零绝对路径 · 34 种植物 · 15 种僵尸 · 16 大关卡", True, (180, 200, 160))
    surface.blit(sub_surf, (1200 // 2 - sub_surf.get_width() // 2, 100))

    buttons: dict[str, pygame.Rect] = {}

    # Level Selection Grid (4 x 4 = 16 levels)
    grid_start_x = 160
    grid_start_y = 150
    btn_w = 200
    btn_h = 70
    gap_x = 26
    gap_y = 20

    for idx, lvl in enumerate(LEVELS):
        col = idx % 4
        row = idx // 4
        bx = grid_start_x + col * (btn_w + gap_x)
        by = grid_start_y + row * (btn_h + gap_y)
        rect = pygame.Rect(bx, by, btn_w, btn_h)

        is_unlocked = idx <= session.highest_level
        is_selected = idx == session.current_level_idx

        if is_unlocked:
            buttons[f"level_{idx}"] = rect
            bg_col = (50, 110, 45) if is_selected else (35, 75, 32)
            border_col = (255, 230, 80) if is_selected else (80, 160, 70)
            text_col = (255, 245, 200)
        else:
            bg_col = (40, 45, 40)
            border_col = (70, 75, 70)
            text_col = (120, 125, 120)

        pygame.draw.rect(surface, bg_col, rect, border_radius=8)
        pygame.draw.rect(surface, border_col, rect, 3 if is_selected else 2, border_radius=8)

        # Level number & Name
        prefix = f"第 {idx + 1} 关: " if not lvl.is_endless else "生存: "
        name_txt = font_mid.render(f"{prefix}{lvl.name}", True, text_col)
        surface.blit(name_txt, (bx + 12, by + 12))

        # Subtitle or Lock status
        sub_text = lvl.subtitle if is_unlocked else "尚未解锁"
        sub_rendered = font_small.render(sub_text[:12], True, (180, 190, 170) if is_unlocked else (100, 105, 100))
        surface.blit(sub_rendered, (bx + 12, by + 40))

    # Bottom Action Buttons
    start_btn = pygame.Rect(380, 560, 200, 60)
    buttons["start"] = start_btn
    pygame.draw.rect(surface, (70, 150, 50), start_btn, border_radius=10)
    pygame.draw.rect(surface, (255, 240, 120), start_btn, 3, border_radius=10)
    st_lbl = font_large.render("进入战斗", True, (255, 255, 255))
    surface.blit(st_lbl, (start_btn.x + (start_btn.width - st_lbl.get_width()) // 2, start_btn.y + 14))

    endless_btn = pygame.Rect(620, 560, 200, 60)
    buttons["endless"] = endless_btn
    pygame.draw.rect(surface, (150, 70, 50), endless_btn, border_radius=10)
    pygame.draw.rect(surface, (255, 180, 100), endless_btn, 3, border_radius=10)
    ed_lbl = font_large.render("无尽模式", True, (255, 255, 255))
    surface.blit(ed_lbl, (endless_btn.x + (endless_btn.width - ed_lbl.get_width()) // 2, endless_btn.y + 14))

    # Hints & shortcuts bar
    hint_txt = font_small.render("按 [F11] 全屏切换 | [空格] 暂停 | [A] 自动吸阳光开关 | [1-8] 快捷选卡", True, (160, 180, 150))
    surface.blit(hint_txt, (1200 // 2 - hint_txt.get_width() // 2, 680))

    return buttons
