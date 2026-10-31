# -*- coding: utf-8 -*-
from pathlib import Path

p = Path("10-pvz/pvz_ten_levels.py")
text = p.read_text(encoding="utf-8")

old_code = '''    def _draw_overlays(self) -> None:
        if not self.overlay:
            return
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((17, 28, 23, 145))
        self.screen.blit(shade, (0, 0))

        if self.overlay == "paused":
            title, subtitle = "游戏暂停", "草坪暂时安静了下来"
            buttons = [
                (pygame.Rect(474, 476, 252, 52), "继续"),
                (pygame.Rect(474, 540, 252, 48), "重新开始"),
                (pygame.Rect(474, 600, 252, 48), "返回选关"),
            ]
        elif self.overlay == "won":
            title = f"第 {self.level_index + 1} 关完成"
            subtitle = "最后一只僵尸已被击退"
            next_label = "下一关" if self.level_index < len(LEVELS) - 1 else "回到第一关"
            buttons = [
                (pygame.Rect(470, 526, 252, 54), next_label),
                (pygame.Rect(470, 592, 252, 44), "返回选关"),
            ]
        else:
            title, subtitle = "草坪失守", self.lose_reason or "僵尸走进了房子"
            buttons = [
                (pygame.Rect(470, 526, 252, 54), "再试一次"),
                (pygame.Rect(470, 592, 252, 44), "返回选关"),
            ]

        box = pygame.Rect(410, 265, 380, 394 if len(buttons) == 3 else 330)
        panel(self.screen, box, (241, 230, 186), (66, 74, 46), radius=11, width=4)
        icon_y = 326
        if self.overlay == "won":
            for i in range(9):
                angle = self.overlay_age * 2 + i * math.tau / 9
                x = 600 + math.cos(angle) * 52
                y = icon_y + math.sin(angle) * 29
                pygame.draw.circle(self.screen, (246, 191, 53), (x, y), 7)
            draw_sun_shape(self.screen, (600, icon_y), 26, self.overlay_age)
        elif self.overlay == "lost":
            pygame.draw.circle(self.screen, (124, 78, 66), (600, icon_y), 45)
            draw_zombie(self.screen, Zombie("basic", 0, 600, 170, 170, 0, 0), self.time_value)
        else:
            pygame.draw.circle(self.screen, (114, 158, 89), (600, icon_y), 46)
            pygame.draw.rect(self.screen, C_CREAM, (582, 310, 11, 35), border_radius=4)
            pygame.draw.rect(self.screen, C_CREAM, (608, 310, 11, 35), border_radius=4)
        text(self.screen, title, self.fonts.get(36, True), (58, 64, 43), (600, 382), "center")
        text(self.screen, subtitle, self.fonts.get(17), (111, 104, 77), (600, 429), "center")
        for rect, label in buttons:
            hover = rect.collidepoint(pygame.mouse.get_pos())
            panel(
                self.screen, rect,
                (91, 157, 75) if not hover else (108, 179, 87),
                (45, 84, 48), radius=8, width=2, shadow=False,
            )
            text(self.screen, label, self.fonts.get(20, True), C_CREAM, rect.center, "center")'''

