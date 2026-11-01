# -*- coding: utf-8 -*-
"""Comprehensive gameplay updater for pvz_ten_levels.py.
Applies:
1. Dynamic grid attributes & wave spawning logic.
2. Carrier plant & pool planting logic.
3. Catapult, Torchwood, Cattail, Garlic, Snorkel, Dolphin, Butter mechanics.
4. Menu screen (16 levels) and Seed Select screen (23 plants, 6x4 grid).
5. Background and preview setups.
"""

from pathlib import Path
import re

PVZ_FILE = Path(__file__).resolve().parent.parent / "pvz_ten_levels.py"

def run_update():
    text = PVZ_FILE.read_text(encoding="utf-8")

    # 1. Update Game.__init__
    text = text.replace(
        '''        self.audio = AudioBank()
        self.clock = pygame.time.Clock()''',
        '''        self.audio = AudioBank()
        self.is_pool = False
        self.rows = ROWS
        self.cell_h = CELL_H
        self.pool_rows: list[int] = []
        self.grid_bottom = GRID_BOTTOM
        self.clock = pygame.time.Clock()'''
    )

    # 2. Update start_level
    old_start = '''    def start_level(self, index: int) -> None:
        self.level_index = int(clamp(index, 0, len(LEVELS) - 1))
        level = LEVELS[self.level_index]
        self._reset_runtime()
        self.sun = level["sun"]
        self.waves = self._build_waves()'''
    new_start = '''    def start_level(self, index: int) -> None:
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
    text = text.replace(old_start, new_start)

    # 3. Update _reset_runtime
    old_reset_mowers = '''        self.mowers = [Mower(row) for row in range(ROWS)]'''
    new_reset_mowers = '''        self.mowers = [
            Mower(row, cell_h=self.cell_h, is_pool=(self.is_pool and row in self.pool_rows))
            for row in range(self.rows)
        ]'''
    text = text.replace(old_reset_mowers, new_reset_mowers)

    # 4. Update _build_waves
    old_bw = '''        last_lane = rng.randrange(ROWS)
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

    new_bw = '''        rows = self.rows
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
    text = text.replace(old_bw, new_bw)

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
    text = text.replace(old_spawn, new_spawn)

    # 6. Update _recommend_seeds
    old_rec = '''    def _recommend_seeds(self) -> None:
        unlocked = self.available_plants()
        level = LEVELS[self.level_index]
        is_night = level.get("theme") == "night"
        picks = []
        if is_night and "sunshroom" in unlocked:
            picks.append("sunshroom")
        elif "sunflower" in unlocked:
            picks.append("sunflower")
        if "wallnut" in unlocked:
            picks.append("wallnut")
        if "snowpea" in unlocked:
            picks.append("snowpea")
        if "threepeater" in unlocked:
            picks.append("threepeater")
        elif "repeater" in unlocked:
            picks.append("repeater")
        elif "peashooter" in unlocked:
            picks.append("peashooter")
        for p in ["squash", "spikeweed", "cherrybomb", "iceshroom", "jalapeno", "potatomine", "puffshroom", "chomper"]:
            if p in unlocked and p not in picks and len(picks) < self.slot_capacity:
                picks.append(p)
        for p in unlocked:
            if p not in picks and len(picks) < self.slot_capacity:
                picks.append(p)
        self.selected_seeds = picks[:self.slot_capacity]'''

    new_rec = '''    def _recommend_seeds(self) -> None:
        unlocked = self.available_plants()
        level = LEVELS[self.level_index]
        is_night = level.get("theme") == "night"
        is_pool = bool(level.get("pool", False))
        picks = []
        if is_pool and "lilypad" in unlocked:
            picks.append("lilypad")
        if is_night and "sunshroom" in unlocked:
            picks.append("sunshroom")
        elif "sunflower" in unlocked:
            picks.append("sunflower")
        if "wallnut" in unlocked:
            picks.append("wallnut")
        if is_pool and "cattail" in unlocked:
            picks.append("cattail")
        if "torchwood" in unlocked and ("repeater" in unlocked or "peashooter" in unlocked):
            picks.append("torchwood")
        if "wintermelon" in unlocked:
            picks.append("wintermelon")
        elif "melonpult" in unlocked:
            picks.append("melonpult")
        elif "cabbagepult" in unlocked:
            picks.append("cabbagepult")
        elif "kernelpult" in unlocked:
            picks.append("kernelpult")
        elif "snowpea" in unlocked:
            picks.append("snowpea")
        elif "threepeater" in unlocked:
            picks.append("threepeater")
        elif "repeater" in unlocked:
            picks.append("repeater")
        elif "peashooter" in unlocked:
            picks.append("peashooter")
        for p in ["squash", "garlic", "spikeweed", "cherrybomb", "iceshroom", "jalapeno", "potatomine", "puffshroom", "chomper"]:
            if p in unlocked and p not in picks and len(picks) < self.slot_capacity:
                picks.append(p)
        for p in unlocked:
            if p not in picks and len(picks) < self.slot_capacity:
                picks.append(p)
        self.selected_seeds = picks[:self.slot_capacity]'''
    text = text.replace(old_rec, new_rec)

    # 7. Update available_plants
    old_avail = '''    def available_plants(self) -> list[str]:
        # Unlock plants dynamically with level index
        unlock_count = min(len(UNLOCK_ORDER), max(4, self.level_index + 4))
        if self.level_index >= 7:
            unlock_count = len(UNLOCK_ORDER)
        return UNLOCK_ORDER[:unlock_count]'''

    new_avail = '''    def available_plants(self) -> list[str]:
        # Unlock plants dynamically with level index
        unlock_count = min(len(UNLOCK_ORDER), max(4, self.level_index + 4))
        if self.level_index >= 10:
            unlock_count = len(UNLOCK_ORDER)
        return UNLOCK_ORDER[:unlock_count]'''
    text = text.replace(old_avail, new_avail)

    # 8. Update _handle_click planting block, _cell_at, _plant_at
    old_click_plant_and_cell = '''        col, row = self._cell_at(pos)
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
        self.burst(*cell_center(col, row), (119, 76, 74), 12, upward=True)
        self.audio.play("plant")

    def _cell_at(self, pos: tuple[int, int]) -> tuple[int | None, int | None]:
        x, y = pos
        if not (GRID_X <= x < GRID_RIGHT and GRID_Y <= y < GRID_BOTTOM):
            return None, None
        return (x - GRID_X) // CELL_W, (y - GRID_Y) // CELL_H

    def _plant_at(self, col: int, row: int) -> Plant | None:
        return next((p for p in self.plants if p.alive and p.col == col and p.row == row), None)'''

    # We match using regex because colors/numbers might have slight differences
    re_click_block = re.compile(
        r'col, row = self\._cell_at\(pos\).*?def _plant_at\(self, col: int, row: int\) -> Plant \| None:.*?\n',
        re.DOTALL
    )

    new_click_and_cell = '''col, row = self._cell_at(pos)
        if col is None or row is None:
            return

        is_water = getattr(self, "is_pool", False) and (row in getattr(self, "pool_rows", []))
        carrier = self._carrier_at(col, row)
        top_plant = self._top_plant_at(col, row)

        if self.shovel_selected:
            if top_plant is not None:
                top_plant.alive = False
                self.burst(top_plant.x, top_plant.y, (141, 98, 54), 15)
                self.float_text(top_plant.x, top_plant.y - 30, "已移除", C_CREAM)
            self.shovel_selected = False
            return

        if not self.selected_plant:
            return

        name = self.selected_plant
        cost = PLANTS[name]["cost"]
        if self.sun < cost or self.cooldowns[name] > 0:
            return

        # 水面与陆地种植规则
        if is_water:
            if name in ("spikeweed", "potatomine"):
                self.float_text(GRID_X + col * CELL_W + 55, GRID_Y + row * self.cell_h + 35, "不能种在水上！", (255, 120, 100))
                return
            if name == "lilypad":
                if carrier is not None:
                    self.float_text(carrier.x, carrier.y - 35, "这里已有睡莲", (255, 220, 123))
                    return
            elif name == "cattail":
                if carrier is None:
                    self.float_text(GRID_X + col * CELL_W + 55, GRID_Y + row * self.cell_h + 35, "猫尾草需种在睡莲上！", (255, 220, 123))
                    return
                if top_plant != carrier:
                    self.float_text(carrier.x, carrier.y - 35, "睡莲已被占用", (255, 220, 123))
                    return
                carrier.alive = False
            else:
                if carrier is None:
                    self.float_text(GRID_X + col * CELL_W + 55, GRID_Y + row * self.cell_h + 35, "必须先种植睡莲！", (255, 120, 100))
                    return
                if top_plant != carrier:
                    self.float_text(carrier.x, carrier.y - 35, "这里已有植物", (255, 220, 123))
                    return
        else:
            if name == "lilypad":
                self.float_text(GRID_X + col * CELL_W + 55, GRID_Y + row * self.cell_h + 35, "睡莲只能种在水中！", (255, 120, 100))
                return
            if top_plant is not None:
                self.float_text(top_plant.x, top_plant.y - 40, "这里已有植物", (255, 220, 123))
                return

        max_hp = PLANTS[name]["hp"]
        new_plant = Plant(name, col, row, max_hp, max_hp, cell_h=self.cell_h)
        if is_water and carrier is not None and name not in ("lilypad", "cattail"):
            new_plant.carrier = carrier
            carrier.carried_plant = new_plant
        self.plants.append(new_plant)
        self.sun -= cost
        self.cooldowns[name] = PLANTS[name]["cooldown"]
        self.selected_plant = None
        self.burst(new_plant.x, new_plant.y, (119, 176, 74), 12, upward=True)
        self.audio.play("plant")

    def _cell_at(self, pos: tuple[int, int]) -> tuple[int | None, int | None]:
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
        return self._top_plant_at(col, row)
