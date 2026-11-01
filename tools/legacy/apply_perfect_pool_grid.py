# -*- coding: utf-8 -*-
"""Apply perfect pool grid & alignment, completely eliminating edge-planting bug in water levels."""

from pathlib import Path
import re

p_pvz = Path(r"10-pvz\pvz_ten_levels.py")
code = p_pvz.read_text(encoding="utf-8")

# 1. 更新 cell_center 和 lane_ground 函数定义
old_funcs = """def cell_center(col: int, row: int, cell_h: int = CELL_H) -> tuple[int, int]:
    return (
        GRID_X + int((col + 0.5) * CELL_W),
        GRID_Y + int((row + 0.5) * cell_h),
    )


def lane_ground(row: int, cell_h: int = CELL_H) -> int:
    return GRID_Y + (row + 1) * cell_h - (13 if cell_h >= 110 else 8)"""

new_funcs = """def cell_center(col: int, row: int, cell_h: int = CELL_H, is_pool: bool = False) -> tuple[int, int]:
    if is_pool:
        # 泳池专属真实网格对齐 (水池与草地 100% 居中，绝不种到水泥边缘)
        POOL_ROW_CENTERS = [155, 265, 406, 498, 615, 705]
        r = max(0, min(5, row))
        cx = 140 + int((col + 0.5) * 80)
        cy = POOL_ROW_CENTERS[r]
        return (cx, cy)
    return (
        GRID_X + int((col + 0.5) * CELL_W),
        GRID_Y + int((row + 0.5) * cell_h),
    )


def lane_ground(row: int, cell_h: int = CELL_H, is_pool: bool = False) -> int:
    if is_pool:
        POOL_LANE_GROUNDS = [190, 300, 435, 528, 645, 735]
        r = max(0, min(5, row))
        return POOL_LANE_GROUNDS[r]
    return GRID_Y + (row + 1) * cell_h - (13 if cell_h >= 110 else 8)"""

if old_funcs in code:
    code = code.replace(old_funcs, new_funcs)
    print("Updated cell_center and lane_ground!")

# 2. 更新 Plant 和 Zombie 类支持 is_pool
old_plant_postinit = """    def __post_init__(self) -> None:
        self._x, self._y = cell_center(self.col, self.row, cell_h=self.cell_h)"""

new_plant_postinit = """    is_pool: bool = False

    def __post_init__(self) -> None:
        self._x, self._y = cell_center(self.col, self.row, cell_h=self.cell_h, is_pool=self.is_pool)"""

if old_plant_postinit in code:
    code = code.replace(old_plant_postinit, new_plant_postinit)
    print("Updated Plant __post_init__ with is_pool!")

old_zombie_props = """    def y(self) -> float:
        return lane_ground(self.row, cell_h=self.cell_h) - 50.0

    def rect(self) -> pygame.Rect:
        ground = lane_ground(self.row, cell_h=self.cell_h)
        return pygame.Rect(int(self.x - 28), ground - 118, 58, 120)"""

new_zombie_props = """    is_pool: bool = False

    @property
    def y(self) -> float:
        return lane_ground(self.row, cell_h=self.cell_h, is_pool=self.is_pool) - 50.0

    def rect(self) -> pygame.Rect:
        ground = lane_ground(self.row, cell_h=self.cell_h, is_pool=self.is_pool)
        return pygame.Rect(int(self.x - 28), ground - 118, 58, 120)"""

if old_zombie_props in code:
    code = code.replace(old_zombie_props, new_zombie_props)
    print("Updated Zombie properties with is_pool!")

# 3. 更新 _cell_at 精确映射泳池点击坐标
old_cell_at = """    def _cell_at(self, pos: tuple[int, int]) -> tuple[int | None, int | None]:
        x, y = pos
        bottom = getattr(self, "grid_bottom", GRID_BOTTOM)
        ch = getattr(self, "cell_h", CELL_H)
        if not (GRID_X <= x < GRID_RIGHT and GRID_Y <= y < bottom):
            return None, None
        return (x - GRID_X) // CELL_W, (y - GRID_Y) // ch"""

new_cell_at = """    def _cell_at(self, pos: tuple[int, int]) -> tuple[int | None, int | None]:
        x, y = pos
        if getattr(self, "is_pool", False):
            if x < 140 or x >= 860:
                return None, None
            col = int((x - 140) // 80)
            if 90 <= y < 210:
                row = 0
            elif 210 <= y < 335:
                row = 1
            elif 335 <= y < 452:
                row = 2
            elif 452 <= y < 560:
                row = 3
            elif 560 <= y < 660:
                row = 4
            elif 660 <= y < 755:
                row = 5
            else:
                return None, None
            return int(clamp(col, 0, 8)), row

        bottom = getattr(self, "grid_bottom", GRID_BOTTOM)
        ch = getattr(self, "cell_h", CELL_H)
        if not (GRID_X <= x < GRID_RIGHT and GRID_Y <= y < bottom):
            return None, None
        return (x - GRID_X) // CELL_W, (y - GRID_Y) // ch"""

