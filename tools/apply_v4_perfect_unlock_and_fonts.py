# -*- coding: utf-8 -*-
import re
from pathlib import Path

pvz_path = Path(r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_ten_levels.py")
code = pvz_path.read_text(encoding="utf-8")

# 1. 替换 text() 函数增加字形净化器
safe_text_func = '''def _clean_text_glyphs(val: str) -> str:
    glyphs = {
        "⭐": "*",
        "🌱": "+",
        "👑": "[冠]",
        "★": "[胜]",
        "▶": ">",
        "Ⅱ": "||",
        "♪": "音",
        "■": "#",
        "□": "-",
    }
    for k, v in glyphs.items():
        if k in val:
            val = val.replace(k, v)
    return "".join(c for c in val if ord(c) < 0x10000)


def text(
    surface: pygame.Surface,
    value: str,
    font: pygame.font.Font,
    color: tuple[int, int, int],
    pos: tuple[float, float],
    anchor: str = "topleft",
    shadow: tuple[int, int, int] | None = None,
) -> pygame.Rect:
    value = _clean_text_glyphs(value)'''

code = re.sub(
    r'def text\(\s*surface:\s*pygame\.Surface,\s*value:\s*str,.*?\)\s*->\s*pygame\.Rect:',
    safe_text_func,
    code,
    flags=re.DOTALL,
)

# 2. 替换 UNLOCK_ORDER
new_unlock_order = '''UNLOCK_ORDER = [
    # 初始基础植物 (第 1 关开局可用)
    "sunflower",
    "peashooter",
    # 白天草坪阶段解锁 (第 1~5 关通关赠送，白天绝不出现蘑菇！)
    "wallnut",
    "snowpea",
    "potatomine",
    "repeater",
    "squash",
    # 黑夜墓地阶段解锁 (第 6~10 关通关赠送，夜间专属蘑菇家族与防御杀器)
    "puffshroom",
    "sunshroom",
    "fumeshroom",
    "spikeweed",
    "hypnoshroom",
    "cherrybomb",
    "chomper",
    "iceshroom",
    "doomshroom",
    "jalapeno",
    # 泳池水面阶段解锁 (第 11~15 关通关赠送，水面两栖战力与强力投手)
    "lilypad",
    "cabbagepult",
    "kernelpult",
    "torchwood",
    "garlic",
    "cattail",
    "twinsunflower",
    "starfruit",
    "threepeater",
    "melonpult",
    "tallnut",
    # 无尽模式终极武器 (第 16 关无尽挑战通关终极战利品)
    "wintermelon",
    "gatlingpea",
]'''

code = re.sub(r'UNLOCK_ORDER = \[.*?\]', new_unlock_order, code, flags=re.DOTALL)

# 3. 替换 LEVEL_REWARDS
new_level_rewards = '''LEVEL_REWARDS = {
    0: {"plants": ["wallnut"], "artifact": None},
    1: {"plants": ["snowpea"], "artifact": None},
    2: {"plants": ["potatomine"], "artifact": None},
    3: {"plants": ["repeater"], "artifact": None},
    4: {
        "plants": ["squash"],
        "artifact": "golden_shovel",
        "artifact_name": "黄金阳光铲",
        "artifact_desc": "神奇黄金铁铲！铲除任何植物时，100% 全额返还种植所消耗的阳光！",
    },
    5: {"plants": ["puffshroom", "sunshroom"], "artifact": None},
    6: {"plants": ["fumeshroom", "spikeweed"], "artifact": None},
    7: {
        "plants": ["hypnoshroom", "cherrybomb"],
        "artifact": "sun_vault",
        "artifact_name": "阳光储蓄罐",
        "artifact_desc": "戴夫特制存钱罐！每个关卡开局额外赠送 +100 点初始阳光储备！",
    },
    8: {"plants": ["chomper", "iceshroom"], "artifact": None},
    9: {
        "plants": ["doomshroom", "jalapeno"],
        "artifact": "rapid_seeds",
        "artifact_name": "园艺快手手套",
        "artifact_desc": "熟练园丁的特制手套！全植物种植冷却恢复速度提升 30%！",
    },
    10: {"plants": ["lilypad", "cabbagepult"], "artifact": None},
    11: {
        "plants": ["kernelpult", "torchwood"],
        "artifact": "golden_mower",
        "artifact_name": "镀金清扫车",
        "artifact_desc": "华丽镀金清扫车！当割草机或泳池清扫机被触发碾压时，额外爆落 200 点阳光！",
    },
    12: {"plants": ["garlic", "cattail", "twinsunflower"], "artifact": None},
    13: {"plants": ["starfruit", "threepeater"], "artifact": None},
    14: {
        "plants": ["melonpult", "tallnut"],
        "artifact": "master_belt",
        "artifact_name": "大师战术腰带",
        "artifact_desc": "顶级战术大师腰带！出战卡槽容量永久扩充至 9 格！",
    },
    15: {"plants": ["wintermelon", "gatlingpea"], "artifact": None},
}'''

code = re.sub(r'LEVEL_REWARDS = \{.*?\n\}', new_level_rewards, code, flags=re.DOTALL)

# 4. 替换 available_plants
new_available_plants = '''    def available_plants(self) -> list[str]:
        # 植物逐步赠送解锁系统：第一关仅基础植物，随后每通关一关解锁赠送新植物
        unlocked = list(DEFAULT_INITIAL_PLANTS)
        save = load_save()
        completed = set(save.get("completed", []))
        for c_idx in sorted(completed):
            rewards = LEVEL_REWARDS.get(c_idx, {}).get("plants", [])
            for p in rewards:
                if p in UNLOCK_ORDER and p not in unlocked:
                    unlocked.append(p)

        # 严格关卡进度封顶（根治前几关提前获得小喷菇/阳光菇）：
        # 如果是在主线关卡（0 <= level_index < 15）
        # 则绝不允许提前带入超出当前关卡正常推进进度的植物！
        # 当前关卡允许的最大植物集合 = 初始植物 + 截止到当前关卡之前的所有关卡（0 到 level_index-1）的通关奖励
        if self.level_index < 15:
            max_allowed = set(DEFAULT_INITIAL_PLANTS)
            for prev_idx in range(self.level_index):
                for p in LEVEL_REWARDS.get(prev_idx, {}).get("plants", []):
                    max_allowed.add(p)
            unlocked = [p for p in unlocked if p in max_allowed]

        # 泳池关卡（11关及以后，即 level_index >= 10）必须自动保证拥有睡莲作为水生载体
        if getattr(self, "is_pool", False) and "lilypad" not in unlocked:
            unlocked.append("lilypad")

        return [p for p in UNLOCK_ORDER if p in unlocked]'''

code = re.sub(
    r'    def available_plants\(self\) -> list\[str\]:.*?(?=    def begin_loop)',
    new_available_plants + '\n\n',
    code,
    flags=re.DOTALL,
)

# 5. 替换所有特殊字符
code = code.replace('★ 已通关', '[已通关]')
code = code.replace(
    '👑 第 16 关 · 水陆无尽大挑战 (ENDLESS POOL SURVIVAL)',
    '【无尽挑战】第 16 关 · 水陆无尽大挑战 (ENDLESS POOL)',
)
code = code.replace(
    '"Ⅱ" if self.overlay != "paused" else "▶"',
    '"||" if self.overlay != "paused" else ">"',
)
code = code.replace(
    'self._small_control(self.audio_rect, "♪", "声音"',
    'self._small_control(self.audio_rect, "音", "音效"',
)
code = code.replace(
    'f"⭐ 荣获通关神器：【{art_name}】 ⭐"',
    'f"【荣获通关神器】{art_name}"',
)
code = code.replace(
    'f"🌱 解锁全新植物：{p_names}"',
    'f"【解锁全新植物】{p_names}"',
)

# 6. 优化选卡界面布局 8列 x 4行
catalog_grid_old = '''        # 23 Plants Catalog Grid (6 cols x 4 rows)
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
            row = idx // 6'''

catalog_grid_new = '''        # 30 Plants Catalog Grid (8 cols x 4 rows)
        unlocked = set(self.available_plants())
        cw = 98
        ch = 72
        gap_x = 12
        gap_y = 6
        gx0 = cat_rect.x + (cat_rect.width - (8 * cw + 7 * gap_x)) // 2
        gy0 = cat_rect.y + 60

        self.catalog_rects = {}
        hovered_plant = None
        for idx, name in enumerate(UNLOCK_ORDER):
            col = idx % 8
            row = idx // 8'''

code = code.replace(catalog_grid_old, catalog_grid_new)

pvz_path.write_text(code, encoding="utf-8")
print("Updated pvz_ten_levels.py successfully!")
