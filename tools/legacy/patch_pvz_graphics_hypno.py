# -*- coding: utf-8 -*-
path = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_graphics.py"

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

target1 = """    # 尺寸缩放适配 (原版僵尸高约 118 像素)
    bw, bh = frame.get_size()"""

replacement1 = """    # 魅惑僵尸水平翻转（调头向右冲锋）
    is_hypno = getattr(zombie, "hypnotized", False)
    if is_hypno:
        frame = pygame.transform.flip(frame, True, False)

    # 尺寸缩放适配 (原版僵尸高约 118 像素)
    bw, bh = frame.get_size()"""

target2 = """    else:
        surface.blit(scaled, (draw_x, draw_y))"""

replacement2 = """    else:
        surface.blit(scaled, (draw_x, draw_y))
        if is_hypno and alpha >= 180:
            glow_surf = pygame.Surface((target_w, target_h), pygame.SRCALPHA)
            glow_a = int(55 + 25 * math.sin(time_value * 7.0))
            pygame.draw.ellipse(glow_surf, (255, 120, 240, glow_a), glow_surf.get_rect())
            surface.blit(glow_surf, (draw_x, draw_y), special_flags=pygame.BLEND_RGBA_ADD)"""

assert target1 in code, "target1 not found"
assert target2 in code, "target2 not found"

code = code.replace(target1, replacement1, 1)
code = code.replace(target2, replacement2, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("Successfully patched pvz_graphics.py for hypno flip and aura!")
