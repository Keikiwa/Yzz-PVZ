# -*- coding: utf-8 -*-
"""Modal and overlay renderers (Pause, Victory Award, and Game Over)."""

import pygame
from typing import Optional
from domain.model.session import Session
from domain.spec.rewards import LevelReward
from domain.spec.plants import PLANTS
from infra.pygame_fonts import get_font
from infra.sprites import get_sprites


def render_pause(surface: pygame.Surface) -> dict[str, pygame.Rect]:
    # Dim overlay
    dim = pygame.Surface((1200, 760), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 160))
    surface.blit(dim, (0, 0))

    box = pygame.Rect(420, 200, 360, 340)
    pygame.draw.rect(surface, (45, 34, 25), box, border_radius=12)
    pygame.draw.rect(surface, (160, 120, 60), box, 3, border_radius=12)

    font_large = get_font(32, bold=True)
    font_mid = get_font(20, bold=True)

    t_lbl = font_large.render("游戏暂停", True, (255, 230, 90))
    surface.blit(t_lbl, (box.x + (box.width - t_lbl.get_width()) // 2, box.y + 30))

    buttons: dict[str, pygame.Rect] = {}

    resume_btn = pygame.Rect(box.x + 60, box.y + 100, 240, 50)
    buttons["resume"] = resume_btn
    pygame.draw.rect(surface, (60, 130, 50), resume_btn, border_radius=8)
    pygame.draw.rect(surface, (140, 220, 100), resume_btn, 2, border_radius=8)
    r_lbl = font_mid.render("继续游戏", True, (255, 255, 255))
    surface.blit(r_lbl, (resume_btn.x + (resume_btn.width - r_lbl.get_width()) // 2, resume_btn.y + 12))

    restart_btn = pygame.Rect(box.x + 60, box.y + 165, 240, 50)
    buttons["restart"] = restart_btn
    pygame.draw.rect(surface, (120, 80, 40), restart_btn, border_radius=8)
    pygame.draw.rect(surface, (220, 160, 90), restart_btn, 2, border_radius=8)
    rs_lbl = font_mid.render("重新开始", True, (255, 255, 255))
    surface.blit(rs_lbl, (restart_btn.x + (restart_btn.width - rs_lbl.get_width()) // 2, restart_btn.y + 12))

    menu_btn = pygame.Rect(box.x + 60, box.y + 230, 240, 50)
    buttons["menu"] = menu_btn
    pygame.draw.rect(surface, (110, 50, 45), menu_btn, border_radius=8)
    pygame.draw.rect(surface, (220, 120, 100), menu_btn, 2, border_radius=8)
    m_lbl = font_mid.render("返回主菜单", True, (255, 255, 255))
    surface.blit(m_lbl, (menu_btn.x + (menu_btn.width - m_lbl.get_width()) // 2, menu_btn.y + 12))

    return buttons


def render_victory(surface: pygame.Surface, reward: Optional[LevelReward]) -> dict[str, pygame.Rect]:
    dim = pygame.Surface((1200, 760), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 180))
    surface.blit(dim, (0, 0))

    box = pygame.Rect(320, 120, 560, 500)
    pygame.draw.rect(surface, (35, 55, 30), box, border_radius=14)
    pygame.draw.rect(surface, (255, 220, 70), box, 4, border_radius=14)

    font_huge = get_font(36, bold=True)
    font_mid = get_font(18, bold=True)
    font_small = get_font(14)
    sprites = get_sprites()

    t_lbl = font_huge.render("关卡胜利！", True, (255, 235, 80))
    surface.blit(t_lbl, (box.x + (box.width - t_lbl.get_width()) // 2, box.y + 25))

    curr_y = box.y + 85
    # Show reward plants
    if reward and reward.plants:
        p_title = font_mid.render("解锁新植物：", True, (200, 255, 180))
        surface.blit(p_title, (box.x + 40, curr_y))
        curr_y += 35

        for p_id in reward.plants:
            spec = PLANTS.get(p_id)
            if not spec:
                continue
            card = sprites.get_card(p_id, (54, 68))
            if card:
                surface.blit(card, (box.x + 50, curr_y))
            name_txt = font_mid.render(spec.name, True, (255, 240, 120))
            surface.blit(name_txt, (box.x + 120, curr_y + 6))
            tip_txt = font_small.render(spec.tip[:28], True, (220, 230, 210))
            surface.blit(tip_txt, (box.x + 120, curr_y + 36))
            curr_y += 80

    # Show reward artifact
    if reward and reward.artifact:
        a_title = font_mid.render(f"获得神器：{reward.artifact_name}", True, (255, 215, 0))
        surface.blit(a_title, (box.x + 40, curr_y))
        curr_y += 30
        desc_txt = font_small.render(reward.artifact_desc[:32], True, (255, 230, 160))
        surface.blit(desc_txt, (box.x + 40, curr_y))
        curr_y += 60

    buttons: dict[str, pygame.Rect] = {}
    next_btn = pygame.Rect(box.x + 80, box.bottom - 80, 180, 50)
    buttons["next_level"] = next_btn
    pygame.draw.rect(surface, (60, 140, 50), next_btn, border_radius=8)
    pygame.draw.rect(surface, (160, 240, 120), next_btn, 2, border_radius=8)
    nxt_lbl = font_mid.render("下一关", True, (255, 255, 255))
    surface.blit(nxt_lbl, (next_btn.x + (next_btn.width - nxt_lbl.get_width()) // 2, next_btn.y + 14))

    menu_btn = pygame.Rect(box.right - 260, box.bottom - 80, 180, 50)
    buttons["menu"] = menu_btn
    pygame.draw.rect(surface, (110, 60, 45), menu_btn, border_radius=8)
    pygame.draw.rect(surface, (220, 140, 100), menu_btn, 2, border_radius=8)
    m_lbl = font_mid.render("返回主菜单", True, (255, 255, 255))
    surface.blit(m_lbl, (menu_btn.x + (menu_btn.width - m_lbl.get_width()) // 2, menu_btn.y + 14))

    return buttons


def render_game_over(surface: pygame.Surface) -> dict[str, pygame.Rect]:
    dim = pygame.Surface((1200, 760), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 200))
    surface.blit(dim, (0, 0))

    box = pygame.Rect(380, 220, 440, 300)
    pygame.draw.rect(surface, (50, 25, 25), box, border_radius=12)
    pygame.draw.rect(surface, (220, 60, 50), box, 3, border_radius=12)

    font_huge = get_font(36, bold=True)
    font_mid = get_font(20, bold=True)

    t_lbl = font_huge.render("僵尸吃掉了你的脑子！", True, (255, 90, 80))
    surface.blit(t_lbl, (box.x + (box.width - t_lbl.get_width()) // 2, box.y + 40))

    buttons: dict[str, pygame.Rect] = {}
    retry_btn = pygame.Rect(box.x + 50, box.y + 150, 160, 50)
    buttons["retry"] = retry_btn
    pygame.draw.rect(surface, (120, 60, 40), retry_btn, border_radius=8)
    pygame.draw.rect(surface, (240, 140, 90), retry_btn, 2, border_radius=8)
    rt_lbl = font_mid.render("重新再战", True, (255, 255, 255))
    surface.blit(rt_lbl, (retry_btn.x + (retry_btn.width - rt_lbl.get_width()) // 2, retry_btn.y + 12))

    menu_btn = pygame.Rect(box.right - 210, box.y + 150, 160, 50)
    buttons["menu"] = menu_btn
    pygame.draw.rect(surface, (70, 70, 70), menu_btn, border_radius=8)
    pygame.draw.rect(surface, (160, 160, 160), menu_btn, 2, border_radius=8)
    m_lbl = font_mid.render("返回主菜单", True, (255, 255, 255))
    surface.blit(m_lbl, (menu_btn.x + (menu_btn.width - m_lbl.get_width()) // 2, menu_btn.y + 12))

    return buttons
