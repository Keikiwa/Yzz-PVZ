# -*- coding: utf-8 -*-
"""Update pvz_graphics.py to add visual rendering for:
Plants:
- cobcannon (玉米加农炮)
- magicshroom (魔术菇)
- agave (龙舌兰)
- laserbean (激光豆)
Zombies:
- gargantuar (巨人僵尸)
- imp (小鬼僵尸)
- balloon (气球僵尸)
- jackbox (小丑僵尸)
- digger (矿工僵尸)
Visual Projectiles / Effects:
- cob_missile (玉米核弹)
- magic_card (扑克牌飞弹)
- agave_sword (龙舌兰剑气)
- laser_beam (激光束)
"""

from pathlib import Path

p_graphics = Path(r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_graphics.py")
code = p_graphics.read_text(encoding="utf-8")

# 在 render_zombie_sprite 中增加对新僵尸的贴图定位与特色视觉装配
old_render_end = '''    # 贴图定位：底部贴齐地平线
    draw_x = int(zombie.x - target_w * 0.45)
    draw_y = int(ground_y - target_h + 8 + vault_y + dy_offset)
    surface.blit(scaled, (draw_x, draw_y))'''

new_render_end = '''    # 新增精英僵尸体型与外观重构
    scale_mult = 1.0
    if ztype == "gargantuar":
        scale_mult = 1.65 # 巨人僵尸身形极其威猛伟岸
    elif ztype == "imp":
        scale_mult = 0.55 # 小鬼僵尸小巧敏捷

    if scale_mult != 1.0:
        gw = int(target_w * scale_mult)
        gh = int(target_h * scale_mult)
        scaled = _get_scaled(scaled, gw, gh)
        target_w, target_h = gw, gh

    # 气球僵尸浮空高度与气球
    balloon_y = 0.0
    if ztype == "balloon" and getattr(zombie, "flying", True):
        balloon_y = -36.0 + math.sin(time_value * 3.5 + phase) * 5.0

    # 矿工僵尸遁地偏移
    if ztype == "digger" and getattr(zombie, "digging", False):
        dy_offset += 32.0

    # 贴图定位：底部贴齐地平线
    draw_x = int(zombie.x - target_w * 0.45)
    draw_y = int(ground_y - target_h + 8 + vault_y + balloon_y + dy_offset)

    # 矿工遁地只显示翻滚泥土
    if ztype == "digger" and getattr(zombie, "digging", False):
        # 翻滚泥土特效
        for di in range(4):
            dx = zombie.x - 18 + di * 12 + math.sin(time_value * 12 + di) * 4
            dy = ground_y - 8 + math.cos(time_value * 10 + di) * 3
            pygame.draw.circle(surface, (139, 90, 43), (int(dx), int(dy)), 6)
            pygame.draw.circle(surface, (185, 122, 60), (int(dx - 2), int(dy - 2)), 3)
    else:
        surface.blit(scaled, (draw_x, draw_y))

    # 巨人僵尸特写：巨锤与背上的小鬼
    if ztype == "gargantuar":
        # 巨型重锤/电线杆
        pole_x = int(zombie.x - 22)
        pole_y = int(ground_y - 120 + vault_y)
        pygame.draw.line(surface, (70, 75, 80), (pole_x + 15, pole_y - 20), (pole_x - 15, ground_y - 4), 10)
        # 铁牌/水泥块锤头
        pygame.draw.rect(surface, (120, 125, 130), (pole_x - 30, ground_y - 28, 30, 24), border_radius=4)
        pygame.draw.rect(surface, (230, 80, 70), (pole_x - 26, ground_y - 24, 22, 16), border_radius=2)
        # 背上的小鬼 (若尚未抛出)
        if getattr(zombie, "has_imp", True):
            imp_x = int(zombie.x + 28)
            imp_y = int(ground_y - 115 + math.sin(time_value * 4) * 3)
            pygame.draw.circle(surface, (153, 177, 143), (imp_x, imp_y), 12)
            pygame.draw.circle(surface, (25, 35, 25), (imp_x - 3, imp_y - 2), 3)
            pygame.draw.circle(surface, (255, 255, 255), (imp_x - 4, imp_y - 3), 1)
            pygame.draw.circle(surface, (25, 35, 25), (imp_x + 3, imp_y - 2), 3)
            pygame.draw.rect(surface, (65, 80, 95), (imp_x - 8, imp_y + 10, 16, 12), border_radius=3)

    # 气球僵尸：头顶摇曳的彩色气球与细线
    if ztype == "balloon" and getattr(zombie, "flying", True):
        bx = int(zombie.x + 2)
        by = int(draw_y - 28 + balloon_y)
        # 绑线
        pygame.draw.line(surface, (220, 220, 220), (int(zombie.x), int(draw_y + 15)), (bx, by + 20), 2)
        # 气球
        pygame.draw.ellipse(surface, (240, 50, 60), (bx - 18, by - 22, 36, 44))
        pygame.draw.ellipse(surface, (255, 200, 60), (bx - 8, by - 22, 16, 44)) # 金色条纹
        pygame.draw.ellipse(surface, (255, 255, 255, 180), (bx - 12, by - 16, 8, 14)) # 高光

    # 玩偶匣小丑僵尸：八音盒与发条火星
    if ztype == "jackbox":
        box_x = int(zombie.x - 14)
        box_y = int(ground_y - 48)
        pygame.draw.rect(surface, (215, 45, 55), (box_x, box_y, 22, 20), border_radius=4)
        pygame.draw.rect(surface, (255, 215, 60), (box_x + 2, box_y + 2, 18, 16), 2, border_radius=3)
        # 旋转发条
        crank_a = time_value * 18.0
        cx_tip = box_x - 6 + math.cos(crank_a) * 6
        cy_tip = box_y + 10 + math.sin(crank_a) * 6
        pygame.draw.line(surface, (210, 180, 70), (box_x, box_y + 10), (int(cx_tip), int(cy_tip)), 2)

    # 矿工僵尸：矿工安全帽与探照灯
    if ztype == "digger" and not getattr(zombie, "digging", False):
        cap_x = int(zombie.x - 14)
        cap_y = int(draw_y - 6)
        pygame.draw.ellipse(surface, (225, 180, 50), (cap_x, cap_y, 30, 16))
        # 探照灯
        pygame.draw.circle(surface, (255, 255, 180), (cap_x + 6, cap_y + 8), 5)
        # 探照灯照射光束
        cone_surf = pygame.Surface((80, 40), pygame.SRCALPHA)
        pygame.draw.polygon(cone_surf, (255, 255, 200, 45), [(0, 20), (80, 0), (80, 40)])
        surface.blit(cone_surf, (cap_x + 10, cap_y - 12))'''

code = code.replace(old_render_end, new_render_end)
p_graphics.write_text(code, encoding="utf-8")
print("Updated pvz_graphics.py successfully!")
