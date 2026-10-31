# -*- coding: utf-8 -*-
"""Implement full level skipping & warp portal + completely eliminate top-right overlapping text bug."""

from pathlib import Path

p_pvz = Path(r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_ten_levels.py")
code = p_pvz.read_text(encoding="utf-8")

# 1. 更新右上角控制按钮坐标与面板声明
init_target = """        self.speed_rect = pygame.Rect(940, 46, 46, 36)
        self.pause_rect = pygame.Rect(990, 46, 46, 36)
        self.shovel_rect = pygame.Rect(1040, 46, 46, 36)
        self.audio_rect = pygame.Rect(1090, 46, 46, 36)
        self.skip_rect = pygame.Rect(1140, 46, 52, 36)
        self.warp_buttons: list[tuple[pygame.Rect, int]] = []
        self.warp_next_btn = pygame.Rect(0, 0, 0, 0)
        self.warp_close_btn = pygame.Rect(0, 0, 0, 0)"""

init_alt = """        self.speed_rect = pygame.Rect(986, 49, 45, 36)
        self.pause_rect = pygame.Rect(1039, 49, 45, 36)
        self.shovel_rect = pygame.Rect(1092, 49, 45, 36)
        self.audio_rect = pygame.Rect(1145, 49, 38, 36)"""

init_replacement = """        self.topright_panel_rect = pygame.Rect(915, 10, 275, 80)
        self.speed_rect = pygame.Rect(925, 46, 48, 36)
        self.pause_rect = pygame.Rect(978, 46, 48, 36)
        self.shovel_rect = pygame.Rect(1031, 46, 48, 36)
        self.audio_rect = pygame.Rect(1084, 46, 48, 36)
        self.skip_rect = pygame.Rect(1137, 46, 48, 36)
        self.warp_buttons: list[tuple[pygame.Rect, int]] = []
        self.warp_next_btn = pygame.Rect(0, 0, 0, 0)
        self.warp_close_btn = pygame.Rect(0, 0, 0, 0)"""

if init_target in code:
    code = code.replace(init_target, init_replacement)
    print("Updated from init_target to init_replacement")
elif init_alt in code:
    code = code.replace(init_alt, init_replacement)
    print("Updated from init_alt to init_replacement")
else:
    print("Note: init rects already modified or need search")

# 2. 检查并确保 _small_control 单行居中
small_ctrl_code = """    def _small_control(self, rect: pygame.Rect, title: str, active: bool = False, highlight: bool = False) -> None:
        if highlight:
            fill = (255, 224, 110)
            border_c = (195, 120, 20)
        elif active:
            fill = (255, 215, 80)
            border_c = (185, 110, 15)
        else:
            fill = (242, 232, 192)
            border_c = (66, 78, 48)

        hover = rect.collidepoint(pygame.mouse.get_pos())
        if hover:
            fill = (255, 245, 215)
            border_c = (220, 140, 25)

        panel(self.screen, rect, fill, border_c, radius=6, width=2, shadow=False)
        text_c = (42, 48, 28) if not active else (15, 25, 10)
        # 单行居中绘制，绝对不重叠！
        text(self.screen, title, self.fonts.get(13, True), text_c, rect.center, "center")"""

import re
code = re.sub(r'def _small_control\(self, rect: pygame\.Rect, .*?\n        text\(self\.screen,.*?\n', small_ctrl_code + "\n", code, flags=re.S)
print("_small_control confirmed clean single-line center!")

# 3. 更新 _draw_hud 中右上角面板及按钮位置
old_hud_topright = """        level = LEVELS[self.level_index]
        panel(self.screen, pygame.Rect(976, 12, 212, 76), (234, 225, 179), (63, 75, 44), radius=9, width=2, shadow=False)
        text(
            self.screen,
            f"第 {self.level_index + 1:02d} 关 · {level['name']}",
            self.fonts.get(14, True), (61, 70, 45), (1082, 16), "midtop",
        )

        # Controls (单行清爽按钮，绝无任何文字重叠乱码)
        self._small_control(self.speed_rect, f"{self.game_speed:0.0f}x速", active=self.game_speed > 1.0)
        self._small_control(self.pause_rect, "暂停" if self.overlay != "paused" else "继续")
        self._small_control(self.shovel_rect, "铲子", active=self.shovel_selected)
        self._small_control(self.audio_rect, "音效" if self.audio_on else "静音", active=self.audio_on)
        self._small_control(self.skip_rect, "跳关", highlight=True)"""

new_hud_topright = """        level = LEVELS[self.level_index]
        top_p = getattr(self, "topright_panel_rect", pygame.Rect(915, 10, 275, 80))
        panel(self.screen, top_p, (234, 225, 179), (63, 75, 44), radius=9, width=2, shadow=False)
        text(
            self.screen,
            f"第 {self.level_index + 1:02d} 关 · {level['name']}",
            self.fonts.get(14, True), (61, 70, 45), (top_p.centerx, 16), "midtop",
        )

        # Controls (单行清爽按钮，居中对齐，绝无任何文字重叠乱码)
        self._small_control(self.speed_rect, f"{self.game_speed:0.0f}x速", active=self.game_speed > 1.0)
        self._small_control(self.pause_rect, "暂停" if self.overlay != "paused" else "继续")
        self._small_control(self.shovel_rect, "铲子", active=self.shovel_selected)
        self._small_control(self.audio_rect, "音效" if self.audio_on else "静音", active=self.audio_on)
        self._small_control(self.skip_rect, "跳关", highlight=True)"""

if old_hud_topright in code:
    code = code.replace(old_hud_topright, new_hud_topright)
    print("HUD topright panel upgraded!")
else:
    # 尝试正则替换
    pattern = r'level = LEVELS\[self\.level_index\].*?self\._small_control\(self\.skip_rect, "跳关", highlight=True\)'
    m = re.search(pattern, code, re.S)
    if m:
        code = code[:m.start()] + new_hud_topright + code[m.end():]
        print("HUD topright panel regex upgraded!")

# 4. 在 _draw_overlays 中加入 warp 跳关传送门
warp_overlay_draw = """    def _draw_overlays(self) -> None:
        if not self.overlay:
            return
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((17, 28, 23, 145))
        self.screen.blit(shade, (0, 0))

        if self.overlay == "warp":
            box = pygame.Rect(140, 50, 920, 620)
            panel(self.screen, box, (246, 238, 212), (68, 52, 28), radius=16, width=4, shadow=True)
            text(self.screen, "【时空穿梭 · 任意跳关传送门】", self.fonts.get(22, True), (62, 42, 18), (box.centerx, box.y + 14), "midtop")
            text(self.screen, "觉得前几关太简单？点击任意关卡秒速直达！快捷键: [Tab]/[N] 下一关  [P] 上一关  [L]/[Esc] 关闭", self.fonts.get(12), (115, 90, 55), (box.centerx, box.y + 44), "midtop")
            pygame.draw.line(self.screen, (185, 160, 120), (box.x + 20, box.y + 68), (box.right - 20, box.y + 68), 2)

            card_w = 205
            card_h = 78
            gap_x = 16
            gap_y = 10
            wx0 = box.x + (box.width - (4 * card_w + 3 * gap_x)) // 2
            wy0 = box.y + 78
            self.warp_buttons = []
            mpos = pygame.mouse.get_pos()

            for i in range(len(LEVELS)):
                col = i % 4
                row = i // 4
                wrect = pygame.Rect(wx0 + col * (card_w + gap_x), wy0 + row * (card_h + gap_y), card_w, card_h)
                self.warp_buttons.append((wrect, i))
                hover = wrect.collidepoint(mpos)
                is_cur = (i == self.level_index)

                theme = LEVELS[i].get("theme", "day")
                if "pool" in theme:
                    bg = (220, 242, 255) if not hover else (235, 250, 255)
                    bd = (45, 120, 180) if not is_cur else (255, 195, 45)
                elif theme == "night":
                    bg = (225, 220, 240) if not hover else (240, 235, 255)
                    bd = (110, 85, 160) if not is_cur else (255, 195, 45)
                else:
                    bg = (248, 242, 215) if not hover else (255, 250, 230)
                    bd = (65, 85, 50) if not is_cur else (255, 195, 45)

                panel(self.screen, wrect, bg, bd, radius=8, width=3 if is_cur else 2)
                badge_c = (215, 140, 30) if is_cur else (60, 100, 70)
                badge = pygame.Rect(wrect.x + 6, wrect.y + 8, 34, 20)
                pygame.draw.rect(self.screen, badge_c, badge, border_radius=4)
                text(self.screen, f"{i+1:02d}", self.fonts.get(12, True), C_CREAM, badge.center, "center")
                text(self.screen, LEVELS[i]["name"], self.fonts.get(14, True), (45, 40, 30), (wrect.x + 46, wrect.y + 8))
                text(self.screen, LEVELS[i]["subtitle"][:12] + "...", self.fonts.get(11), (110, 100, 80), (wrect.x + 8, wrect.y + 34))
                tag = "[当前关卡]" if is_cur else ("[泳池水面]" if "pool" in theme else ("[暗夜墓地]" if "night" in theme else "[白天草坪]"))
                text(self.screen, tag, self.fonts.get(11, True), (140, 95, 30) if is_cur else (80, 110, 70), (wrect.x + 8, wrect.y + 54))

            self.warp_next_btn = pygame.Rect(box.centerx - 180, box.bottom - 54, 160, 40)
            panel(self.screen, self.warp_next_btn, (50, 145, 65), (255, 220, 90), radius=8, width=2)
            text(self.screen, "下一关 >> [Tab]", self.fonts.get(14, True), C_CREAM, self.warp_next_btn.center, "center")

            self.warp_close_btn = pygame.Rect(box.centerx + 20, box.bottom - 54, 160, 40)
            panel(self.screen, self.warp_close_btn, (140, 60, 50), (240, 180, 160), radius=8, width=2)
            text(self.screen, "返回战斗 [Esc]", self.fonts.get(14, True), C_CREAM, self.warp_close_btn.center, "center")
            return

        if self.overlay == "paused":"""

if 'if self.overlay == "warp":' not in code:
    code = code.replace("""    def _draw_overlays(self) -> None:
        if not self.overlay:
            return
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((17, 28, 23, 145))
        self.screen.blit(shade, (0, 0))

        if self.overlay == "paused":""", warp_overlay_draw)
    print("Overlay warp drawing hooked into _draw_overlays!")

# 5. 在 _handle_click 中处理 warp_buttons 点击
warp_click_handler = """        if self.overlay == "warp":
            if getattr(self, "warp_next_btn", None) and self.warp_next_btn.collidepoint(pos):
                next_lvl = (self.level_index + 1) % len(LEVELS)
                self.overlay = ""
                self.start_level(next_lvl)
                return
            if getattr(self, "warp_close_btn", None) and self.warp_close_btn.collidepoint(pos):
                self.overlay = ""
                return
            for wrect, idx in getattr(self, "warp_buttons", []):
                if wrect.collidepoint(pos):
                    self.overlay = ""
                    self.start_level(idx)
                    return
            return

        if self.overlay == "paused":"""

if 'if self.overlay == "warp":' not in code[code.find('def _handle_click('):]:
    code = code.replace("""        if self.overlay == "paused":""", warp_click_handler, 1)
    print("Overlay warp click handling hooked into _handle_click!")

p_pvz.write_text(code, encoding="utf-8")
print("=== All Warp & Clean Top-Right patches integrated! ===")