new_code = '''    def _draw_overlays(self) -> None:
        if not self.overlay:
            return
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((17, 28, 23, 145))
        self.screen.blit(shade, (0, 0))

        if self.overlay == "paused":
            title, subtitle = "游戏暂停", "草坪暂时安静了下来"
            buttons = [
                (pygame.Rect(474, 476, 252, 52), "继续"),
                (pygame.Rect(474, 540, 252, 48), "重新开始"),
                (pygame.Rect(474, 600, 252, 48), "返回选关"),
            ]
            box = pygame.Rect(410, 265, 380, 394)
        elif self.overlay == "won":
            title = f"第 {self.level_index + 1} 关 战役胜利！"
            subtitle = "所有僵尸已被全歼，草坪恢复平静！"
            next_label = "下一关" if self.level_index < len(LEVELS) - 1 else "回到第一关"
            buttons = [
                (pygame.Rect(470, 526, 252, 54), next_label),
                (pygame.Rect(470, 592, 252, 44), "返回选关"),
            ]
            box = pygame.Rect(350, 150, 500, 500)
        else:
            title, subtitle = "草坪失守", self.lose_reason or "僵尸走进了房子"
            buttons = [
                (pygame.Rect(470, 526, 252, 54), "再试一次"),
                (pygame.Rect(470, 592, 252, 44), "返回选关"),
            ]
            box = pygame.Rect(410, 265, 380, 330)

        panel(self.screen, box, (241, 230, 186), (66, 74, 46), radius=11, width=4)
        
        if self.overlay == "won":
            icon_y = 200
            for i in range(12):
                angle = self.overlay_age * 2 + i * math.tau / 12
                x = 600 + math.cos(angle) * 58
                y = icon_y + math.sin(angle) * 32
                pygame.draw.circle(self.screen, (255, 215, 60), (x, y), 6)
            draw_sun_shape(self.screen, (600, icon_y), 30, self.overlay_age)
            text(self.screen, title, self.fonts.get(32, True), (58, 64, 43), (600, 248), "center")
            text(self.screen, subtitle, self.fonts.get(15), (111, 104, 77), (600, 278), "center")

            # 战利品与神器结算展示面板
            rew = LEVEL_REWARDS.get(self.level_index, {})
            art_name = rew.get("artifact_name")
            art_desc = rew.get("artifact_desc")
            new_plants = rew.get("plants", [])

            reward_box = pygame.Rect(370, 302, 460, 206)
            panel(self.screen, reward_box, (255, 248, 224), (200, 155, 60), radius=9, width=2)

            if art_name:
                text(self.screen, f"⭐ 荣获通关神器：【{art_name}】 ⭐", self.fonts.get(18, True), (180, 95, 10), (600, 322), "center")
                text(self.screen, art_desc or "", self.fonts.get(12), (80, 60, 40), (600, 350), "center")
            
            if new_plants:
                p_names = "、".join(PLANTS.get(p, {}).get("name", p) for p in new_plants)
                text(self.screen, f"🌱 解锁全新植物：{p_names}", self.fonts.get(16, True), (42, 115, 48), (600, 385 if art_name else 335), "center")
                card_w, card_h = 50, 70
                total_w = len(new_plants) * (card_w + 12) - 12
                start_x = 600 - total_w // 2
                card_y = 412 if art_name else 365
                for i, p in enumerate(new_plants):
                    csurf = pvz_graphics.get_card_surface(p, (card_w, card_h))
                    if csurf:
                        self.screen.blit(csurf, (start_x + i * (card_w + 12), card_y))
        elif self.overlay == "lost":
            icon_y = 326
            pygame.draw.circle(self.screen, (124, 78, 66), (600, icon_y), 45)
            draw_zombie(self.screen, Zombie("basic", 0, 600, 170, 170, 0, 0), self.time_value)
            text(self.screen, title, self.fonts.get(36, True), (58, 64, 43), (600, 382), "center")
            text(self.screen, subtitle, self.fonts.get(17), (111, 104, 77), (600, 429), "center")
        else:
            icon_y = 326
            pygame.draw.circle(self.screen, (114, 158, 89), (600, icon_y), 46)
            pygame.draw.rect(self.screen, C_CREAM, (582, 310, 11, 35), border_radius=4)
            pygame.draw.rect(self.screen, C_CREAM, (608, 310, 11, 35), border_radius=4)
            text(self.screen, title, self.fonts.get(36, True), (58, 64, 43), (600, 382), "center")
            text(self.screen, subtitle, self.fonts.get(17), (111, 104, 77), (600, 429), "center")

        for rect, label in buttons:
            hover = rect.collidepoint(pygame.mouse.get_pos())
            panel(
                self.screen, rect,
                (91, 157, 75) if not hover else (108, 179, 87),
                (45, 84, 48), radius=8, width=2, shadow=False,
            )
            text(self.screen, label, self.fonts.get(20, True), C_CREAM, rect.center, "center")'''

assert old_code in text, "old_code not found in pvz_ten_levels.py"
text = text.replace(old_code, new_code)
p.write_text(text, encoding="utf-8")
print("OVERLAYS_UPDATED_SUCCESSFULLY")
