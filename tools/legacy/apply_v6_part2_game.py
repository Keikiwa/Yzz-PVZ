# -*- coding: utf-8 -*-
"""apply_v6_part2_game.py:
Upgrade Game class in pvz_ten_levels.py:
- Fullscreen Canvas & Letterbox Projection & get_logical_mouse_pos
- Pool Grid get_cell_rect & 100% pixel-perfect ghost plant alignment
- Auto sun collect mechanism (unlocked after level 10, toggleable)
- Topright HUD 7-button layout without text overlap
"""

from pathlib import Path

pvz_main_path = Path("10-pvz/pvz_ten_levels.py")
with open(pvz_main_path, "r", encoding="utf-8") as f:
    code = f.read()

# -------------------------------------------------------------------------
# A. Game.__init__ setup: canvas, fullscreen, autosun & rects
# -------------------------------------------------------------------------
old_init_top = '''        self.screen = screen
        pvz_graphics.init_graphics()'''

new_init_top = '''        self.real_screen = screen
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.screen = self.canvas
        self.is_fullscreen = False
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        pvz_graphics.init_graphics()'''
code = code.replace(old_init_top, new_init_top, 1)

old_hud_rects = '''        self.topright_panel_rect = pygame.Rect(915, 10, 275, 80)
        self.speed_rect = pygame.Rect(925, 46, 48, 36)
        self.pause_rect = pygame.Rect(978, 46, 48, 36)
        self.shovel_rect = pygame.Rect(1031, 46, 48, 36)
        self.audio_rect = pygame.Rect(1084, 46, 48, 36)
        self.skip_rect = pygame.Rect(1137, 46, 48, 36)'''

new_hud_rects = '''        self.topright_panel_rect = pygame.Rect(825, 10, 365, 80)
        self.speed_rect = pygame.Rect(832, 46, 48, 36)
        self.pause_rect = pygame.Rect(883, 46, 48, 36)
        self.shovel_rect = pygame.Rect(934, 46, 48, 36)
        self.fullscreen_rect = pygame.Rect(985, 46, 48, 36)
        self.autosun_rect = pygame.Rect(1036, 46, 48, 36)
        self.audio_rect = pygame.Rect(1087, 46, 48, 36)
        self.skip_rect = pygame.Rect(1138, 46, 48, 36)
        self.auto_sun_unlocked = False
        self.auto_sun_enabled = True'''
code = code.replace(old_hud_rects, new_hud_rects, 1)

# -------------------------------------------------------------------------
# B. Methods: toggle_fullscreen, get_logical_mouse_pos, render_present, get_cell_rect
# -------------------------------------------------------------------------
old_begin_loop = '''    def begin_loop(self) -> None:
        while self.running:
            raw_dt = min(0.05, self.clock.tick(FPS) / 1000.0)
            self.time_value += raw_dt
            self.ambient += raw_dt
            self.handle_events()
            self.update(raw_dt)
            self.draw()
            pygame.display.flip()'''

