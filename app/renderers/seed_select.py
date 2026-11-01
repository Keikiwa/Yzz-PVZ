# -*- coding: utf-8 -*-
"""Seed Selection Screen Renderer.
Allows players to customize their plant deck from unlocked blueprints before entering battle.
"""

import pygame
from domain.model.session import Session
from domain.spec.plants import PLANTS
from domain.spec.rewards import UNLOCK_ORDER
from infra.pygame_fonts import get_font
from infra.sprites import get_sprites


def render_seed_select(
    surface: pygame.Surface, session: Session, mouse_pos: tuple[float, float]
) -> dict[str, pygame.Rect]:
    surface.fill((30, 22, 16))

    font_large = get_font(26, bold=True)
    font_mid = get_font(18, bold=True)
    font_small = get_font(12, bold=True)
    sprites = get_sprites()

    buttons: dict[str, pygame.Rect] = {}

    # Title
    t_surf = font_large.render(f"选择出战植物 (已选 {len(session.selected_seeds)}/{session.max_seed_slots})", True, (255, 230, 100))
    surface.blit(t_surf, (1200 // 2 - t_surf.get_width() // 2, 20))

    # Top Tray: Current Selected Seeds
    tray_rect = pygame.Rect(100, 65, 1000, 96)
    pygame.draw.rect(surface, (45, 34, 25), tray_rect, border_radius=8)
    pygame.draw.rect(surface, (140, 105, 60), tray_rect, 2, border_radius=8)

    slot_w = 64
    slot_h = 80
    slot_gap = 12
    start_x = tray_rect.x + (tray_rect.width - (session.max_seed_slots * (slot_w + slot_gap) - slot_gap)) // 2

    for i in range(session.max_seed_slots):
        sx = start_x + i * (slot_w + slot_gap)
        sy = tray_rect.y + 8
        s_rect = pygame.Rect(sx, sy, slot_w, slot_h)
        pygame.draw.rect(surface, (30, 20, 15), s_rect, border_radius=6)
        pygame.draw.rect(surface, (80, 60, 40), s_rect, 1, border_radius=6)

        if i < len(session.selected_seeds):
            spec_id = session.selected_seeds[i]
            buttons[f"tray_{i}"] = s_rect
            card_surf = sprites.get_card(spec_id, (slot_w, slot_h))
            if card_surf:
                surface.blit(card_surf, (sx, sy))
            else:
                pygame.draw.rect(surface, (60, 120, 50), s_rect, border_radius=6)
                name_lbl = font_small.render(spec_id[:4], True, (255, 255, 255))
                surface.blit(name_lbl, (sx + 4, sy + 6))

    # Bottom Catalog: All Unlocked Plants
    cat_rect = pygame.Rect(100, 185, 1000, 460)
    pygame.draw.rect(surface, (40, 30, 22), cat_rect, border_radius=8)
    pygame.draw.rect(surface, (120, 90, 50), cat_rect, 2, border_radius=8)

    unlocked_list = [p for p in UNLOCK_ORDER if p in session.unlocked_plants]
    cols = 9
    card_w = 64
    card_h = 80
    gap_x = 18
    gap_y = 12
    cat_start_x = cat_rect.x + (cat_rect.width - (cols * (card_w + gap_x) - gap_x)) // 2
    cat_start_y = cat_rect.y + 20

    for idx, p_id in enumerate(unlocked_list):
        c = idx % cols
        r = idx // cols
        cx = cat_start_x + c * (card_w + gap_x)
        cy = cat_start_y + r * (card_h + gap_y)
        c_rect = pygame.Rect(cx, cy, card_w, card_h)

        is_chosen = p_id in session.selected_seeds
        buttons[f"catalog_{p_id}"] = c_rect

        card_surf = sprites.get_card(p_id, (card_w, card_h))
        if card_surf:
            surface.blit(card_surf, (cx, cy))
        else:
            pygame.draw.rect(surface, (50, 90, 45), c_rect, border_radius=6)
            name_lbl = font_small.render(p_id[:4], True, (255, 255, 255))
            surface.blit(name_lbl, (cx + 4, cy + 6))

        if is_chosen:
            # Darkened check overlay
            mask = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 140))
            surface.blit(mask, (cx, cy))
            pygame.draw.rect(surface, (255, 220, 60), c_rect, 2, border_radius=6)

    # Action Buttons: Start Battle & Smart Auto-Fill
    start_btn = pygame.Rect(500, 665, 200, 55)
    buttons["start_battle"] = start_btn
    can_start = len(session.selected_seeds) > 0
    bg_col = (60, 140, 50) if can_start else (60, 60, 60)
    pygame.draw.rect(surface, bg_col, start_btn, border_radius=8)
    pygame.draw.rect(surface, (255, 240, 100) if can_start else (100, 100, 100), start_btn, 2, border_radius=8)
    st_lbl = font_mid.render("开始迎战!", True, (255, 255, 255) if can_start else (160, 160, 160))
    surface.blit(st_lbl, (start_btn.x + (start_btn.width - st_lbl.get_width()) // 2, start_btn.y + 16))

    auto_btn = pygame.Rect(260, 665, 160, 55)
    buttons["auto_fill"] = auto_btn
    pygame.draw.rect(surface, (60, 80, 110), auto_btn, border_radius=8)
    pygame.draw.rect(surface, (140, 180, 240), auto_btn, 2, border_radius=8)
    af_lbl = font_mid.render("智能推荐", True, (255, 255, 255))
    surface.blit(af_lbl, (auto_btn.x + (auto_btn.width - af_lbl.get_width()) // 2, auto_btn.y + 16))

    back_btn = pygame.Rect(780, 665, 160, 55)
    buttons["back"] = back_btn
    pygame.draw.rect(surface, (110, 60, 50), back_btn, border_radius=8)
    pygame.draw.rect(surface, (220, 140, 120), back_btn, 2, border_radius=8)
    bk_lbl = font_mid.render("返回主菜单", True, (255, 255, 255))
    surface.blit(bk_lbl, (back_btn.x + (back_btn.width - bk_lbl.get_width()) // 2, back_btn.y + 16))

    return buttons
