# -*- coding: utf-8 -*-
"""Script to apply deep game mechanics updates to pvz_ten_levels.py."""

from pathlib import Path
import re

PVZ_FILE = Path(__file__).resolve().parent.parent / "pvz_ten_levels.py"

def update_game_logic():
    content = PVZ_FILE.read_text(encoding="utf-8")

    # 1. Update Game.__init__ to initialize dynamic grid attributes
    old_init = '''    def __init__(self, screen: pygame.Surface, headless: bool = False) -> None:
        self.screen = screen
        pvz_graphics.init_graphics()
        self.fonts = FontBook()
        self.audio = AudioBank()'''

    new_init = '''    def __init__(self, screen: pygame.Surface, headless: bool = False) -> None:
        self.screen = screen
        pvz_graphics.init_graphics()
        self.fonts = FontBook()
        self.audio = AudioBank()
        self.is_pool = False
        self.rows = ROWS
        self.cell_h = CELL_H
        self.pool_rows: list[int] = []
        self.grid_bottom = GRID_BOTTOM'''

    if old_init in content:
        content = content.replace(old_init, new_init, 1)
        print("Updated Game.__init__.")

    # 2. Update start_level
    old_start_level = '''    def start_level(self, index: int) -> None:
        self.level_index = int(clamp(index, 0, len(LEVELS) - 1))
        level = LEVELS[self.level_index]
        self._reset_runtime()
        self.sun = level["sun"]
        self.waves = self._build_waves()'''

    new_start_level = '''    def start_level(self, index: int) -> None:
        self.level_index = int(clamp(index, 0, len(LEVELS) - 1))
        level = LEVELS[self.level_index]
        self.is_pool = bool(level.get("pool", False))
        self.rows = 6 if self.is_pool else 5
        self.cell_h = 96 if self.is_pool else 116
        self.pool_rows = [2, 3] if self.is_pool else []
        self.grid_bottom = GRID_Y + self.rows * self.cell_h
        self._reset_runtime()
        self.sun = level["sun"]
        self.waves = self._build_waves()'''

    if old_start_level in content:
        content = content.replace(old_start_level, new_start_level, 1)
        print("Updated start_level.")

    # 3. Update _reset_runtime
    old_reset = '''        self.mowers = [Mower(row) for row in range(ROWS)]
        self.sun = 150
        self.cooldowns = {name: 0.0 for name in UNLOCK_ORDER}'''

    new_reset = '''        self.mowers = [
            Mower(row, cell_h=self.cell_h, is_pool=(self.is_pool and row in self.pool_rows))
            for row in range(self.rows)
        ]
        self.sun = 150
        self.cooldowns = {name: 0.0 for name in UNLOCK_ORDER}'''

    if old_reset in content:
        content = content.replace(old_reset, new_reset, 1)
        print("Updated _reset_runtime.")

    # 4. Update _build_waves to use self.rows instead of ROWS
    old_build_waves = '''        waves: list[Wave] = []
        last_lane = rng.randrange(ROWS)
        for wave_index, wave_size in enumerate(counts):
            members: list[WaveMember] = []
            delay = 0.0
            for member_index in range(wave_size):
                roll = rng.random()
                cumulative = 0.0
                ztype = "basic"
                for name, weight in zip(types, mix):
                    cumulative += weight
                    if roll <= cumulative:
                        ztype = name
                        break

                if wave_index == wave_count - 1 and member_index < ROWS:
                    lane = member_index
                else:
                    lane = rng.randrange(ROWS)
                    if member_index > 0 and rng.random() < 0.3 and lane == last_lane:
                        lane = (lane + rng.randint(1, ROWS - 1)) % ROWS
                last_lane = lane
                members.append(WaveMember(delay, ztype, lane))'''

    new_build_waves = '''        waves: list[Wave] = []
        rows = self.rows
        last_lane = rng.randrange(rows)
        for wave_index, wave_size in enumerate(counts):
            members: list[WaveMember] = []
            delay = 0.0
            for member_index in range(wave_size):
                roll = rng.random()
                cumulative = 0.0
                ztype = "basic"
                for name, weight in zip(types, mix):
                    cumulative += weight
                    if roll <= cumulative:
                        ztype = name
                        break

                if wave_index == wave_count - 1 and member_index < rows:
                    lane = member_index
                else:
                    lane = rng.randrange(rows)
                    if member_index > 0 and rng.random() < 0.3 and lane == last_lane:
                        lane = (lane + rng.randint(1, rows - 1)) % rows
                last_lane = lane
                members.append(WaveMember(delay, ztype, lane))'''

    if old_build_waves in content:
        content = content.replace(old_build_waves, new_build_waves, 1)
        print("Updated _build_waves.")

    # 5. Update _spawn_wave_member
    old_spawn = '''    def _spawn_wave_member(self, wave_id: int, member: WaveMember) -> None:
        config = ZOMBIES[member.ztype]
        speed_scale = 1.0 + self.level_index * 0.012
        zombie = Zombie(
            member.ztype, member.row, WIDTH + random.randint(20, 62),
            config["hp"], config["hp"],
            config["speed"] * speed_scale,
            config["damage"],
            wave_id=wave_id,
        )
        if member.ztype == "pole":
            zombie.has_pole = True
            zombie.vault_state = "run"
        elif member.ztype == "newspaper":
            zombie.has_newspaper = True
            zombie.newspaper_hp = 140.0
        self.zombies.append(zombie)
        self.spawned_count += 1'''

    new_spawn = '''    def _spawn_wave_member(self, wave_id: int, member: WaveMember) -> None:
        row = member.row
        ztype = member.ztype
        if getattr(self, "is_pool", False):
            is_water_row = row in self.pool_rows
            is_water_zombie = ztype in ("ducky", "snorkel", "dolphin")
            if is_water_zombie and not is_water_row:
                row = random.choice(self.pool_rows)
            elif not is_water_zombie and is_water_row:
                ztype = "ducky"

        config = ZOMBIES[ztype]
        speed_scale = 1.0 + self.level_index * 0.012
        zombie = Zombie(
            ztype, row, WIDTH + random.randint(20, 62),
            config["hp"], config["hp"],
            config["speed"] * speed_scale,
            config["damage"],
            wave_id=wave_id,
            cell_h=self.cell_h,
        )
        if ztype == "pole":
            zombie.has_pole = True
            zombie.vault_state = "run"
        elif ztype == "newspaper":
            zombie.has_newspaper = True
            zombie.newspaper_hp = 140.0
        elif ztype == "dolphin":
            zombie.has_dolphin = True
            zombie.vault_state = "run"
        elif ztype == "snorkel":
            zombie.is_submerged = True
        self.zombies.append(zombie)
        self.spawned_count += 1'''

    if old_spawn in content:
        content = content.replace(old_spawn, new_spawn, 1)
        print("Updated _spawn_wave_member.")

    # 6. Update _cell_at and plant query helpers
    old_cell_helpers = '''    def _cell_at(self, pos: tuple[int, int]) -> tuple[int | None, int | None]:
        x, y = pos
        if not (GRID_X <= x < GRID_RIGHT and GRID_Y <= y < GRID_BOTTOM):
            return None, None
        return (x - GRID_X) // CELL_W, (y - GRID_Y) // CELL_H

    def _plant_at(self, col: int, row: int) -> Plant | None:
        return next((p for p in self.plants if p.alive and p.col == col and p.row == row), None)'''

    new_cell_helpers = '''    def _cell_at(self, pos: tuple[int, int]) -> tuple[int | None, int | None]:
        x, y = pos
        bottom = getattr(self, "grid_bottom", GRID_BOTTOM)
        ch = getattr(self, "cell_h", CELL_H)
        if not (GRID_X <= x < GRID_RIGHT and GRID_Y <= y < bottom):
            return None, None
        return (x - GRID_X) // CELL_W, (y - GRID_Y) // ch

    def _plants_at(self, col: int, row: int) -> list[Plant]:
        return [p for p in self.plants if p.alive and p.col == col and p.row == row]

    def _carrier_at(self, col: int, row: int) -> Plant | None:
        return next((p for p in self.plants if p.alive and p.col == col and p.row == row and p.ptype == "lilypad"), None)

    def _top_plant_at(self, col: int, row: int) -> Plant | None:
        plants = self._plants_at(col, row)
        non_carrier = [p for p in plants if p.ptype != "lilypad"]
        return non_carrier[0] if non_carrier else (plants[0] if plants else None)

    def _plant_at(self, col: int, row: int) -> Plant | None:
        return self._top_plant_at(col, row)'''

    if old_cell_helpers in content:
        content = content.replace(old_cell_helpers, new_cell_helpers, 1)
        print("Updated _cell_at and query helpers.")

    # 7. Update _try_plant
    old_try_plant = '''    def _try_plant(self, col: int, row: int, name: str) -> None:
        if not self.selected_plant and not self.shovel_selected:
            return

        col, row = self._cell_at(pos)
        if col is None or row is None:
            return
        existing = self._plant_at(col, row)
        if self.shovel_selected:
            if existing is not None:
                existing.alive = False
                self.burst(existing.x, existing.y, (141, 98, 54), 15)
                self.float_text(existing.x, existing.y - 30, "已移除", C_CREAM)
            self.shovel_selected = False
            return
        if not self.selected_plant:
            return
        if existing is not None:
            self.float_text(existing.x, existing.y - 40, "这里已有植物", (255, 220, 123))
            return
        name = self.selected_plant
        cost = PLANTS[name]["cost"]
        if self.sun < cost or self.cooldowns[name] > 0:
            return
        max_hp = PLANTS[name]["hp"]
        self.plants.append(Plant(name, col, row, max_hp, max_hp))
        self.sun -= cost
        self.cooldowns[name] = PLANTS[name]["cooldown"]
        self.selected_plant = None
        self.burst(*cell_center(col, row), (119, 176, 74), 12, upward=True)
        self.audio.play("plant")'''

    # Notice the pos in _handle_click or _try_plant. Let's inspect _handle_click around _try_plant first.
    pass

    PVZ_FILE.write_text(content, encoding="utf-8")

if __name__ == "__main__":
    update_game_logic()