new_begin_loop = '''    def get_logical_mouse_pos(self, pos: tuple[int, int] | None = None) -> tuple[int, int]:
        if pos is None:
            pos = pygame.mouse.get_pos()
        rx, ry = pos
        if not self.is_fullscreen or self.scale <= 0:
            return int(clamp(rx, 0, WIDTH)), int(clamp(ry, 0, HEIGHT))
        lx = (rx - self.offset_x) / self.scale
        ly = (ry - self.offset_y) / self.scale
        return int(clamp(lx, 0, WIDTH)), int(clamp(ly, 0, HEIGHT))

    def toggle_fullscreen(self) -> None:
        if self.headless:
            return
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            info = pygame.display.Info()
            sw, sh = max(WIDTH, info.current_w), max(HEIGHT, info.current_h)
            try:
                self.real_screen = pygame.display.set_mode((sw, sh), pygame.FULLSCREEN)
            except Exception:
                self.real_screen = pygame.display.set_mode((WIDTH, HEIGHT))
                self.is_fullscreen = False
                return
            self.scale = min(sw / WIDTH, sh / HEIGHT)
            draw_w = int(WIDTH * self.scale)
            draw_h = int(HEIGHT * self.scale)
            self.offset_x = (sw - draw_w) // 2
            self.offset_y = (sh - draw_h) // 2
        else:
            self.real_screen = pygame.display.set_mode((WIDTH, HEIGHT))
            self.scale = 1.0
            self.offset_x = 0
            self.offset_y = 0

    def render_present(self) -> None:
        if self.headless:
            return
        if self.is_fullscreen:
            self.real_screen.fill((0, 0, 0))
            draw_w = int(WIDTH * self.scale)
            draw_h = int(HEIGHT * self.scale)
            scaled = pygame.transform.smoothscale(self.canvas, (draw_w, draw_h))
            self.real_screen.blit(scaled, (self.offset_x, self.offset_y))
        else:
            self.real_screen.blit(self.canvas, (0, 0))
        pygame.display.flip()

    def get_cell_rect(self, col: int, row: int) -> pygame.Rect:
        if getattr(self, "is_pool", False):
            POOL_ROW_RANGES = [(95, 210), (210, 335), (335, 452), (452, 560), (560, 660), (660, 755)]
            r = max(0, min(5, row))
            top_y, bot_y = POOL_ROW_RANGES[r]
            gx = 140 + col * 80
            return pygame.Rect(gx, top_y, 80, bot_y - top_y)
        return pygame.Rect(GRID_X + col * CELL_W, GRID_Y + row * self.cell_h, CELL_W, self.cell_h)

    def begin_loop(self) -> None:
        while self.running:
            raw_dt = min(0.05, self.clock.tick(FPS) / 1000.0)
            self.time_value += raw_dt
            self.ambient += raw_dt
            self.handle_events()
            self.update(raw_dt)
            self.draw()
            self.render_present()'''
code = code.replace(old_begin_loop, new_begin_loop, 1)

# -------------------------------------------------------------------------
# C. handle_events: logical mouse coordinates & F11 / Alt+Enter keys
# -------------------------------------------------------------------------
old_handle_events = '''    def handle_events(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        # 快捷阳光吸附：鼠标滑过即可自动收集阳光
        if self.mode == "playing" and not self.overlay:
            for token in self.suns:
                if not token.collected and token.contains(mouse_pos):
                    self.collect_sun(token)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.selected_plant = None
                self.shovel_selected = False'''

new_handle_events = '''    def handle_events(self) -> None:
        mouse_pos = self.get_logical_mouse_pos()
        # 快捷阳光吸附：鼠标滑过即可自动收集阳光
        if self.mode == "playing" and not self.overlay:
            for token in self.suns:
                if not token.collected and token.contains(mouse_pos):
                    self.collect_sun(token)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_F11, pygame.K_f) or (event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT)):
                    self.toggle_fullscreen()
                else:
                    self._handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                log_pos = self.get_logical_mouse_pos(event.pos)
                self._handle_click(log_pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.selected_plant = None
                self.shovel_selected = False'''
code = code.replace(old_handle_events, new_handle_events, 1)

# -------------------------------------------------------------------------
# D. Key handling: C key toggles auto sun or collects all suns
# -------------------------------------------------------------------------
old_c_key = '''            elif key == pygame.K_c:
                self.selected_seeds.clear()
                self.audio.play("click")'''

new_c_key = '''            elif key == pygame.K_c:
                self.selected_seeds.clear()
                self.audio.play("click")'''
# Also handle C in playing mode
old_play_keys = '''        if self.mode == "playing":
            if key == pygame.K_SPACE:
                self.overlay = "paused" if not self.overlay else ""
                if self.overlay:
                    self.audio.pause_music()
                else:
                    self.audio.unpause_music()
                return'''

new_play_keys = '''        if self.mode == "playing":
            if key == pygame.K_c:
                if getattr(self, "auto_sun_unlocked", False):
                    self.auto_sun_enabled = not self.auto_sun_enabled
                    state_str = "【已开启】" if self.auto_sun_enabled else "【已关闭】"
                    self.float_text(600, 100, f"自动吸附阳光：{state_str}", C_GOLD)
                else:
                    # 未解锁自动吸附时，按 C 一键吸附场上全部阳光！
                    collected_any = False
                    for token in self.suns:
                        if not token.collected:
                            self.collect_sun(token)
                            collected_any = True
                    if collected_any:
                        self.float_text(600, 100, "一键阳光吸附！", C_GOLD)
                self.audio.play("collect")
                return
            if key == pygame.K_SPACE:
                self.overlay = "paused" if not self.overlay else ""
                if self.overlay:
                    self.audio.pause_music()
                else:
                    self.audio.unpause_music()
                return'''
