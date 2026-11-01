# -*- coding: utf-8 -*-
"""Level specifications.
16 levels covering Day, Dusk, Night, Pool Day, Pool Night, and Endless Survival.
"""

from dataclasses import dataclass
from typing import Optional
from domain.spec.field_layout import FieldLayout, LAND_LAYOUT, POOL_LAYOUT


@dataclass(frozen=True)
class LevelSpec:
    id: int
    name: str
    subtitle: str
    initial_sun: int
    zombie_count: int
    zombie_weights: dict[str, float]
    theme: str
    is_pool: bool = False
    is_endless: bool = False

    @property
    def layout(self) -> FieldLayout:
        return POOL_LAYOUT if self.is_pool else LAND_LAYOUT


LEVELS: list[LevelSpec] = [
    LevelSpec(
        id=0, name="草坪初醒", subtitle="第一波僵尸正在靠近",
        initial_sun=150, zombie_count=7,
        zombie_weights={"basic": 1.0},
        theme="day",
    ),
    LevelSpec(
        id=1, name="向阳生长", subtitle="阳光越多，防线越稳",
        initial_sun=150, zombie_count=9,
        zombie_weights={"basic": 0.8, "cone": 0.2},
        theme="day",
    ),
    LevelSpec(
        id=2, name="坚果防线", subtitle="把危险挡在门外",
        initial_sun=150, zombie_count=11,
        zombie_weights={"basic": 0.65, "cone": 0.35},
        theme="day",
    ),
    LevelSpec(
        id=3, name="撑杆越障", subtitle="小心飞跃防线的撑杆跳手",
        initial_sun=175, zombie_count=13,
        zombie_weights={"basic": 0.50, "cone": 0.25, "pole": 0.25},
        theme="dusk",
    ),
    LevelSpec(
        id=4, name="铁桶警告", subtitle="硬壳僵尸闯进草坪",
        initial_sun=175, zombie_count=15,
        zombie_weights={"basic": 0.42, "cone": 0.28, "bucket": 0.16, "pole": 0.14},
        theme="dusk",
    ),
    LevelSpec(
        id=5, name="读报愤怒", subtitle="撕碎报纸的瞬间极其危险",
        initial_sun=200, zombie_count=18,
        zombie_weights={"basic": 0.35, "cone": 0.25, "bucket": 0.15, "pole": 0.10, "newspaper": 0.15},
        theme="dusk",
    ),
    LevelSpec(
        id=6, name="旗帜浪潮", subtitle="一大波混合僵尸即将到来",
        initial_sun=200, zombie_count=22,
        zombie_weights={"basic": 0.32, "cone": 0.24, "bucket": 0.18, "runner": 0.08, "pole": 0.10, "newspaper": 0.08},
        theme="day",
    ),
    LevelSpec(
        id=7, name="月夜花园", subtitle="月光下也不能松懈",
        initial_sun=225, zombie_count=26,
        zombie_weights={"basic": 0.28, "cone": 0.22, "bucket": 0.18, "runner": 0.12, "pole": 0.10, "newspaper": 0.10},
        theme="night",
    ),
    LevelSpec(
        id=8, name="极速进攻", subtitle="脚步声比往常更快",
        initial_sun=225, zombie_count=28,
        zombie_weights={"basic": 0.24, "cone": 0.20, "bucket": 0.20, "runner": 0.16, "pole": 0.10, "newspaper": 0.10},
        theme="night",
    ),
    LevelSpec(
        id=9, name="黑夜决战", subtitle="守住草坪最后一条防线",
        initial_sun=400, zombie_count=32,
        zombie_weights={"basic": 0.26, "cone": 0.22, "bucket": 0.18, "runner": 0.12, "pole": 0.11, "newspaper": 0.11},
        theme="night",
    ),
    LevelSpec(
        id=10, name="阳光碧波", subtitle="水面初遇！鸭子救生圈僵尸登场",
        initial_sun=250, zombie_count=18,
        zombie_weights={"basic": 0.28, "cone": 0.22, "bucket": 0.15, "ducky": 0.35},
        theme="pool_day", is_pool=True,
    ),
    LevelSpec(
        id=11, name="潜水突袭", subtitle="直射无效！用投手植物重创潜水怪",
        initial_sun=275, zombie_count=24,
        zombie_weights={"basic": 0.20, "cone": 0.20, "bucket": 0.15, "ducky": 0.25, "snorkel": 0.20},
        theme="pool_day", is_pool=True,
    ),
    LevelSpec(
        id=12, name="海豚跃浪", subtitle="飞跃防线！大蒜分流与猫尾草迎敌",
        initial_sun=300, zombie_count=28,
        zombie_weights={"basic": 0.18, "cone": 0.18, "bucket": 0.14, "ducky": 0.20, "snorkel": 0.15, "dolphin": 0.15},
        theme="pool_day", is_pool=True,
    ),
    LevelSpec(
        id=13, name="浓雾夜泳", subtitle="迷雾笼罩！暗夜水陆混合狂攻",
        initial_sun=350, zombie_count=34,
        zombie_weights={"basic": 0.15, "cone": 0.18, "bucket": 0.17, "runner": 0.10, "ducky": 0.15, "snorkel": 0.12, "dolphin": 0.13},
        theme="pool_night", is_pool=True,
    ),
    LevelSpec(
        id=14, name="水陆决战", subtitle="全兵种防守演练！守住全场",
        initial_sun=600, zombie_count=42,
        zombie_weights={"basic": 0.14, "cone": 0.16, "bucket": 0.16, "runner": 0.10, "pole": 0.08, "newspaper": 0.08, "ducky": 0.10, "snorkel": 0.09, "dolphin": 0.09},
        theme="pool_night", is_pool=True,
    ),
    LevelSpec(
        id=15, name="水陆无尽", subtitle="极限泳池生存，水陆两栖永无止境！",
        initial_sun=500, zombie_count=50,
        zombie_weights={"basic": 0.15, "cone": 0.15, "bucket": 0.15, "runner": 0.10, "pole": 0.08, "newspaper": 0.08, "ducky": 0.10, "snorkel": 0.09, "dolphin": 0.10},
        theme="pool_day", is_pool=True, is_endless=True,
    ),
]