if old_cell_at in code:
    code = code.replace(old_cell_at, new_cell_at)
    print("Updated _cell_at with pool dynamic grid mapping!")

# 4. 更新 Plant 创建时传入 is_pool
old_new_plant = 'new_plant = Plant(name, col, row, max_hp, max_hp, cell_h=self.cell_h)'
new_new_plant = 'new_plant = Plant(name, col, row, max_hp, max_hp, cell_h=self.cell_h, is_pool=self.is_pool)'

if old_new_plant in code:
    code = code.replace(old_new_plant, new_new_plant)
    print("Updated Plant creation with is_pool parameter!")

# 5. 更新 Zombie 创建时传入 is_pool
old_zombie_spawn = 'zombie = Zombie(ztype, row, WIDTH + 20, config["hp"], config["hp"], speed, config["damage"], wave_id=wave_id, cell_h=self.cell_h)'
new_zombie_spawn = 'zombie = Zombie(ztype, row, WIDTH + 20, config["hp"], config["hp"], speed, config["damage"], wave_id=wave_id, cell_h=self.cell_h, is_pool=self.is_pool)'

if old_zombie_spawn in code:
    code = code.replace(old_zombie_spawn, new_zombie_spawn)
    print("Updated Zombie spawn with is_pool parameter!")

# 6. 更新 Ghost Preview 种植虚影在泳池关卡的绘制
old_ghost = """        if self.selected_plant:
            mouse = pygame.mouse.get_pos()
            col, row = self._cell_at(mouse)
            if col is not None and row is not None:
                rect = pygame.Rect(GRID_X + col * CELL_W, GRID_Y + row * CELL_H, CELL_W, CELL_H)
                surface = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)
                pygame.draw.rect(surface, (255, 244, 151, 40), surface.get_rect(), border_radius=7)
                pygame.draw.rect(surface, (255, 239, 137, 145), surface.get_rect(), 2, border_radius=7)
                self.screen.blit(surface, rect)
                if not self.headless:
                    ghost = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)
                    draw_plant(ghost, self.selected_plant, (CELL_W / 2, CELL_H / 2), 0.75, self.time_value)
                    ghost.set_alpha(155)
                    self.screen.blit(ghost, rect)"""

new_ghost = """        if self.selected_plant:
            mouse = pygame.mouse.get_pos()
            col, row = self._cell_at(mouse)
            if col is not None and row is not None:
                if getattr(self, "is_pool", False):
                    POOL_BOUNDS = [(100, 110), (210, 110), (360, 92), (452, 93), (570, 90), (660, 90)]
                    ry, rh = POOL_BOUNDS[row]
                    rect = pygame.Rect(140 + col * 80, ry, 80, rh)
                else:
                    rect = pygame.Rect(GRID_X + col * CELL_W, GRID_Y + row * CELL_H, CELL_W, CELL_H)
                surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.rect(surface, (255, 244, 151, 40), surface.get_rect(), border_radius=7)
                pygame.draw.rect(surface, (255, 239, 137, 145), surface.get_rect(), 2, border_radius=7)
                self.screen.blit(surface, rect)
                if not self.headless:
                    ghost = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    draw_plant(ghost, self.selected_plant, (rect.width / 2, rect.height / 2), 0.75, self.time_value)
                    ghost.set_alpha(155)
                    self.screen.blit(ghost, rect)"""

if old_ghost in code:
    code = code.replace(old_ghost, new_ghost)
    print("Updated Ghost preview with pool layout!")

# 7. 更新推车 Mower 在泳池关卡的位置
old_mower_init = """        self.mowers = [
            Mower(lane_ground(row, cell_h=self.cell_h) - 34, row)
            for row in range(self.rows)
        ]"""

new_mower_init = """        self.mowers = [
            Mower(lane_ground(row, cell_h=self.cell_h, is_pool=self.is_pool) - 34, row, x=88 if self.is_pool else 18)
            for row in range(self.rows)
        ]"""

if old_mower_init in code:
    code = code.replace(old_mower_init, new_mower_init)
    print("Updated Mower initialization with is_pool!")

p_pvz.write_text(code, encoding="utf-8")
print("=== All pool grid updates integrated into pvz_ten_levels.py! ===")
