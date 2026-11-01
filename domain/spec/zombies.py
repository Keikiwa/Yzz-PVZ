# -*- coding: utf-8 -*-
"""Zombie specifications.
Declarative design: speeds, health, armor breakdown, water capability, and special mechanics.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ZombieSpec:
    id: str
    name: str
    max_hp: float
    speed: float
    damage: float
    is_water: bool = False
    shield_hp: float = 0.0
    shield_type: Optional[str] = None  # "cone", "bucket", "paper", "door", "football_helmet"
    can_vault: bool = False
    can_dive: bool = False
    can_dig: bool = False
    score: int = 10
    tip: str = ""


ZOMBIES: dict[str, ZombieSpec] = {
    "basic": ZombieSpec(
        id="basic", name="普通僵尸", max_hp=170, speed=18.0, damage=28,
        score=10, tip="普通僵尸：最基础的庭院入侵者，血量较薄。",
    ),
    "flag": ZombieSpec(
        id="flag", name="旗帜领队僵尸", max_hp=190, speed=22.0, damage=28,
        score=15, tip="旗帜僵尸：预示着一大波尸潮的到来，移速稍快。",
    ),
    "cone": ZombieSpec(
        id="cone", name="路障僵尸", max_hp=290, speed=17.0, damage=30,
        shield_hp=120, shield_type="cone", score=25,
        tip="路障僵尸：头戴塑料路障，防御力是普通僵尸的两倍以上。",
    ),
    "bucket": ZombieSpec(
        id="bucket", name="铁桶僵尸", max_hp=470, speed=15.0, damage=34,
        shield_hp=300, shield_type="bucket", score=50,
        tip="铁桶僵尸：坚硬的铁桶使其极具抗击打能力，单体防御极高。",
    ),
    "runner": ZombieSpec(
        id="runner", name="奔跑僵尸", max_hp=155, speed=31.0, damage=24,
        score=20, tip="奔跑僵尸：身形敏捷，突进速度极快。",
    ),
    "pole": ZombieSpec(
        id="pole", name="撑杆僵尸", max_hp=240, speed=32.0, damage=28,
        can_vault=True, score=35,
        tip="撑杆僵尸：手握撑杆，能飞跃第一道植物防线！高坚果除外。",
    ),
    "newspaper": ZombieSpec(
        id="newspaper", name="读报僵尸", max_hp=280, speed=14.0, damage=28,
        shield_hp=100, shield_type="paper", score=30,
        tip="读报僵尸：报纸防御力有限，但一旦被撕碎就会陷入极度狂暴！",
    ),
    "ducky": ZombieSpec(
        id="ducky", name="鸭子救生圈僵尸", max_hp=200, speed=18.0, damage=28,
        is_water=True, score=20,
        tip="鸭子僵尸：套着救生圈在水面游弋，泳池关卡常见入侵者。",
    ),
    "snorkel": ZombieSpec(
        id="snorkel", name="潜水僵尸", max_hp=240, speed=20.0, damage=30,
        is_water=True, can_dive=True, score=40,
        tip="潜水僵尸：潜伏在水下避开普通子弹，仅抛投植物与水下陷阱能命中。",
    ),
    "dolphin": ZombieSpec(
        id="dolphin", name="海豚骑士僵尸", max_hp=320, speed=36.0, damage=30,
        is_water=True, can_vault=True, score=45,
        tip="海豚骑士：在水面疾速冲刺并飞跃防线，威力和撑杆跳类似。",
    ),
    "gargantuar": ZombieSpec(
        id="gargantuar", name="巨人僵尸", max_hp=3000, speed=11.0, damage=1500,
        score=150, tip="巨人僵尸：力拔山河的巨兽，手持巨柱秒杀植物，残血时会投掷小鬼！",
    ),
    "imp": ZombieSpec(
        id="imp", name="小鬼僵尸", max_hp=90, speed=38.0, damage=25,
        score=15, tip="小鬼僵尸：体型小移速飞快，由巨人投掷直插阵地后排。",
    ),
    "balloon": ZombieSpec(
        id="balloon", name="气球僵尸", max_hp=140, speed=17.0, damage=28,
        score=30, tip="气球僵尸：低空悬停飞行，仙人掌或高阶火力能将其击落。",
    ),
    "jackbox": ZombieSpec(
        id="jackbox", name="小丑僵尸", max_hp=240, speed=28.0, damage=30,
        score=40, tip="小丑僵尸：手摇惊魂魔盒，随机自爆引爆周围大范围阵地！",
    ),
    "digger": ZombieSpec(
        id="digger", name="矿工僵尸", max_hp=220, speed=22.0, damage=30,
        can_dig=True, score=45,
        tip="矿工僵尸：遁地钻行直达草坪最左侧，钻出后向右反向包抄！",
    ),
}