'''

    text = re_click_block.sub(new_click_and_cell, text)

    # 9. Update _update_plants to add catapults, cattail
    old_update_plants_header = '''    def _update_plants(self, dt: float) -> None:'''
    # We will expand _update_plants logic
    re_update_plants = re.compile(r'def _update_plants\(self, dt: float\) -> None:.*?def _update_zombies', re.DOTALL)
    new_update_plants = '''def _update_plants(self, dt: float) -> None:
        for plant in self.plants:
            if not plant.alive:
                continue
            plant.age += dt
            plant.action_timer += dt
            plant.flash = max(0.0, plant.flash - dt)
            if plant.ptype == "sunflower":
                if plant.action_timer >= (4.1 if plant.age < 8 else 7.0):
                    plant.action_timer = 0
                    target = lane_ground(plant.row, cell_h=self.cell_h) - 34 + random.randint(-15, 15)
                    self.suns.append(SunToken(plant.x + random.randint(-10, 10), plant.y - 45, target))
            elif plant.ptype in ("peashooter", "snowpea", "repeater"):
                if plant.action_timer >= (1.42 if plant.ptype != "repeater" else 1.58):
                    has_target = any(
                        z.row == plant.row and not z.dead and z.x > plant.x - 20 and z.x < GRID_RIGHT + 180
                        for z in self.zombies
                    )
                    if has_target:
                        plant.action_timer = 0
                        y = lane_ground(plant.row, cell_h=self.cell_h) - 70
                        freeze = plant.ptype == "snowpea"
                        self.projectiles.append(Projectile(plant.x + 43, y, plant.row, 25, freeze=freeze))
                        if plant.ptype == "repeater":
                            self.projectiles.append(Projectile(plant.x + 30, y + 4, plant.row, 25))
            elif plant.ptype == "cabbagepult":
                if plant.action_timer >= 2.85:
                    target = next((z for z in sorted(self.zombies, key=lambda z: z.x) if z.row == plant.row and not z.dead and z.x > plant.x - 20 and z.x < GRID_RIGHT + 180), None)
                    if target:
                        plant.action_timer = 0.0
                        tx = target.x
                        ty = target.y
                        dist = max(80.0, tx - plant.x)
                        duration = clamp(dist / 400.0, 0.55, 1.1)
                        self.projectiles.append(
                            Projectile(
                                x=plant.x + 20, y=plant.y - 30, row=plant.row, damage=40.0,
                                bullet_type="cabbage", is_lobbed=True,
                                start_x=plant.x + 20, start_y=plant.y - 30,
                                target_x=tx, target_y=ty, lob_duration=duration, apex_h=110.0,
                            )
                        )
                        self.audio.play("plant", cooldown=0.1)
            elif plant.ptype == "kernelpult":
                if plant.action_timer >= 2.85:
                    target = next((z for z in sorted(self.zombies, key=lambda z: z.x) if z.row == plant.row and not z.dead and z.x > plant.x - 20 and z.x < GRID_RIGHT + 180), None)
                    if target:
                        plant.action_timer = 0.0
                        is_butter = random.random() < 0.25
                        b_type = "butter" if is_butter else "kernel"
                        dmg = 40.0 if is_butter else 20.0
                        tx = target.x
                        ty = target.y
                        dist = max(80.0, tx - plant.x)
                        duration = clamp(dist / 400.0, 0.55, 1.1)
                        self.projectiles.append(
                            Projectile(
                                x=plant.x + 20, y=plant.y - 30, row=plant.row, damage=dmg,
                                bullet_type=b_type, is_lobbed=True,
                                start_x=plant.x + 20, start_y=plant.y - 30,
                                target_x=tx, target_y=ty, lob_duration=duration, apex_h=110.0,
                            )
                        )
                        self.audio.play("plant", cooldown=0.1)
            elif plant.ptype == "melonpult":
                if plant.action_timer >= 2.9:
                    target = next((z for z in sorted(self.zombies, key=lambda z: z.x) if z.row == plant.row and not z.dead and z.x > plant.x - 20 and z.x < GRID_RIGHT + 180), None)
                    if target:
                        plant.action_timer = 0.0
                        tx = target.x
                        ty = target.y
                        dist = max(80.0, tx - plant.x)
                        duration = clamp(dist / 400.0, 0.55, 1.1)
                        self.projectiles.append(
                            Projectile(
                                x=plant.x + 20, y=plant.y - 35, row=plant.row, damage=80.0,
                                bullet_type="melon", is_lobbed=True,
                                start_x=plant.x + 20, start_y=plant.y - 35,
                                target_x=tx, target_y=ty, lob_duration=duration, apex_h=120.0,
                            )
                        )
                        self.audio.play("plant", cooldown=0.1)
            elif plant.ptype == "wintermelon":
                if plant.action_timer >= 2.9:
                    target = next((z for z in sorted(self.zombies, key=lambda z: z.x) if z.row == plant.row and not z.dead and z.x > plant.x - 20 and z.x < GRID_RIGHT + 180), None)
                    if target:
                        plant.action_timer = 0.0
                        tx = target.x
                        ty = target.y
                        dist = max(80.0, tx - plant.x)
                        duration = clamp(dist / 400.0, 0.55, 1.1)
                        self.projectiles.append(
                            Projectile(
                                x=plant.x + 20, y=plant.y - 35, row=plant.row, damage=80.0, freeze=True,
                                bullet_type="winter_melon", is_lobbed=True,
                                start_x=plant.x + 20, start_y=plant.y - 35,
                                target_x=tx, target_y=ty, lob_duration=duration, apex_h=120.0,
                            )
                        )
                        self.audio.play("plant", cooldown=0.1)
            elif plant.ptype == "cattail":
                if plant.action_timer >= 1.4:
                    alive_zombies = [z for z in self.zombies if not z.dead and z.x < GRID_RIGHT + 150]
                    if alive_zombies:
                        target = min(alive_zombies, key=lambda z: z.x)
                        plant.action_timer = 0.0
                        self.projectiles.append(
                            Projectile(
                                x=plant.x + 10, y=plant.y - 20, row=target.row, damage=20.0,
                                speed=520.0, bullet_type="cattail_spike",
                                is_homing=True, target_zombie=target,
                            )
                        )
                        self.projectiles.append(
                            Projectile(
                                x=plant.x - 6, y=plant.y - 12, row=target.row, damage=20.0,
                                speed=480.0, bullet_type="cattail_spike",
                                is_homing=True, target_zombie=target,
                            )
                        )
                        self.audio.play("plant", cooldown=0.1)
            elif plant.ptype == "squash" and not plant.exploded:
                if plant.squash_state == "idle":
                    target = next((z for z in self.zombies if z.row == plant.row and not z.dead and -35 <= (z.x - plant.x) <= 95), None)
                    if target:
                        plant.squash_state = "jump"
                        plant.squash_target_x = target.x
                        plant.squash_timer = 0.0
                        self.audio.play("groan", cooldown=0.3)
                elif plant.squash_state == "jump":
                    plant.squash_timer += dt * 2.8
                    if plant.squash_timer >= 1.0:
                        plant.squash_state = "smash"
                        plant.exploded = True
                        plant.alive = False
                        self.audio.play("squash")
                        self._explode_radius(plant.squash_target_x, lane_ground(plant.row, cell_h=self.cell_h) - 30, 85, 1800, (88, 172, 76))
                        self.burst(plant.squash_target_x, lane_ground(plant.row, cell_h=self.cell_h) - 10, (65, 140, 55), 24, speed=160)
            elif plant.ptype == "chomper":
                if plant.swallow_timer > 0:
                    plant.swallow_timer = max(0.0, plant.swallow_timer - dt)
                else:
                    target = next((z for z in self.zombies if z.row == plant.row and not z.dead and 0 <= (z.x - plant.x) <= 135), None)
                    if target:
                        self.kill_zombie(target)
                        plant.swallow_timer = 20.0
                        self.audio.play("chomp")
                        self.float_text(plant.x, plant.y - 45, "咀嚼吞食中...", C_PURPLE)
                        self.burst(plant.x + 30, plant.y - 15, (160, 70, 200), 14)
            elif plant.ptype == "cherrybomb" and not plant.exploded and plant.age >= 1.15:
                plant.exploded = True
                self._explode_radius(plant.x, plant.y, 165, 1300, (255, 112, 53))
                plant.alive = False
            elif plant.ptype == "jalapeno" and not plant.exploded and plant.age >= 1.15:
                plant.exploded = True
                self._burn_lane(plant.row)
                plant.alive = False
            elif plant.ptype == "potatomine" and plant.age >= 6.0 and not plant.exploded:
                target = next(
                    (z for z in self.zombies if z.row == plant.row and not z.dead and abs(z.x - plant.x) < 64),
                    None,
                )
                if target is not None:
                    plant.exploded = True
                    self._explode_radius(plant.x, plant.y + 9, 82, 1000, (255, 178, 72))
                    plant.alive = False
            elif plant.ptype == "threepeater":
                if plant.action_timer >= 1.45:
                    target_rows = [r for r in (plant.row - 1, plant.row, plant.row + 1) if 0 <= r < self.rows]
                    has_target = any(
                        z.row in target_rows and not z.dead and z.x > plant.x - 20 and z.x < GRID_RIGHT + 180
                        for z in self.zombies
                    )
                    if has_target:
                        plant.action_timer = 0
                        for r in target_rows:
                            y = lane_ground(r, cell_h=self.cell_h) - 70
                            self.projectiles.append(Projectile(plant.x + 38, y, r, 20))
            elif plant.ptype == "spikeweed":
                if plant.action_timer >= 0.45:
                    plant.action_timer = 0
                    for z in self.zombies:
                        if z.row == plant.row and not z.dead and abs(z.x - plant.x) < 48:
                            z.hp -= 22.0
                            z.flash = 0.08
                            if z.hp <= 0:
                                self.kill_zombie(z)
            elif plant.ptype == "puffshroom":
                if plant.action_timer >= 1.35:
                    has_target = any(
                        z.row == plant.row and not z.dead and plant.x - 10 <= z.x <= plant.x + CELL_W * 3.6
                        for z in self.zombies
                    )
                    if has_target:
                        plant.action_timer = 0
                        y = lane_ground(plant.row, cell_h=self.cell_h) - 52
                        self.projectiles.append(Projectile(plant.x + 28, y, plant.row, 18, bullet_type="mushroom"))
            elif plant.ptype == "sunshroom":
                if plant.action_timer >= (6.5 if plant.age < 35 else 8.5):
                    plant.action_timer = 0
                    target = lane_ground(plant.row, cell_h=self.cell_h) - 34 + random.randint(-10, 10)
                    val = 15 if plant.age < 35 else 25
                    self.suns.append(SunToken(plant.x + random.randint(-8, 8), plant.y - 35, target, value=val))
            elif plant.ptype == "iceshroom" and not plant.exploded and plant.age >= 1.2:
                plant.exploded = True
                plant.alive = False
                for z in self.zombies:
                    if not z.dead:
                        z.slow_timer = 12.0
                        z.hp -= 35.0
                        z.flash = 0.2
                        if z.hp <= 0:
                            self.kill_zombie(z)
                for _ in range(40):
                    self.burst(random.randint(GRID_X, GRID_RIGHT), random.randint(GRID_Y, self.grid_bottom), (180, 240, 255), 4, speed=120)
                self.float_text(WIDTH // 2, HEIGHT // 2 - 30, "全场冰封！", (140, 225, 255))

    def _update_zombies'''
    text = re_update_plants.sub(new_update_plants, text)

    # 10. Update _update_zombies, _plant_under_attack, _update_projectiles, and add _damage_zombie
    re_zombies_and_proj = re.compile(r'def _update_zombies\(self, dt: float\) -> None:.*?def _spawn_natural_sun', re.DOTALL)
    new_zombies_and_proj = '''def _update_zombies(self, dt: float) -> None:
        plants_by_row: dict[int, list[Plant]] = {}
        for plant in self.plants:
            if plant.alive:
                plants_by_row.setdefault(plant.row, []).append(plant)

        for zombie in self.zombies:
            if zombie.dead:
                continue

            # 黄油定身眩晕判定
            if getattr(zombie, "butter_timer", 0.0) > 0:
                zombie.butter_timer = max(0.0, zombie.butter_timer - dt)
                zombie.eating = 0.0
                continue

            # 撑杆跳越障
            if zombie.ztype == "pole" and zombie.has_pole:
                if zombie.vault_state == "run":
                    target_plant = self._plant_under_attack(zombie, plants_by_row)
                    if target_plant and target_plant.alive:
                        zombie.vault_state = "jumping"
                        zombie.vault_progress = 0.0
                        zombie.eating = 0.0
                        self.audio.play("vault")
                elif zombie.vault_state == "jumping":
                    zombie.vault_progress += dt * 2.2
                    zombie.x -= 140 * dt * 2.2
                    if zombie.vault_progress >= 1.0:
                        zombie.vault_state = "done"
                        zombie.has_pole = False
                        zombie.speed = 16.0
                        self.burst(zombie.x, lane_ground(zombie.row, cell_h=self.cell_h) - 10, (140, 110, 80), 8)
                    continue

            # 海豚骑士飞跃
            if zombie.ztype == "dolphin" and getattr(zombie, "has_dolphin", False):
                if zombie.vault_state == "run":
                    target_plant = self._plant_under_attack(zombie, plants_by_row)
                    if target_plant and target_plant.alive:
                        zombie.vault_state = "jumping"
                        zombie.vault_progress = 0.0
                        zombie.eating = 0.0
                        self.audio.play("vault")
                        self.audio.play("splash", cooldown=0.3)
                elif zombie.vault_state == "jumping":
                    zombie.vault_progress += dt * 2.2
                    zombie.x -= 150 * dt * 2.2
                    if zombie.vault_progress >= 1.0:
                        zombie.vault_state = "done"
                        zombie.has_dolphin = False
                        zombie.speed = 16.0
                        self.audio.play("splash", cooldown=0.3)
                        self.burst(zombie.x, lane_ground(zombie.row, cell_h=self.cell_h) - 10, (140, 220, 255), 16)
                    continue

            zombie.slow_timer = max(0.0, zombie.slow_timer - dt)
            speed_mult = 0.55 if zombie.slow_timer > 0 else 1.0
            plant = self._plant_under_attack(zombie, plants_by_row)

            # 潜水僵尸潜水状态维护 (啃咬时探出头，平时潜入水中)
            if zombie.ztype == "snorkel":
                zombie.is_submerged = (plant is None)

            if plant is not None:
                zombie.eating = min(1.0, zombie.eating + dt * 4)
                zombie.bite_timer += dt
                bite_delay = 0.38 if zombie.enraged else 0.55
                if zombie.bite_timer >= bite_delay:
                    zombie.bite_timer = 0
                    plant.hp -= zombie.damage * (1.5 if zombie.enraged else 1.0)
                    plant.flash = 0.18
                    self.burst(plant.x, plant.y, (120, 185, 75), 2)

                    # 大蒜啃咬分流变道
                    if plant.ptype == "garlic":
                        old_row = zombie.row
                        new_row = old_row
                        if getattr(self, "is_pool", False):
                            if old_row in (0, 1):
                                new_row = 1 if old_row == 0 else 0
                            elif old_row in (2, 3):
                                new_row = 3 if old_row == 2 else 2
                            elif old_row in (4, 5):
                                new_row = 5 if old_row == 4 else 4
                        else:
                            if old_row == 0:
                                new_row = 1
                            elif old_row == self.rows - 1:
                                new_row = old_row - 1
                            else:
                                new_row = old_row + random.choice([-1, 1])
                        if new_row != old_row:
                            zombie.row = new_row
                            zombie.eating = 0.0
                            self.burst(plant.x, plant.y, (240, 235, 200), 10)
                            self.float_text(zombie.x, zombie.y - 25, "嫌弃变道！", (230, 240, 180))

                    if plant.hp <= 0:
                        plant.alive = False
                        zombie.eating = 0.0
                        self.audio.play("click")
            else:
                zombie.eating = max(0.0, zombie.eating - dt * 3)
                zombie.x -= zombie.speed * speed_mult * dt
                if zombie.x < MOWER_X - 6:
                    self.overlay = "lost"
                    self.lose_reason = f"第 {zombie.row + 1} 路的僵尸冲进了屋子！"
                    self.audio.stop_music()
                    self.audio.play("lose")
                    break

    def _plant_under_attack(self, zombie: Zombie, plants_by_row: dict[int, list[Plant]] | None = None) -> Plant | None:
        row_plants = plants_by_row.get(zombie.row, []) if plants_by_row is not None else [
            p for p in self.plants if p.alive and p.row == zombie.row
        ]
        eligible = []
        for plant in row_plants:
            if not plant.alive or plant.ptype == "spikeweed":
                continue
            dx = zombie.x - plant.x
            if -12 <= dx <= 44:
                eligible.append(plant)
        if not eligible:
            return None
        top = [p for p in eligible if p.ptype != "lilypad"]
        return top[0] if top else eligible[0]

    def _damage_zombie(self, zombie: Zombie, damage: float, freeze: bool = False) -> None:
        if zombie.dead:
            return
        if zombie.ztype == "newspaper" and zombie.has_newspaper and zombie.newspaper_hp > 0:
            zombie.newspaper_hp -= damage
            self.burst(zombie.x, zombie.y - 20, (240, 240, 230), 5)
            if zombie.newspaper_hp <= 0:
                zombie.has_newspaper = False
                zombie.enraged = True
                zombie.speed = 36.0
                zombie.damage = 45.0
                self.float_text(zombie.x, zombie.y - 30, "暴怒！", (255, 60, 60))
                self.burst(zombie.x, zombie.y - 40, (250, 250, 250), 18)
                self.audio.play("groan")
        else:
            zombie.hp -= damage
            zombie.flash = 0.08
            if freeze:
                zombie.slow_timer = 5.0
            self.burst(zombie.x, zombie.y - 10, (126, 206, 92) if not freeze else (152, 234, 255), 4)
            if zombie.hp <= 0:
                self.kill_zombie(zombie)

    def _update_projectiles(self, dt: float) -> None:
        torchwoods = [p for p in self.plants if p.alive and p.ptype == "torchwood"]
        for projectile in self.projectiles:
            if not projectile.alive:
                continue
            old_x = projectile.x
            projectile.update(dt)

            # 火炬树桩穿透点燃判定 (仅水平直射豌豆)
            if not projectile.is_lobbed and projectile.bullet_type in ("pea", "snowpea"):
                for torch in torchwoods:
                    if torch.row == projectile.row and old_x <= torch.x <= projectile.x + 15:
                        if projectile.bullet_type == "pea":
                            projectile.bullet_type = "fire_pea"
                            projectile.damage = 40.0
                            projectile.freeze = False
                            self.burst(torch.x, torch.y - 20, (255, 140, 40), 6, upward=True)
                        elif projectile.bullet_type == "snowpea":
                            projectile.bullet_type = "pea"
                            projectile.freeze = False
                            projectile.damage = 20.0
                            self.burst(torch.x, torch.y - 20, (200, 230, 255), 4)
                        break

            # 抛物线投掷物落地结算
            if projectile.is_lobbed:
                if projectile.lob_progress >= 1.0:
                    projectile.alive = False
                    impact_x = projectile.target_x
                    impact_y = projectile.target_y

                    hit_targets = [
                        z for z in self.zombies
                        if z.row == projectile.row and not z.dead and abs(z.x - impact_x) < 55
                    ]
                    main_target = min(hit_targets, key=lambda z: abs(z.x - impact_x)) if hit_targets else None

                    if projectile.bullet_type == "cabbage":
                        self.burst(impact_x, impact_y, (140, 210, 80), 8)
                        if main_target:
                            self._damage_zombie(main_target, projectile.damage, freeze=False)
                    elif projectile.bullet_type == "kernel":
                        self.burst(impact_x, impact_y, (255, 220, 80), 6)
                        if main_target:
                            self._damage_zombie(main_target, projectile.damage, freeze=False)
                    elif projectile.bullet_type == "butter":
                        self.burst(impact_x, impact_y, (255, 235, 110), 12)
                        self.audio.play("butter", cooldown=0.1)
                        if main_target:
                            self._damage_zombie(main_target, projectile.damage, freeze=False)
                            main_target.butter_timer = 4.0
                            self.float_text(main_target.x, main_target.y - 35, "黄油定身！", (255, 230, 90))
                    elif projectile.bullet_type in ("melon", "winter_melon"):
                        is_ice = projectile.bullet_type == "winter_melon"
                        splash_c = (160, 240, 255) if is_ice else (120, 220, 90)
                        self.burst(impact_x, impact_y, splash_c, 16, speed=160.0)
                        self.audio.play("squash", cooldown=0.1)
                        if main_target:
                            self._damage_zombie(main_target, 80.0, freeze=is_ice)
                            if is_ice:
                                main_target.slow_timer = 6.0
                        for z in self.zombies:
                            if not z.dead and z != main_target:
                                if abs(z.row - projectile.row) <= 1 and abs(z.x - impact_x) <= 80:
                                    self._damage_zombie(z, 26.0, freeze=is_ice)
                                    if is_ice:
                                        z.slow_timer = 6.0
                continue

            # 普通直线子弹与追踪尖刺命中判定
            for zombie in self.zombies:
                if zombie.dead:
                    continue
                if projectile.is_homing:
                    if abs(zombie.x - projectile.x) > 28 or abs(zombie.y - projectile.y) > 36:
                        continue
                else:
                    if zombie.row != projectile.row or abs(zombie.x - projectile.x) > 30:
                        continue

                # 潜水中的潜水僵尸免疫水平直射
                if getattr(zombie, "is_submerged", False):
                    continue

                projectile.alive = False

                # 火焰豌豆附带小范围溅射
                if projectile.bullet_type == "fire_pea":
                    self.burst(projectile.x, projectile.y, (255, 110, 30), 8, speed=140.0)
                    for z in self.zombies:
                        if z.row == projectile.row and not z.dead and abs(z.x - projectile.x) <= 45 and z != zombie:
                            self._damage_zombie(z, 15.0, freeze=False)

                self._damage_zombie(zombie, projectile.damage, freeze=projectile.freeze)
                break

    def _spawn_natural_sun'''
    text = re_zombies_and_proj.sub(new_zombies_and_proj, text)

    # 11. Update _background to use pvz_graphics.get_map_surface
    old_bg_func = re.compile(r'def _background\(self, theme: str\) -> pygame\.Surface:.*?self\.background_cache\[theme\] = surface\s+return surface', re.DOTALL)
    new_bg_func = '''def _background(self, theme: str) -> pygame.Surface:
        cached = self.background_cache.get(theme)
        if cached is not None:
            return cached

        # 优先读取高清还原地图背景
        map_surf = pvz_graphics.get_map_surface(theme, (WIDTH, HEIGHT))
        if map_surf is not None:
            self.background_cache[theme] = map_surf
            return map_surf

        surface = pygame.Surface((WIDTH, HEIGHT))
        is_pool = theme in ("pool_day", "pool_night")
        rows = 6 if is_pool else 5
        cell_h = 96 if is_pool else 116
        grid_bottom = GRID_Y + rows * cell_h

        sky_top, sky_bottom, grass_light, grass_dark = {
            "day": ((108, 185, 224), (205, 237, 244), (112, 188, 77), (95, 168, 65)),
            "dusk": ((219, 125, 78), (252, 203, 137), (142, 171, 72), (119, 149, 58)),
            "night": ((18, 32, 44), (43, 67, 85), (63, 122, 69), (48, 102, 57)),
            "pool_day": ((108, 185, 224), (205, 237, 244), (112, 188, 77), (95, 168, 65)),
            "pool_night": ((18, 32, 44), (43, 67, 85), (63, 122, 69), (48, 102, 57)),
        }[theme]
        surface.fill(grass_dark)

        for y in range(0, GRID_Y):
            ratio = y / GRID_Y
            color = lerp_color(sky_top, sky_bottom, ratio)
            pygame.draw.line(surface, color, (0, y), (WIDTH, y))

        if "night" in theme:
            for x, y, size in self.stars:
                pygame.draw.circle(surface, (245, 247, 218), (x, y), 1.5 if size > 0.5 else 1.0)
            pygame.draw.circle(surface, (255, 252, 214), (1040, 68), 28)
            pygame.draw.circle(surface, sky_top, (1054, 62), 26)
        elif theme == "dusk":
            pygame.draw.circle(surface, (255, 172, 85), (960, 95), 38)
            pygame.draw.circle(surface, (255, 232, 148), (960, 95), 32)
        else:
            draw_sun_shape(surface, (1080, 58), 26, 0.0, glow=True)

        for col in range(COLS):
            for row in range(rows):
                cell_rect = pygame.Rect(
                    GRID_X + col * CELL_W,
                    GRID_Y + row * cell_h,
                    CELL_W,
                    cell_h,
                )
                if is_pool and row in (2, 3):
                    # 泳池碧波
                    water_c = (52, 148, 204) if (col + row) % 2 == 0 else (42, 128, 182)
                    pygame.draw.rect(surface, water_c, cell_rect)
                    pygame.draw.rect(surface, (80, 180, 230), cell_rect, 1)
                else:
                    base = grass_light if (col + row) % 2 == 0 else grass_dark
                    pygame.draw.rect(surface, base, cell_rect)
                    pygame.draw.rect(surface, lerp_color(base, (22, 50, 28), 0.16), cell_rect, 1)

        for row in range(rows + 1):
            y = GRID_Y + row * cell_h
            pygame.draw.line(surface, (45, 96, 48), (GRID_X - 10, y), (GRID_RIGHT + 10, y), 2)
        for col in range(COLS + 1):
            x = GRID_X + col * CELL_W
            pygame.draw.line(surface, (45, 96, 48), (x, GRID_Y), (x, grid_bottom), 1)

        self._draw_house_edge(surface)
        self._draw_right_garden(surface, theme)
        self.background_cache[theme] = surface
        return surface'''
    text = old_bg_func.sub(new_bg_func, text)

    # 12. Update _draw_entities
    old_draw_entities = '''    def _draw_entities(self) -> None:
        for mower in self.mowers:
            draw_mower(self.screen, mower)
        for plant in sorted(self.plants, key=lambda p: (p.row, p.y)):'''

    new_draw_entities = '''    def _draw_entities(self) -> None:
        for mower in self.mowers:
            is_pool_mower = getattr(self, "is_pool", False) and mower.row in getattr(self, "pool_rows", [])
            draw_mower(self.screen, mower, is_pool=is_pool_mower, cell_h=self.cell_h)
        for plant in sorted(self.plants, key=lambda p: (p.row, 0 if p.ptype == 'lilypad' else 1, p.y)):'''
    text = text.replace(old_draw_entities, new_draw_entities)

    # 13. Update _draw_menu (16 levels support)
    re_menu = re.compile(r'def _draw_menu\(self\) -> None:.*?def _draw_seed_select', re.DOTALL)
    new_menu = '''def _draw_menu(self) -> None:
        if self.menu_background is None:
            background = pygame.Surface((WIDTH, HEIGHT))
            background.fill((27, 62, 46))
            for y in range(0, HEIGHT, 4):
                amount = y / HEIGHT
                color = lerp_color((43, 128, 168), (130, 184, 100), amount)
                pygame.draw.rect(background, color, (0, y, WIDTH, 4))
            pygame.draw.rect(background, (80, 143, 62), (0, 540, WIDTH, 220))
            for i in range(7):
                pygame.draw.arc(background, (56, 118, 55), (i * 180 - 60, 540, 250, 88), math.pi, math.tau, 3)
            self.menu_background = background
        self.screen.blit(self.menu_background, (0, 0))
        for i in range(5):
            x = (i * 310 + int(self.time_value * 8)) % 1500 - 180
            self._cloud(x, 82 + i * 43, 0.8 + i * 0.08)
        self._draw_house_edge(self.screen)
        pygame.draw.ellipse(self.screen, (46, 88, 48), (965, 551, 160, 46))
        draw_zombie(
            self.screen,
            Zombie("pole", 0, 1060, 240, 240, 0, 0, phase=self.time_value * 0.4, has_pole=True),
            self.time_value,
        )
        draw_plant(self.screen, "squash", (850, 596), 1.0, self.time_value)
        draw_plant(self.screen, "sunflower", (920, 606), 0.95, self.time_value)
        draw_plant(self.screen, "chomper", (988, 622), 0.9, self.time_value + 1.0)

        text(self.screen, "植物大战僵尸", self.fonts.get(52, True), C_CREAM, (600, 36), "midtop", (33, 61, 38))
        text(self.screen, "PYGAME  ·  全功能豪华版  ·  草坪与泳池十六关", self.fonts.get(17, True), (255, 225, 137), (600, 96), "midtop")

        save = load_save()
        completed = set(save.get("completed", []))

        self.level_buttons = []
        card_w = 184
        card_h = 74
        gap_x = 18
        gap_y = 10
        x0 = (WIDTH - card_w * 5 - gap_x * 4) // 2
        y0 = 126

        # Draw levels 1 to 10 (草坪章节)
        for i in range(10):
            level = LEVELS[i]
            col = i % 5
            row = i // 5
            rect = pygame.Rect(x0 + col * (card_w + gap_x), y0 + row * (card_h + gap_y), card_w, card_h)
            self.level_buttons.append((rect, i))
            hover = rect.collidepoint(pygame.mouse.get_pos())
            is_done = i in completed
            fill = (255, 246, 207) if not hover else (255, 252, 228)
            border_c = (255, 202, 72) if is_done else (62, 81, 53)
            panel(self.screen, rect, fill, border_c, radius=8, width=3 if is_done else 2, shadow=True)
            badge = pygame.Rect(rect.x + 8, rect.y + 8, 38, 22)
            pygame.draw.rect(self.screen, (72, 128, 62) if not is_done else (205, 145, 45), badge, border_radius=5)
            text(self.screen, f"{i + 1:02d}", self.fonts.get(14, True), C_CREAM, badge.center, "center")
            text(self.screen, level["name"], self.fonts.get(16, True), (54, 60, 43), (rect.x + 52, rect.y + 8))
            text(self.screen, level["subtitle"], self.fonts.get(11), (112, 103, 77), (rect.x + 8, rect.y + 36))
            if is_done:
                text(self.screen, "★ 已通关", self.fonts.get(12, True), (195, 130, 20), (rect.x + 8, rect.y + 54))
            else:
                for j in range(5):
                    color = (112, 174, 76) if j < 2 + (i + 1) // 2 else (208, 207, 178)
                    pygame.draw.rect(self.screen, color, (rect.x + 8 + j * 14, rect.y + 56, 9, 4), border_radius=2)

        # Draw levels 11 to 15 (泳池碧波章节)
        y_pool = y0 + 2 * (card_h + gap_y) + 12
        pygame.draw.line(self.screen, (160, 210, 240, 160), (x0, y_pool - 6), (x0 + card_w * 5 + gap_x * 4, y_pool - 6), 2)
        text(self.screen, "【 泳池水上篇 · 水面六路关卡 】", self.fonts.get(13, True), (210, 245, 255), (600, y_pool - 16), "center")

        for i in range(10, 15):
            level = LEVELS[i]
            col = (i - 10) % 5
            rect = pygame.Rect(x0 + col * (card_w + gap_x), y_pool, card_w, card_h)
            self.level_buttons.append((rect, i))
            hover = rect.collidepoint(pygame.mouse.get_pos())
            is_done = i in completed
            fill = (225, 245, 255) if not hover else (240, 250, 255)
            border_c = (255, 202, 72) if is_done else (42, 118, 172)
            panel(self.screen, rect, fill, border_c, radius=8, width=3 if is_done else 2, shadow=True)
            badge = pygame.Rect(rect.x + 8, rect.y + 8, 38, 22)
            pygame.draw.rect(self.screen, (45, 125, 180) if not is_done else (205, 145, 45), badge, border_radius=5)
            text(self.screen, f"{i + 1:02d}", self.fonts.get(14, True), C_CREAM, badge.center, "center")
            text(self.screen, level["name"], self.fonts.get(16, True), (28, 54, 82), (rect.x + 52, rect.y + 8))
            text(self.screen, level["subtitle"], self.fonts.get(11), (72, 102, 128), (rect.x + 8, rect.y + 36))
            if is_done:
                text(self.screen, "★ 已通关", self.fonts.get(12, True), (195, 130, 20), (rect.x + 8, rect.y + 54))
            else:
                for j in range(5):
                    color = (72, 164, 226) if j < 3 + (i - 10) // 2 else (190, 215, 230)
                    pygame.draw.rect(self.screen, color, (rect.x + 8 + j * 14, rect.y + 56, 9, 4), border_radius=2)

        # Level 16 Endless Mode Card (水陆无尽)
        y_endless = y_pool + card_h + gap_y + 4
        endless_rect = pygame.Rect(x0, y_endless, card_w * 5 + gap_x * 4, 58)
        self.level_buttons.append((endless_rect, 15))
        e_hover = endless_rect.collidepoint(pygame.mouse.get_pos())
        panel(self.screen, endless_rect, (64, 40, 85) if not e_hover else (82, 52, 108), (255, 215, 95), radius=10, width=3)
        text(self.screen, "👑 第 16 关 · 水陆无尽大挑战 (ENDLESS POOL SURVIVAL)", self.fonts.get(20, True), (255, 235, 140), (endless_rect.x + 24, endless_rect.y + 10))
        best_w = save.get("endless_best", 0)
        e_info = f"极限水陆两栖无尽挑战！全 23 种植物大战全 9 种水陆僵尸 · 历史最佳坚守：{best_w} 轮"
        text(self.screen, e_info, self.fonts.get(13), (220, 215, 240), (endless_rect.x + 28, endless_rect.y + 34))

        bar = pygame.Rect(312, 478, 576, 50)
        panel(self.screen, bar, (38, 80, 47), (22, 47, 31), radius=12, width=2)
        text(self.screen, "点击任意关卡开始挑战", self.fonts.get(18, True), C_CREAM, (600, 492), "center")
        text(
            self.screen, "Space/F 倍速  ·  C 键全屏收阳光  ·  1-8 快捷选植物  ·  Esc 退出",
            self.fonts.get(13), (206, 223, 186), (600, 514), "center",
        )
        text(
            self.screen, "全量实装 23 种原版植物、9 种水陆僵尸、泳池 6 行水面地图与制导/抛物线机制",
            self.fonts.get(14, True), (255, 230, 130), (600, 706), "center",
        )

    def _draw_seed_select'''
    text = re_menu.sub(new_menu, text)

    # 14. Update _draw_seed_select (23 plants in 6 cols x 4 rows)
    re_seed_select = re.compile(r'def _draw_seed_select\(self\) -> None:.*?def _cloud', re.DOTALL)
    new_seed_select = '''def _draw_seed_select(self) -> None:
        level = LEVELS[self.level_index]
        self._draw_game_background()

        # Preview incoming zombies
        mix = level.get("mix", ())
        types = list(ZOMBIES)
        active_zombies = [name for name, weight in zip(types, mix) if weight > 0]
        for r_idx, ztype in enumerate(active_zombies[:5]):
            pz = Zombie(ztype, r_idx % self.rows, 1050 + (r_idx % 2) * 45, 100, 100, 0, 0, phase=self.time_value * 0.4, cell_h=self.cell_h)
            if ztype == "pole":
                pz.has_pole = True
            elif ztype == "dolphin":
                pz.has_dolphin = True
            draw_zombie(self.screen, pz, self.time_value)

        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((12, 22, 16, 155))
        self.screen.blit(veil, (0, 0))

        # Top Bar: 出战植物卡槽 (Seed Bank)
        bank_rect = pygame.Rect(260, 12, 680, 84)
        panel(self.screen, bank_rect, (82, 54, 30), (45, 28, 14), radius=10, width=3, shadow=True)

        text(self.screen, "出战卡槽", self.fonts.get(17, True), (255, 235, 140), (bank_rect.x - 16, bank_rect.y + 16), "topright", (40, 30, 20))
        text(self.screen, f"{len(self.selected_seeds)}/{self.slot_capacity} (点击下阵)", self.fonts.get(12), (210, 210, 190), (bank_rect.x - 16, bank_rect.y + 44), "topright")

        slot_w = 70
        slot_h = 70
        slot_gap = 8
        sx0 = bank_rect.x + (bank_rect.width - (self.slot_capacity * (slot_w + slot_gap) - slot_gap)) // 2
        sy0 = bank_rect.y + 7

        self.slot_rects = []
        mouse_pos = pygame.mouse.get_pos()
        for i in range(self.slot_capacity):
            srect = pygame.Rect(sx0 + i * (slot_w + slot_gap), sy0, slot_w, slot_h)
            self.slot_rects.append(srect)
            hover = srect.collidepoint(mouse_pos)
            if i < len(self.selected_seeds):
                name = self.selected_seeds[i]
                card_img = pvz_graphics.get_card_surface(name, (slot_w, slot_h))
                if card_img:
                    self.screen.blit(card_img, srect)
                else:
                    panel(self.screen, srect, (247, 235, 184), (66, 75, 44), radius=6, width=2, shadow=False)
                    draw_plant(self.screen, name, (srect.centerx, srect.y + 30), 0.30, self.time_value)
                    text(self.screen, PLANTS[name]["name"], self.fonts.get(11, True), (58, 60, 42), (srect.centerx, srect.y + 46), "midtop")
                if hover:
                    pygame.draw.rect(self.screen, (240, 80, 70), srect, 3, border_radius=6)
                    rm_badge = pygame.Rect(srect.centerx - 22, srect.centery - 10, 44, 20)
                    pygame.draw.rect(self.screen, (200, 40, 40, 220), rm_badge, border_radius=4)
                    text(self.screen, "下阵", self.fonts.get(11, True), C_CREAM, rm_badge.center, "center")
                else:
                    pygame.draw.rect(self.screen, (220, 190, 120), srect, 2, border_radius=6)

                hk_rect = pygame.Rect(srect.x + 3, srect.y + 3, 16, 16)
                pygame.draw.rect(self.screen, (20, 28, 22, 210), hk_rect, border_radius=4)
                pygame.draw.rect(self.screen, (90, 120, 95), hk_rect, 1, border_radius=4)
                text(self.screen, str(i + 1), self.fonts.get(10, True), C_CREAM, hk_rect.center, "center")
            else:
                pygame.draw.rect(self.screen, (58, 38, 22), srect, border_radius=6)
                pygame.draw.rect(self.screen, (108, 80, 50), srect, 2, border_radius=6)
                text(self.screen, f"槽位 {i + 1}", self.fonts.get(12), (125, 98, 68), srect.center, "center")

        # Center Catalog Board
        cat_rect = pygame.Rect(140, 104, 920, 528)
        panel(self.screen, cat_rect, (244, 233, 202), (68, 48, 26), radius=14, width=4, shadow=True)

        theme_names = {"day": "白天", "dusk": "黄昏", "night": "黑夜", "pool_day": "泳池日间", "pool_night": "泳池暗夜"}
        theme_cn = theme_names.get(level.get("theme", "day"), "常规")
        title_text = f"第 {self.level_index + 1} 关 · {level['name']}  [ {theme_cn} · 初始阳光: {level['sun']} ]"
        text(self.screen, title_text, self.fonts.get(19, True), (62, 44, 22), (cat_rect.centerx, cat_rect.y + 10), "midtop")
        text(
            self.screen,
            "点击植物卡牌加入出战槽，至多选择 8 种；快捷键: [R] 智能推荐  [C] 清空卡槽  [Enter] 确认开打",
            self.fonts.get(12), (120, 92, 55), (cat_rect.centerx, cat_rect.y + 34), "midtop",
        )
        pygame.draw.line(self.screen, (185, 160, 125), (cat_rect.x + 24, cat_rect.y + 54), (cat_rect.right - 24, cat_rect.y + 54), 2)

        # 23 Plants Catalog Grid (6 cols x 4 rows)
        unlocked = set(self.available_plants())
        cw = 120
        ch = 82
        gap_x = 22
        gap_y = 8
        gx0 = cat_rect.x + (cat_rect.width - (6 * cw + 5 * gap_x)) // 2
        gy0 = cat_rect.y + 60

        self.catalog_rects = {}
        hovered_plant = None
        for idx, name in enumerate(UNLOCK_ORDER):
            col = idx % 6
            row = idx // 6
            crect = pygame.Rect(gx0 + col * (cw + gap_x), gy0 + row * (ch + gap_y), cw, ch)
            self.catalog_rects[name] = crect
            is_unlocked = name in unlocked
            is_selected = name in self.selected_seeds
            hover = crect.collidepoint(mouse_pos)
            if hover and is_unlocked:
                hovered_plant = name

            if not is_unlocked:
                panel(self.screen, crect, (205, 202, 195), (145, 140, 130), radius=7, width=1, shadow=False)
                text(self.screen, "未解锁", self.fonts.get(13, True), (130, 130, 130), (crect.centerx, crect.centery - 8), "center")
                text(self.screen, PLANTS[name]["name"], self.fonts.get(11), (150, 150, 150), (crect.centerx, crect.centery + 12), "center")
            else:
                card_img = pvz_graphics.get_card_surface(name, (cw, ch))
                if card_img:
                    self.screen.blit(card_img, crect)
                else:
                    panel(self.screen, crect, (248, 237, 192), (72, 80, 52), radius=7, width=2, shadow=False)
                    draw_plant(self.screen, name, (crect.centerx, crect.y + 36), 0.35, self.time_value)
                    text(self.screen, PLANTS[name]["name"], self.fonts.get(11, True), (55, 58, 42), (crect.centerx, crect.y + 58), "midtop")
                    cost_badge = pygame.Rect(crect.right - 38, crect.bottom - 20, 34, 16)
                    pygame.draw.rect(self.screen, (52, 70, 44), cost_badge, border_radius=4)
                    text(self.screen, str(PLANTS[name]["cost"]), self.fonts.get(10, True), C_SUN, cost_badge.center, "center")

                if is_selected:
                    shade = pygame.Surface((cw, ch), pygame.SRCALPHA)
                    shade.fill((16, 55, 26, 175))
                    self.screen.blit(shade, crect)
                    tag_rect = pygame.Rect(crect.centerx - 34, crect.centery - 12, 68, 24)
                    pygame.draw.rect(self.screen, (36, 135, 42), tag_rect, border_radius=5)
                    pygame.draw.rect(self.screen, (215, 255, 215), tag_rect, 2, border_radius=5)
                    text(self.screen, "已出战", self.fonts.get(12, True), C_CREAM, tag_rect.center, "center")
                else:
                    if hover:
                        pygame.draw.rect(self.screen, C_GOLD, crect, 3, border_radius=7)
                    else:
                        pygame.draw.rect(self.screen, (85, 65, 42), crect, 2, border_radius=6)

        # Plant Description Box at bottom of catalog
        desc_box = pygame.Rect(cat_rect.x + 20, cat_rect.bottom - 98, cat_rect.width - 40, 84)
        panel(self.screen, desc_box, (232, 220, 188), (145, 120, 85), radius=8, width=2, shadow=False)
        if hovered_plant:
            p_cfg = PLANTS[hovered_plant]
            desc = PLANT_TIPS.get(hovered_plant, "")
            text(
                self.screen,
                f"【{p_cfg['name']}】 消耗: {p_cfg['cost']}阳光  |  冷却时间: {p_cfg['cooldown']}秒  |  生命值: {p_cfg['hp']}",
                self.fonts.get(13, True), (70, 45, 20), (desc_box.x + 14, desc_box.y + 10),
            )
            text(self.screen, desc, self.fonts.get(12), (85, 68, 48), (desc_box.x + 14, desc_box.y + 36))
        else:
            if level.get("pool"):
                advice = "【战术提示】 本关为泳池水面！必须先在水中种植【睡莲】，方可种植陆生植物；【猫尾草】可全图自动追踪突袭！"
            elif level.get("theme") == "night":
                advice = "【战术提示】 本关为夜间！推荐携带【小喷菇】(0费防守神器) 与【阳光菇】作为主力，配合【寒冰菇】全屏冰控！"
            else:
                advice = "【战术提示】 白天必备【向日葵】保障经济；面对大群僵尸，【卷心菜投手】、【玉米投手】与【火炬树桩】威力绝伦！"
            text(self.screen, advice, self.fonts.get(12, True), (80, 60, 35), (desc_box.centerx, desc_box.centery), "center")

        # Bottom Action Buttons
        b_hover = self.seed_btn_back.collidepoint(mouse_pos)
        panel(self.screen, self.seed_btn_back, (62, 54, 46) if not b_hover else (82, 72, 62), (180, 170, 150), radius=10, width=2)
        text(self.screen, "返回菜单 [Esc]", self.fonts.get(14, True), C_CREAM, self.seed_btn_back.center, "center")

        c_hover = self.seed_btn_clear.collidepoint(mouse_pos)
        panel(self.screen, self.seed_btn_clear, (160, 62, 52) if not c_hover else (190, 78, 68), (240, 180, 170), radius=10, width=2)
        text(self.screen, "清空卡槽 [C]", self.fonts.get(14, True), C_CREAM, self.seed_btn_clear.center, "center")

        s_hover = self.seed_btn_start.collidepoint(mouse_pos)
        can_start = len(self.selected_seeds) > 0
        s_fill = (44, 138, 56) if can_start else (95, 115, 100)
        if can_start and s_hover:
            s_fill = (56, 172, 72)
        panel(self.screen, self.seed_btn_start, s_fill, (255, 218, 90) if can_start else (150, 165, 155), radius=12, width=3)
        text(self.screen, "摇滚开打！[Enter]", self.fonts.get(20, True), (255, 245, 160) if can_start else (200, 210, 205), self.seed_btn_start.center, "center")

        r_hover = self.seed_btn_recommend.collidepoint(mouse_pos)
        panel(self.screen, self.seed_btn_recommend, (45, 102, 148) if not r_hover else (58, 128, 185), (170, 215, 245), radius=10, width=2)
        text(self.screen, "智能推荐 [R]", self.fonts.get(14, True), C_CREAM, self.seed_btn_recommend.center, "center")

    def _cloud'''
    text = re_seed_select.sub(new_seed_select, text)

    # 15. Update setup_preview to support pool showcase
    re_preview = re.compile(r'def setup_preview\(self, level_index: int\) -> None:.*?def parse_args', re.DOTALL)
    new_preview = '''def setup_preview(self, level_index: int) -> None:
        self.start_level(level_index)
        self.mode = "playing"
        if not self.selected_seeds:
            self._recommend_seeds()
        self.banner_timer = 0
        self.intro_timer = 0
        self.elapsed = 20
        self.current_wave_index = len(self.waves) - 1
        self.next_wave_at = float("inf")
        self.pending_wave_spawns = []
        self.sun = 575
        self.cooldowns = {name: 0 for name in UNLOCK_ORDER}

        if getattr(self, "is_pool", False):
            # 泳池 6 行豪华演示阵容
            demo_plants = [
                ("sunflower", 0, 0), ("sunflower", 0, 1),
                ("lilypad", 0, 2), ("lilypad", 0, 3), ("cattail", 0, 2),
                ("sunflower", 0, 4), ("sunflower", 0, 5),
                ("cabbagepult", 1, 0), ("repeater", 2, 0), ("torchwood", 3, 0), ("wallnut", 5, 0),
                ("melonpult", 1, 1), ("wintermelon", 2, 1), ("garlic", 4, 1),
                ("lilypad", 1, 2), ("kernelpult", 1, 2), ("lilypad", 2, 2), ("repeater", 2, 2),
                ("lilypad", 1, 3), ("cattail", 1, 3), ("lilypad", 2, 3), ("wallnut", 4, 3),
                ("kernelpult", 1, 4), ("torchwood", 3, 4), ("garlic", 4, 4),
                ("cabbagepult", 1, 5), ("snowpea", 2, 5), ("wallnut", 5, 5),
            ]
            self.plants = []
            for name, col, row in demo_plants:
                p = Plant(name, col, row, PLANTS[name]["hp"], PLANTS[name]["hp"], age=8.0, cell_h=self.cell_h)
                self.plants.append(p)

            demo_zombies = [
                ("basic", 0, 1020), ("cone", 0, 1140),
                ("bucket", 1, 880), ("pole", 1, 1090),
                ("ducky", 2, 780), ("snorkel", 2, 940),
                ("dolphin", 3, 860), ("ducky", 3, 1120),
                ("runner", 4, 820), ("newspaper", 4, 1040),
                ("bucket", 5, 910), ("basic", 5, 1130),
            ]
            self.zombies = []
            for ztype, row, x in demo_zombies:
                config = ZOMBIES[ztype]
                zombie = Zombie(ztype, row, x, config["hp"] * 0.82, config["hp"], config["speed"], config["damage"], cell_h=self.cell_h)
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
                    zombie.is_submerged = (x > 850)
                if row == 1:
                    zombie.slow_timer = 3.0
                self.zombies.append(zombie)

            self.projectiles = [
                Projectile(580, lane_ground(0, cell_h=self.cell_h) - 70, 0, 40, bullet_type="fire_pea"),
                Projectile(620, lane_ground(1, cell_h=self.cell_h) - 70, 1, 80, bullet_type="winter_melon", is_lobbed=True, start_x=340, start_y=lane_ground(1, cell_h=self.cell_h) - 90, target_x=880, target_y=lane_ground(1, cell_h=self.cell_h) - 50, lob_progress=0.6),
                Projectile(480, lane_ground(2, cell_h=self.cell_h) - 70, 2, 40, bullet_type="butter", is_lobbed=True, start_x=260, start_y=lane_ground(2, cell_h=self.cell_h) - 80, target_x=780, target_y=lane_ground(2, cell_h=self.cell_h) - 50, lob_progress=0.45),
                Projectile(690, lane_ground(3, cell_h=self.cell_h) - 60, 3, 20, bullet_type="cattail_spike", is_homing=True),
            ]
        else:
            demo_plants = [
                ("sunflower", 0, 0), ("sunflower", 0, 1), ("sunshroom", 0, 2),
                ("sunflower", 0, 3), ("sunflower", 0, 4),
                ("peashooter", 2, 0), ("wallnut", 4, 0),
                ("snowpea", 2, 1), ("repeater", 3, 1), ("wallnut", 5, 1),
                ("threepeater", 2, 2), ("puffshroom", 3, 2), ("spikeweed", 4, 2), ("squash", 5, 2),
                ("snowpea", 2, 3), ("repeater", 3, 3), ("chomper", 4, 3),
                ("peashooter", 2, 4), ("cherrybomb", 4, 4), ("jalapeno", 6, 2),
            ]
            self.plants = [
                Plant(name, col, row, PLANTS[name]["hp"], PLANTS[name]["hp"], age=7.0, cell_h=self.cell_h)
                for name, col, row in demo_plants
            ]
            demo_zombies = [
                ("basic", 0, 1015), ("cone", 1, 855), ("bucket", 1, 1110),
                ("runner", 2, 760), ("pole", 3, 910), ("newspaper", 4, 820),
                ("bucket", 3, 1170), ("basic", 2, 1080),
            ]
            self.zombies = []
            for ztype, row, x in demo_zombies:
                config = ZOMBIES[ztype]
                zombie = Zombie(ztype, row, x, config["hp"] * 0.76, config["hp"], config["speed"], config["damage"], cell_h=self.cell_h)
                if ztype == "pole":
                    zombie.has_pole = True
                    zombie.vault_state = "run"
                elif ztype == "newspaper":
                    zombie.has_newspaper = True
                    zombie.newspaper_hp = 140.0
                if row == 2 and ztype == "runner":
                    zombie.slow_timer = 2.0
                self.zombies.append(zombie)
            self.projectiles = [
                Projectile(620, lane_ground(0, cell_h=self.cell_h) - 70, 0, 25),
                Projectile(520, lane_ground(1, cell_h=self.cell_h) - 70, 1, 25, freeze=True),
                Projectile(680, lane_ground(3, cell_h=self.cell_h) - 70, 3, 25),
            ]

        self.suns = [
            SunToken(250, 250, 250, phase=0.2),
            SunToken(745, 435, 435, phase=1.6),
            SunToken(920, 200, 200, phase=3.3),
        ]
        self.spawned_count = 18

    def parse_args'''
    text = re_preview.sub(new_preview, text)

    PVZ_FILE.write_text(text, encoding="utf-8")
    print("All gameplay mechanics applied successfully.")

if __name__ == "__main__":
    run_update()
