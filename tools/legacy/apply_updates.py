# -*- coding: utf-8 -*-
"""Script to apply full updates for 23 plants, 9 zombies, and 16 levels to pvz_ten_levels.py."""

from pathlib import Path
import re

PVZ_FILE = Path(__file__).resolve().parent.parent / "pvz_ten_levels.py"

def update_pvz():
    content = PVZ_FILE.read_text(encoding="utf-8")

    # 1. Update cell_center and lane_ground to accept cell_h
    old_centers = '''def cell_center(col: int, row: int) -> tuple[int, int]:
    return (
        GRID_X + int((col + 0.5) * CELL_W),
        GRID_Y + int((row + 0.5) * CELL_H),
    )


def lane_ground(row: int) -> int:
    return GRID_Y + (row + 1) * CELL_H - 13'''

    new_centers = '''def cell_center(col: int, row: int, cell_h: int = CELL_H) -> tuple[int, int]:
    return (
        GRID_X + int((col + 0.5) * CELL_W),
        GRID_Y + int((row + 0.5) * cell_h),
    )


def lane_ground(row: int, cell_h: int = CELL_H) -> int:
    return GRID_Y + (row + 1) * cell_h - (13 if cell_h >= 110 else 8)'''

    if old_centers in content:
        content = content.replace(old_centers, new_centers)
        print("Updated cell_center and lane_ground.")

    # 2. Update PLANTS, UNLOCK_ORDER, PLANT_TIPS, ZOMBIES, LEVELS
    pattern_consts = re.compile(r'PLANTS = \{.*?LEVELS = \[.*?\]\n', re.DOTALL)
    
    new_consts = '''PLANTS = {
    "sunflower": {
        "name": "向日葵", "cost": 50, "cooldown": 5.0, "hp": 300,
    },
    "peashooter": {
        "name": "豌豆射手", "cost": 100, "cooldown": 5.5, "hp": 300,
    },
    "wallnut": {
        "name": "坚果墙", "cost": 50, "cooldown": 15.0, "hp": 1500,
    },
    "snowpea": {
        "name": "寒冰射手", "cost": 175, "cooldown": 8.0, "hp": 300,
    },
    "squash": {
        "name": "窝瓜", "cost": 50, "cooldown": 16.0, "hp": 300,
    },
    "cherrybomb": {
        "name": "樱桃炸弹", "cost": 150, "cooldown": 20.0, "hp": 9999,
    },
    "repeater": {
        "name": "双发射手", "cost": 200, "cooldown": 10.0, "hp": 300,
    },
    "potatomine": {
        "name": "土豆雷", "cost": 25, "cooldown": 18.0, "hp": 300,
    },
    "chomper": {
        "name": "大嘴花", "cost": 150, "cooldown": 12.0, "hp": 300,
    },
    "jalapeno": {
        "name": "火爆辣椒", "cost": 125, "cooldown": 20.0, "hp": 9999,
    },
    "threepeater": {
        "name": "三线射手", "cost": 300, "cooldown": 12.0, "hp": 300,
    },
    "spikeweed": {
        "name": "地刺", "cost": 100, "cooldown": 7.5, "hp": 9999,
    },
    "puffshroom": {
        "name": "小喷菇", "cost": 0, "cooldown": 7.5, "hp": 200,
    },
    "sunshroom": {
        "name": "阳光菇", "cost": 25, "cooldown": 7.5, "hp": 250,
    },
    "iceshroom": {
        "name": "寒冰菇", "cost": 75, "cooldown": 25.0, "hp": 9999,
    },
    "lilypad": {
        "name": "睡莲", "cost": 25, "cooldown": 5.0, "hp": 300,
    },
    "torchwood": {
        "name": "火炬树桩", "cost": 175, "cooldown": 7.5, "hp": 300,
    },
    "cabbagepult": {
        "name": "卷心菜投手", "cost": 100, "cooldown": 7.5, "hp": 300,
    },
    "kernelpult": {
        "name": "玉米投手", "cost": 100, "cooldown": 7.5, "hp": 300,
    },
    "melonpult": {
        "name": "西瓜投手", "cost": 300, "cooldown": 7.5, "hp": 300,
    },
    "wintermelon": {
        "name": "冰西瓜投手", "cost": 500, "cooldown": 15.0, "hp": 300,
    },
    "garlic": {
        "name": "大蒜", "cost": 50, "cooldown": 7.5, "hp": 400,
    },
    "cattail": {
        "name": "猫尾草", "cost": 225, "cooldown": 15.0, "hp": 300,
    },
}

UNLOCK_ORDER = [
    "sunflower",
    "peashooter",
    "wallnut",
    "snowpea",
    "puffshroom",
    "sunshroom",
    "squash",
    "cherrybomb",
    "spikeweed",
    "repeater",
    "potatomine",
    "threepeater",
    "chomper",
    "iceshroom",
    "jalapeno",
    "lilypad",
    "torchwood",
    "cabbagepult",
    "kernelpult",
    "garlic",
    "cattail",
    "melonpult",
    "wintermelon",
]

PLANT_TIPS = {
    "sunflower": "向日葵：每隔 24 秒生产 25 点阳光，白天必备的基础经济植物。",
    "peashooter": "豌豆射手：向前发射豌豆攻击僵尸，单发伤害 20 点，基础对单火力。",
    "wallnut": "坚果墙：拥有 1500 超高生命值，阻挡僵尸前进的坚固钢铁屏障。",
    "snowpea": "寒冰射手：发射冰冻豌豆，造成 20 伤害并使僵尸移速与攻速降低 50%。",
    "puffshroom": "小喷菇：0 阳光速射！射程 3 格，夜间开局抗压神器，成群威力极大。",
    "sunshroom": "阳光菇：开局生产 15 阳光，成熟后大产 25 阳光，夜间首选经济核心。",
    "squash": "窝瓜：发现僵尸靠近时跃起猛砸，造成 1800 点范围毁灭伤害，秒杀精英。",
    "cherrybomb": "樱桃炸弹：种植后瞬间爆炸，摧毁 3x3 范围内所有僵尸（伤害 1800）！",
    "spikeweed": "地刺：不可被啃咬！扎伤经过的所有僵尸，持续克制集群与高速怪。",
    "repeater": "双发射手：每次射出 2 颗豌豆，提供双倍持续火力压制，高效中坚力量。",
    "potatomine": "土豆雷：消耗极低！出土准备完成后秒杀接触的僵尸，完美克制单怪。",
    "threepeater": "三线射手：一次性向本行及上下相邻两行齐射 3 枚豌豆，全图火力覆盖！",
    "chomper": "大嘴花：一口吞噬正前方僵尸（包含铁桶/读报），咀嚼期间需坚果保护。",
    "iceshroom": "寒冰菇：全屏大招！全场僵尸冰封 12 秒并附带减速，绝境翻盘神技！",
    "jalapeno": "火爆辣椒：消灭整整一整行的全部僵尸，火海清场绝杀利器。",
    "lilypad": "睡莲：水面承载基石！种植在泳池水路上，使你能够在水面上种植任何陆地植物。",
    "torchwood": "火炬树桩：普通豌豆穿过后点燃为双倍伤害的烈焰火球；还能融化寒冰豌豆解除减速！",
    "cabbagepult": "卷心菜投手：以抛物线弧线投掷卷心菜，造成 40 点重击伤害，克制潜水僵尸！",
    "kernelpult": "玉米投手：投掷轻型玉米粒或黄油块；黄油命中后定身眩晕僵尸 4 秒，强力控场！",
    "melonpult": "西瓜投手：投掷重型西瓜，直接命中造成 80 巨额伤害，并在周围引发范围强力溅射！",
    "wintermelon": "冰西瓜投手：顶级战术植物！造成 80 范围重创的同时，使命中范围的所有僵尸减速 50%！",
    "garlic": "大蒜：耐嚼刺鼻！任何僵尸啃咬大蒜后都会嫌恶变道，将尸群分流至其它重兵防线。",
    "cattail": "猫尾草：水生制导王者！种植在睡莲上，可向全图任何一行的僵尸发射自动追踪刺针！",
}

ZOMBIES = {
    "basic": {"name": "普通僵尸", "hp": 170, "speed": 18.0, "damage": 28},
    "cone": {"name": "路障僵尸", "hp": 290, "speed": 17.0, "damage": 30},
    "bucket": {"name": "铁桶僵尸", "hp": 470, "speed": 15.0, "damage": 34},
    "runner": {"name": "奔跑僵尸", "hp": 155, "speed": 31.0, "damage": 24},
    "pole": {"name": "撑杆僵尸", "hp": 240, "speed": 32.0, "damage": 28},
    "newspaper": {"name": "读报僵尸", "hp": 280, "speed": 14.0, "damage": 28},
    "ducky": {"name": "鸭子救生圈僵尸", "hp": 200, "speed": 18.0, "damage": 28, "water": True},
    "snorkel": {"name": "潜水僵尸", "hp": 240, "speed": 20.0, "damage": 30, "water": True},
    "dolphin": {"name": "海豚骑士僵尸", "hp": 320, "speed": 36.0, "damage": 30, "water": True},
}

LEVELS = [
    {
        "name": "草坪初醒", "subtitle": "第一波僵尸正在靠近",
        "sun": 150, "count": 7,
        "mix": (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00), "theme": "day",
    },
    {
        "name": "向阳生长", "subtitle": "阳光越多，防线越稳",
        "sun": 150, "count": 9,
        "mix": (0.80, 0.20, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00), "theme": "day",
    },
    {
        "name": "坚果防线", "subtitle": "把危险挡在门外",
        "sun": 150, "count": 11,
        "mix": (0.65, 0.35, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00), "theme": "day",
    },
    {
        "name": "撑杆越障", "subtitle": "小心飞跃防线的撑杆跳手",
        "sun": 175, "count": 13,
        "mix": (0.50, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00), "theme": "dusk",
    },
    {
        "name": "铁桶警告", "subtitle": "硬壳僵尸闯进草坪",
        "sun": 175, "count": 15,
        "mix": (0.42, 0.28, 0.16, 0.00, 0.14, 0.00, 0.00, 0.00, 0.00), "theme": "dusk",
    },
    {
        "name": "读报愤怒", "subtitle": "撕碎报纸的瞬间极其危险",
        "sun": 200, "count": 18,
        "mix": (0.35, 0.25, 0.15, 0.00, 0.10, 0.15, 0.00, 0.00, 0.00), "theme": "dusk",
    },
    {
        "name": "旗帜浪潮", "subtitle": "一大波混合僵尸即将到来",
        "sun": 200, "count": 22,
        "mix": (0.32, 0.24, 0.18, 0.08, 0.10, 0.08, 0.00, 0.00, 0.00), "theme": "day",
    },
    {
        "name": "月夜花园", "subtitle": "月光下也不能松懈",
        "sun": 225, "count": 26,
        "mix": (0.28, 0.22, 0.18, 0.12, 0.10, 0.10, 0.00, 0.00, 0.00), "theme": "night",
    },
    {
        "name": "极速进攻", "subtitle": "脚步声比往常更快",
        "sun": 225, "count": 28,
        "mix": (0.24, 0.20, 0.20, 0.16, 0.10, 0.10, 0.00, 0.00, 0.00), "theme": "night",
    },
    {
        "name": "黑夜决战", "subtitle": "守住草坪最后一条防线",
        "sun": 400, "count": 32,
        "mix": (0.26, 0.22, 0.18, 0.12, 0.11, 0.11, 0.00, 0.00, 0.00), "theme": "night",
    },
    {
        "name": "阳光碧波", "subtitle": "水面初遇！鸭子救生圈僵尸登场",
        "sun": 250, "count": 18,
        "mix": (0.28, 0.22, 0.15, 0.00, 0.00, 0.00, 0.35, 0.00, 0.00), "theme": "pool_day",
        "pool": True,
    },
    {
        "name": "潜水突袭", "subtitle": "直射无效！用投手植物重创潜水怪",
        "sun": 275, "count": 24,
        "mix": (0.20, 0.20, 0.15, 0.00, 0.00, 0.00, 0.25, 0.20, 0.00), "theme": "pool_day",
        "pool": True,
    },
    {
        "name": "海豚跃浪", "subtitle": "飞跃防线！大蒜分流与猫尾草迎敌",
        "sun": 300, "count": 28,
        "mix": (0.18, 0.18, 0.14, 0.00, 0.00, 0.00, 0.20, 0.15, 0.15), "theme": "pool_day",
        "pool": True,
    },
    {
        "name": "浓雾夜泳", "subtitle": "迷雾笼罩！暗夜水陆混合狂攻",
        "sun": 350, "count": 34,
        "mix": (0.15, 0.18, 0.17, 0.10, 0.00, 0.00, 0.15, 0.12, 0.13), "theme": "pool_night",
        "pool": True,
    },
    {
        "name": "水陆决战", "subtitle": "全兵种终极大决战！守住全场",
        "sun": 600, "count": 42,
        "mix": (0.14, 0.16, 0.16, 0.10, 0.08, 0.08, 0.10, 0.09, 0.09), "theme": "pool_night",
        "pool": True,
    },
    {
        "name": "水陆无尽", "subtitle": "极限泳池生存，水陆两栖永无止境！",
        "sun": 500, "count": 50,
        "mix": (0.15, 0.15, 0.15, 0.10, 0.08, 0.08, 0.10, 0.09, 0.10), "theme": "pool_day",
        "pool": True, "endless": True,
    },
]
'''
    if pattern_consts.search(content):
        content = pattern_consts.sub(new_consts, content)
        print("Updated PLANTS, UNLOCK_ORDER, PLANT_TIPS, ZOMBIES, LEVELS.")

    # 3. Add sound effects to AudioBank
    old_sounds = '''                "groan": self._tone(110, 160, 0.40, 0.30, 0.35),
            }'''
    new_sounds = '''                "groan": self._tone(110, 160, 0.40, 0.30, 0.35),
                "splash": self._tone(320, 160, 0.28, 0.28, 0.35),
                "butter": self._tone(450, 220, 0.20, 0.35, 0.20),
            }'''
    if old_sounds in content:
        content = content.replace(old_sounds, new_sounds)
        print("Updated AudioBank sounds.")

    # 4. Update Plant, Zombie, Projectile, Mower dataclasses
    pattern_dataclasses = re.compile(r'@dataclass\s+class Plant:.*?class Game:', re.DOTALL)
    new_dataclasses = '''@dataclass
class Plant:
    ptype: str
    col: int
    row: int
    hp: float
    max_hp: float
    age: float = 0.0
    action_timer: float = 0.0
    alive: bool = True
    exploded: bool = False
    flash: float = 0.0
    swallow_timer: float = 0.0
    squash_state: str = "idle"
    squash_timer: float = 0.0
    squash_target_x: float = 0.0
    cell_h: int = CELL_H
    carrier: "Plant | None" = None
    carried_plant: "Plant | None" = None

    def __post_init__(self) -> None:
        self._x, self._y = cell_center(self.col, self.row, cell_h=self.cell_h)

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - 42, self.y - 50, 84, 98)


@dataclass
class Zombie:
    ztype: str
    row: int
    x: float
    hp: float
    max_hp: float
    speed: float
    damage: float
    phase: float = field(default_factory=lambda: random.random() * 6.0)
    slow_timer: float = 0.0
    eating: float = 0.0
    bite_timer: float = 0.0
    dead: bool = False
    death_timer: float = 0.0
    flash: float = 0.0
    wave_id: int = -1
    has_pole: bool = False
    vault_state: str = "run"
    vault_progress: float = 0.0
    has_newspaper: bool = False
    newspaper_hp: float = 140.0
    enraged: bool = False
    cell_h: int = CELL_H
    butter_timer: float = 0.0
    is_submerged: bool = False
    has_dolphin: bool = False

    @property
    def y(self) -> float:
        return lane_ground(self.row, cell_h=self.cell_h) - 50.0

    def rect(self) -> pygame.Rect:
        ground = lane_ground(self.row, cell_h=self.cell_h)
        return pygame.Rect(int(self.x - 28), ground - 118, 58, 120)


@dataclass(frozen=True)
class WaveMember:
    delay: float
    ztype: str
    row: int


@dataclass
class Wave:
    index: int
    members: list[WaveMember]
    total_hp: float
    advance_ratio: float
    fallback_gap: float


@dataclass
class Projectile:
    x: float
    y: float
    row: int
    damage: float
    speed: float = 430.0
    freeze: bool = False
    alive: bool = True
    bullet_type: str = "pea"
    is_lobbed: bool = False
    start_x: float = 0.0
    start_y: float = 0.0
    target_x: float = 0.0
    target_y: float = 0.0
    lob_progress: float = 0.0
    lob_duration: float = 1.0
    apex_h: float = 120.0
    is_homing: bool = False
    target_zombie: object = None

    def update(self, dt: float) -> None:
        if self.is_homing:
            if self.target_zombie and not getattr(self.target_zombie, "dead", True):
                tx = getattr(self.target_zombie, "x", self.x)
                ty = getattr(self.target_zombie, "y", self.y)
                dx = tx - self.x
                dy = ty - self.y
                dist = math.hypot(dx, dy)
                if dist > 0.01:
                    step = min(dist, self.speed * dt)
                    self.x += (dx / dist) * step
                    self.y += (dy / dist) * step
                if dist < 24.0:
                    self.lob_progress = 1.0
            else:
                self.x += self.speed * dt
        elif self.is_lobbed:
            self.lob_progress += dt / max(0.001, self.lob_duration)
            p = min(1.0, self.lob_progress)
            self.x = self.start_x + (self.target_x - self.start_x) * p
            linear_y = self.start_y + (self.target_y - self.start_y) * p
            arc = 4.0 * self.apex_h * p * (1.0 - p)
            self.y = linear_y - arc
        else:
            self.x += self.speed * dt
        if self.x > WIDTH + 80 or self.x < -80 or self.y < -80 or self.y > HEIGHT + 80:
            self.alive = False


@dataclass
class Mower:
    row: int
    x: float = MOWER_X
    triggered: bool = False
    spent: bool = False
    cell_h: int = CELL_H
    is_pool: bool = False

    def update(self, dt: float, game: "Game") -> None:
        if not self.triggered:
            return
        self.x += 520 * dt
        for zombie in game.zombies:
            if zombie.row == self.row and not zombie.dead and abs(zombie.x - self.x) < 62:
                game.kill_zombie(zombie, mower=True)
        if self.x > WIDTH + 60:
            self.spent = True


class Game:'''
    if pattern_dataclasses.search(content):
        content = pattern_dataclasses.sub(new_dataclasses, content)
        print("Updated dataclasses.")

    # 5. Update draw_mower
    pattern_draw_mower = re.compile(r'def draw_mower\(surface: pygame\.Surface, mower: "Mower"\) -> None:.*?def ', re.DOTALL)
    new_draw_mower = '''def draw_mower(surface: pygame.Surface, mower: "Mower", is_pool: bool = False, cell_h: int = CELL_H) -> None:
    if mower.spent:
        return
    ground = lane_ground(mower.row, cell_h=cell_h)
    x = mower.x
    y = ground - 24
    try:
        car_surf = pvz_graphics.get_mower_surface((58, 44), is_pool=is_pool)
        if car_surf:
            pygame.draw.ellipse(surface, (29, 45, 33, 90), (x - 22, ground - 3, 48, 14))
            surface.blit(car_surf, car_surf.get_rect(center=(x, y)))
            return
    except Exception:
        pass
    spin = mower.x * 0.12 if mower.triggered else 0.0

    pygame.draw.ellipse(surface, (29, 45, 33, 90), (x - 22, ground - 3, 48, 14))
    body_rect = pygame.Rect(int(x - 20), int(y - 20), 42, 24)
    pygame.draw.rect(surface, (148, 38, 41), body_rect.inflate(4, 4), border_radius=8)
    pygame.draw.rect(surface, (218, 56, 59), body_rect, border_radius=7)
    pygame.draw.rect(surface, (244, 114, 112), (x - 17, y - 18, 36, 6), border_radius=3)

    pygame.draw.line(surface, (91, 102, 107), (x - 18, y - 12), (x - 30, y - 36), 4)
    pygame.draw.line(surface, (48, 54, 57), (x - 33, y - 38), (x - 22, y - 38), 4)

    blade_box = pygame.Rect(int(x + 10), int(y - 14), 18, 20)
    pygame.draw.rect(surface, (168, 178, 182), blade_box, border_radius=4)
    for i in range(4):
        angle = spin + i * math.tau / 4
        bx = blade_box.centerx + math.cos(angle) * 7
        by = blade_box.centery + math.sin(angle) * 7
        pygame.draw.line(surface, (242, 246, 248), blade_box.center, (bx, by), 2)

    for wx, wy in [(x - 12, y + 5), (x + 12, y + 5)]:
        pygame.draw.circle(surface, (36, 41, 45), (wx, wy), 9)
        pygame.draw.circle(surface, (162, 171, 176), (wx, wy), 6)
        pygame.draw.circle(surface, (214, 222, 226), (wx, wy), 2)


def '''
    if pattern_draw_mower.search(content):
        content = pattern_draw_mower.sub(new_draw_mower, content)
        print("Updated draw_mower function.")

    PVZ_FILE.write_text(content, encoding="utf-8")
    print("Base updates written.")

if __name__ == "__main__":
    update_pvz()