code = code.replace(old_play_keys, new_play_keys, 1)

# -------------------------------------------------------------------------
# E. Update loop: auto collect sun & auto_sun_unlocked status check
# -------------------------------------------------------------------------
old_update_sun = '''        for token in self.suns:
            token.update(dt)'''

new_update_sun = '''        # 自动收集阳光检测 (第 10 关通关后解锁，用户可随时开/关)
        if not getattr(self, "auto_sun_unlocked", False):
            if "auto_sun_magnet" in self.artifacts or self.save_data.get("highest_level", 0) >= 9 or self.level_index >= 9:
                self.auto_sun_unlocked = True

        if getattr(self, "auto_sun_unlocked", False) and getattr(self, "auto_sun_enabled", True):
            for token in self.suns:
                if not token.collected and token.age >= 0.35:
                    self.collect_sun(token)

        for token in self.suns:
            token.update(dt)'''
code = code.replace(old_update_sun, new_update_sun, 1)

# -------------------------------------------------------------------------
# F. _handle_click: fullscreen_rect & autosun_rect
# -------------------------------------------------------------------------
old_click_ctrls = '''            if self.shovel_rect.collidepoint(pos):
                self.shovel_selected = not self.shovel_selected
                self.selected_plant = None
                return
            if self.audio_rect.collidepoint(pos):
                self.audio_on = not self.audio_on
                self.audio.enabled = self.audio_on
                self.audio.play("click")
                return'''

new_click_ctrls = '''            if self.shovel_rect.collidepoint(pos):
                self.shovel_selected = not self.shovel_selected
                self.selected_plant = None
                return
            if hasattr(self, "fullscreen_rect") and self.fullscreen_rect.collidepoint(pos):
                self.toggle_fullscreen()
                self.audio.play("click")
                return
            if hasattr(self, "autosun_rect") and self.autosun_rect.collidepoint(pos):
                if getattr(self, "auto_sun_unlocked", False):
                    self.auto_sun_enabled = not self.auto_sun_enabled
                    state_str = "【已开启】" if self.auto_sun_enabled else "【已关闭】"
                    self.float_text(600, 100, f"自动吸附阳光：{state_str}", C_GOLD)
                else:
                    for token in self.suns:
                        if not token.collected:
                            self.collect_sun(token)
                    self.float_text(600, 100, "一键阳光吸附！[第10关后永久全自动]", C_GOLD)
                self.audio.play("collect")
                return
            if self.audio_rect.collidepoint(pos):
                self.audio_on = not self.audio_on
                self.audio.enabled = self.audio_on
                self.audio.play("click")
                return'''
code = code.replace(old_click_ctrls, new_click_ctrls, 1)

# -------------------------------------------------------------------------
# G. Ghost Plant Preview Alignment (100% pixel-perfect for pool & grass)
# -------------------------------------------------------------------------
old_ghost_preview = '''        if self.selected_plant:
            mouse = pygame.mouse.get_pos()
            col, row = self._cell_at(mouse)
            if col is not None and row is not None:
                rect = pygame.Rect(GRID_X + col * CELL_W, GRID_Y + row * CELL_H, CELL_W, CELL_H)
                surface = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)
                pygame.draw.rect(surface, (255, 244, 151, 40), surface.get_rect(), border_radius=7)
                pygame.draw.rect(surface, (255, 239, 137, 145), surface.get_rect(), 3, border_radius=7)
                self.screen.blit(surface, rect)
                if self._plant_at(col, row) is None:
                    ghost = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)
                    draw_plant(ghost, self.selected_plant, (CELL_W / 2, CELL_H / 2), 0.75, self.time_value)
                    ghost.set_alpha(155)
                    self.screen.blit(ghost, rect)'''

new_ghost_preview = '''        if self.selected_plant:
            mouse = self.get_logical_mouse_pos()
            col, row = self._cell_at(mouse)
            if col is not None and row is not None:
                rect = self.get_cell_rect(col, row)
                surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.rect(surface, (255, 244, 151, 55), surface.get_rect(), border_radius=6)
                pygame.draw.rect(surface, (255, 239, 137, 180), surface.get_rect(), 3, border_radius=6)
                self.screen.blit(surface, rect)

                # 判定能否在此种植：
                is_water = getattr(self, "is_pool", False) and (row in getattr(self, "pool_rows", []))
                carrier = self._carrier_at(col, row)
                top_plant = self._top_plant_at(col, row)
                can_plant = False
                pname = self.selected_plant
                if is_water:
                    if pname == "lilypad" and carrier is None:
                        can_plant = True
                    elif pname == "cattail" and carrier is not None and top_plant == carrier:
                        can_plant = True
                    elif pname not in ("spikeweed", "potatomine", "lilypad") and carrier is not None and top_plant == carrier:
                        can_plant = True
                else:
                    if pname != "lilypad" and top_plant is None:
                        can_plant = True
                    elif pname == "gatlingpea" and top_plant and top_plant.ptype == "repeater":
                        can_plant = True
                    elif pname == "twinsunflower" and top_plant and top_plant.ptype == "sunflower":
                        can_plant = True

                cx, cy = cell_center(col, row, cell_h=self.cell_h, is_pool=self.is_pool)
                ghost = pygame.Surface((120, 120), pygame.SRCALPHA)
                draw_plant(ghost, pname, (60, 60), 0.75, self.time_value)
                ghost.set_alpha(175 if can_plant else 85)
                self.screen.blit(ghost, (cx - 60, cy - 60))
                if not can_plant:
                    pygame.draw.line(self.screen, (240, 70, 70, 210), (rect.x + 8, rect.y + 8), (rect.right - 8, rect.bottom - 8), 3)
                    pygame.draw.line(self.screen, (240, 70, 70, 210), (rect.right - 8, rect.y + 8), (rect.x + 8, rect.bottom - 8), 3)'''
code = code.replace(old_ghost_preview, new_ghost_preview, 1)

# -------------------------------------------------------------------------
# H. _draw_hud Controls (7 buttons, single line, no overlapping)
# -------------------------------------------------------------------------
old_hud_controls = '''        # Controls (单行清爽按钮，居中对齐，绝无任何文字重叠乱码)
        self._small_control(self.speed_rect, f"{self.game_speed:0.0f}x速", active=self.game_speed > 1.0)
        self._small_control(self.pause_rect, "暂停" if self.overlay != "paused" else "继续")
        self._small_control(self.shovel_rect, "铲子", active=self.shovel_selected)
        self._small_control(self.audio_rect, "音效" if self.audio_on else "静音", active=self.audio_on)
        self._small_control(self.skip_rect, "跳关", highlight=True)'''

new_hud_controls = '''        # Controls (7 个独立紧凑精致按钮，单行居中对齐，绝无任何文字重叠与乱码)
        self._small_control(self.speed_rect, f"{self.game_speed:0.0f}x速", active=self.game_speed > 1.0)
        self._small_control(self.pause_rect, "暂停" if self.overlay != "paused" else "继续")
        self._small_control(self.shovel_rect, "铲子", active=self.shovel_selected)
        self._small_control(self.fullscreen_rect, "全屏" if not self.is_fullscreen else "窗口")
        if getattr(self, "auto_sun_unlocked", False):
            self._small_control(self.autosun_rect, "自吸" if self.auto_sun_enabled else "手动", active=self.auto_sun_enabled)
        else:
            self._small_control(self.autosun_rect, "吸附")
        self._small_control(self.audio_rect, "音效" if self.audio_on else "静音", active=self.audio_on)
        self._small_control(self.skip_rect, "跳关", highlight=True)'''
code = code.replace(old_hud_controls, new_hud_controls, 1)

# Write back
with open(pvz_main_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Part 2: Game class upgrades applied successfully!")
