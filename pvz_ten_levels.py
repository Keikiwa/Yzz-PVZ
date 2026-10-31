#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A self-contained ten-level Plants vs. Zombies style pygame prototype with rich enhancements."""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from array import array
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import pygame

import pvz_graphics


WIDTH = 1200
HEIGHT = 760
FPS = 60

GRID_X = 70
GRID_Y = 124
COLS = 9
ROWS = 5
CELL_W = 111
CELL_H = 116
GRID_RIGHT = GRID_X + COLS * CELL_W
GRID_BOTTOM = GRID_Y + ROWS * CELL_H
HUD_H = 100
MOWER_X = 34
FIRST_WAVE_DELAY = 15.0

C_BG = (22, 42, 34)
C_INK = (39, 42, 35)
C_CREAM = (255, 244, 207)
C_GOLD = (255, 202, 72)
C_SUN = (255, 224, 82)
C_GREEN = (97, 179, 72)
C_DARK_GREEN = (38, 91, 49)
C_RED = (219, 70, 66)
C_BLUE = (104, 205, 230)
C_BROWN = (139, 90, 51)
C_PURPLE = (142, 68, 173)

SAVE_FILE = Path(__file__).parent / "pvz_save.json"

# 每帧重复绘制的内容集中缓存，避免反复分配 Surface 和旋转/渲染文本。
_TEXT_CACHE: dict[tuple[int, str, tuple[int, int, int]], pygame.Surface] = {}
_LEAF_CACHE: dict[tuple[float, float, int, tuple[int, int, int]], pygame.Surface] = {}
_SUN_GLOW_CACHE: dict[int, pygame.Surface] = {}
_GLOW_CACHE: dict[tuple[int, tuple[int, int, int]], pygame.Surface] = {}
_PARTICLE_CACHE: dict[tuple[tuple[int, int, int], int], pygame.Surface] = {}


def load_save() -> dict:
    try:
        if SAVE_FILE.exists():
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"completed": [], "artifacts": [], "endless_best": 0}


def record_win(level_idx: int, endless_wave: int = 0) -> dict:
    data = load_save()
    if "completed" not in data:
        data["completed"] = []
    if "artifacts" not in data:
        data["artifacts"] = []

    first_time = level_idx not in data["completed"]
    if first_time:
        data["completed"].append(level_idx)

    reward_info = LEVEL_REWARDS.get(level_idx, {})
    new_art = reward_info.get("artifact")
    if new_art and new_art not in data["artifacts"]:
        data["artifacts"].append(new_art)

    if endless_wave > data.get("endless_best", 0):
        data["endless_best"] = endless_wave

    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return {"first_time": first_time, "reward": reward_info}


PLANTS = {
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
    "tallnut": {
        "name": "高坚果", "cost": 125, "cooldown": 20.0, "hp": 8000,
    },
    "gatlingpea": {
        "name": "机枪射手", "cost": 250, "cooldown": 15.0, "hp": 300,
    },
    "hypnoshroom": {
        "name": "魅惑菇", "cost": 75, "cooldown": 15.0, "hp": 300,
    },
    "fumeshroom": {
        "name": "大喷菇", "cost": 75, "cooldown": 7.5, "hp": 300,
    },
    "doomshroom": {
        "name": "毁灭菇", "cost": 125, "cooldown": 25.0, "hp": 300,
    },
    "twinsunflower": {
        "name": "双子向日葵", "cost": 150, "cooldown": 15.0, "hp": 300,
    },
    "starfruit": {
        "name": "杨桃", "cost": 125, "cooldown": 7.5, "hp": 300,
    },
    "cobcannon": {
        "name": "玉米加农炮", "cost": 500, "cooldown": 30.0, "hp": 1200,
    },
    "magicshroom": {
        "name": "魔术菇", "cost": 175, "cooldown": 10.0, "hp": 300,
    },
    "agave": {
        "name": "龙舌兰", "cost": 150, "cooldown": 10.0, "hp": 600,
    },
    "laserbean": {
        "name": "激光豆", "cost": 200, "cooldown": 10.0, "hp": 300,
    },
}

UNLOCK_ORDER = [
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
    # 传奇新植物与终极武器
    "agave",
    "magicshroom",
    "laserbean",
    "wintermelon",
    "gatlingpea",
    "cobcannon",
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
    "tallnut": "高坚果：拥有 8000 超高血量的重型钢铁壁垒！撑杆跳与海豚僵尸绝对无法跳越！",
    "gatlingpea": "机枪射手：头戴钢盔的终极射手！一次性扫射 4 颗豌豆，配合火炬树桩火力毁天灭地！",
    "hypnoshroom": "魅惑菇：让吃下它的僵尸彻底倒戈！掉头反向冲锋并为你攻击其他敌方僵尸！",
    "fumeshroom": "大喷菇：喷射大范围强力紫色穿透孢子气雾，一次性贯穿打击整行内所有僵尸！",
    "doomshroom": "毁灭菇：末日级超级核弹！产生惊天动地的毁灭蘑菇云，瞬秒 5x5 格内全部僵尸！",
    "twinsunflower": "双子向日葵：双头并立双倍快乐！每次稳定产出 50 点巨量阳光，经济腾飞核心！",
    "starfruit": "杨桃：全方位无死角弹幕射手！同时向 5 个方向发射高速旋转飞星，密不透风！",
    "cobcannon": "玉米加农炮：PVZ 终极大杀器！装填高爆玉米核弹，轰炸全屏 3x3 范围造成 1800 毁天灭地巨额伤害！",
    "magicshroom": "魔术菇：挥舞魔杖连发旋转魔术扑克牌！命中时 25% 几率奇迹魅惑变节僵尸或掉落暴富阳光！",
    "agave": "龙舌兰：近战刺客与剑气宗师！拔出青翠多肉巨剑蓄力二连斩；对残血僵尸直接施展苍翠剑浪斩杀！",
    "laserbean": "激光豆：未来科幻双目射手！双眼射出贯通全屏整行的超强蓝色激光束，无视护甲穿透灼烧！",
}

ZOMBIES = {
    "basic": {"name": "普通僵尸", "hp": 170, "speed": 18.0, "damage": 28},
    "flag": {"name": "旗帜领队僵尸", "hp": 190, "speed": 22.0, "damage": 28},
    "cone": {"name": "路障僵尸", "hp": 290, "speed": 17.0, "damage": 30},
    "bucket": {"name": "铁桶僵尸", "hp": 470, "speed": 15.0, "damage": 34},
    "runner": {"name": "奔跑僵尸", "hp": 155, "speed": 31.0, "damage": 24},
    "pole": {"name": "撑杆僵尸", "hp": 240, "speed": 32.0, "damage": 28},
    "newspaper": {"name": "读报僵尸", "hp": 280, "speed": 14.0, "damage": 28},
    "ducky": {"name": "鸭子救生圈僵尸", "hp": 200, "speed": 18.0, "damage": 28, "water": True},
    "snorkel": {"name": "潜水僵尸", "hp": 240, "speed": 20.0, "damage": 30, "water": True},
    "dolphin": {"name": "海豚骑士僵尸", "hp": 320, "speed": 36.0, "damage": 30, "water": True},
    "gargantuar": {"name": "巨人僵尸", "hp": 3000, "speed": 11.0, "damage": 1500},
    "imp": {"name": "小鬼僵尸", "hp": 90, "speed": 38.0, "damage": 25},
    "balloon": {"name": "气球僵尸", "hp": 140, "speed": 17.0, "damage": 28},
    "jackbox": {"name": "小丑僵尸", "hp": 240, "speed": 28.0, "damage": 30},
    "digger": {"name": "矿工僵尸", "hp": 220, "speed": 22.0, "damage": 30},
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



LEVEL_REWARDS = {
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
    13: {"plants": ["starfruit", "threepeater", "agave"], "artifact": None},
    14: {
        "plants": ["melonpult", "tallnut", "magicshroom", "laserbean"],
        "artifact": "master_belt",
        "artifact_name": "大师战术腰带",
        "artifact_desc": "顶级战术大师腰带！出战卡槽容量永久扩充至 10 格！",
    },
    15: {"plants": ["wintermelon", "gatlingpea", "cobcannon"], "artifact": None},
}

DEFAULT_INITIAL_PLANTS = ["sunflower", "peashooter"]

def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def lerp(a: float, b: float, amount: float) -> float:
    return a + (b - a) * amount


def lerp_color(a: tuple[int, ...], b: tuple[int, ...], amount: float) -> tuple[int, ...]:
    return tuple(int(lerp(x, y, amount)) for x, y in zip(a, b))


def cell_center(col: int, row: int, cell_h: int = CELL_H, is_pool: bool = False) -> tuple[int, int]:
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
    return GRID_Y + (row + 1) * cell_h - (13 if cell_h >= 110 else 8)


class FontBook:
    def __init__(self) -> None:
        self.cache: dict[tuple[int, bool], pygame.font.Font] = {}
        self.regular_path = Path(r"C:\Windows\Fonts\msyh.ttc")
        self.bold_path = Path(r"C:\Windows\Fonts\msyhbd.ttc")

    def get(self, size: int, bold: bool = False) -> pygame.font.Font:
        key = (size, bold)
        if key not in self.cache:
            path = self.bold_path if bold and self.bold_path.exists() else self.regular_path
            if path.exists():
                self.cache[key] = pygame.font.Font(str(path), size)
            else:
                self.cache[key] = pygame.font.SysFont("microsoftyahei,simhei,arial", size, bold=bold)
        return self.cache[key]


class AudioBank:
    """Official PVZ soundtrack player and synthesized sound effect bank."""

    SAMPLE_RATE = 44100

    def __init__(self, base_dir: Path | None = None) -> None:
        self._enabled = True
        self.available = False
        self.base_dir = base_dir or Path(__file__).resolve().parent
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.last_played: dict[str, float] = {}
        self.current_music: str | None = None
        self.music_volume = 0.55
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=self.SAMPLE_RATE, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(16)
            self.sounds = {
                "collect": self._tone(760, 1120, 0.16, 0.15, 0.0),
                "plant": self._tone(190, 290, 0.18, 0.10, 0.05),
                "click": self._tone(430, 390, 0.08, 0.045, 0.0),
                "explode": self._tone(95, 38, 0.70, 0.34, 0.45),
                "mower": self._tone(72, 118, 0.45, 0.32, 0.18),
                "win": self._tone(420, 880, 0.44, 0.26, 0.0),
                "lose": self._tone(220, 82, 0.55, 0.32, 0.06),
                "chomp": self._tone(150, 75, 0.16, 0.30, 0.25),
                "squash": self._tone(85, 38, 0.35, 0.45, 0.30),
                "vault": self._tone(280, 560, 0.24, 0.25, 0.08),
                "groan": self._tone(110, 160, 0.40, 0.30, 0.35),
                "splash": self._tone(320, 160, 0.28, 0.28, 0.35),
                "butter": self._tone(450, 220, 0.20, 0.35, 0.20),
            }
            self.available = True
        except (pygame.error, ValueError):
            self.available = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, val: bool) -> None:
        self._enabled = bool(val)
        if not self.available:
            return
        if not self._enabled:
            try:
                pygame.mixer.music.pause()
            except Exception:
                pass
        else:
            try:
                if self.current_music:
                    pygame.mixer.music.unpause()
                    if not pygame.mixer.music.get_busy():
                        self.play_music(self.current_music)
            except Exception:
                pass

    def _tone(
        self,
        start_frequency: float,
        end_frequency: float,
        duration: float,
        volume: float,
        noise_amount: float,
    ) -> pygame.mixer.Sound:
        sample_count = max(1, int(self.SAMPLE_RATE * duration))
        rng = random.Random(int(start_frequency * 17 + end_frequency * 3))
        data = array("h")
        phase = 0.0
        for i in range(sample_count):
            progress = i / sample_count
            frequency = lerp(start_frequency, end_frequency, progress)
            phase += math.tau * frequency / self.SAMPLE_RATE
            attack = min(1.0, i / max(1, self.SAMPLE_RATE * 0.012))
            release = max(0.0, 1.0 - progress) ** 0.7
            envelope = attack * release
            wave = math.sin(phase) * 0.75 + math.sin(phase * 2.01) * 0.18
            wave += rng.uniform(-1.0, 1.0) * noise_amount
            value = int(clamp(wave * volume * envelope, -1.0, 1.0) * 32767)
            data.append(value)
            data.append(value)
        return pygame.mixer.Sound(buffer=data.tobytes())

    def play(self, name: str, cooldown: float = 0.0) -> None:
        if not self._enabled or not self.available or name not in self.sounds:
            return
        now = pygame.time.get_ticks() / 1000.0
        if cooldown and now - self.last_played.get(name, -999.0) < cooldown:
            return
        self.last_played[name] = now
        self.sounds[name].play()

    def play_music(self, track_name: str, loop: bool = True) -> None:
        if not self.available:
            return
        target_file = self.base_dir / f"music_{track_name}.mp3"
        if not target_file.exists():
            return
        if self.current_music == track_name and pygame.mixer.music.get_busy():
            return
        self.current_music = track_name
        if not self._enabled:
            return
        try:
            pygame.mixer.music.load(str(target_file))
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception:
            pass

    def pause_music(self) -> None:
        if not self.available:
            return
        try:
            pygame.mixer.music.pause()
        except Exception:
            pass

    def unpause_music(self) -> None:
        if not self.available or not self._enabled:
            return
        try:
            pygame.mixer.music.unpause()
            if not pygame.mixer.music.get_busy() and self.current_music:
                self.play_music(self.current_music)
        except Exception:
            pass

    def stop_music(self) -> None:
        if not self.available:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self.current_music = None


def _clean_text_glyphs(val: str) -> str:
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
    value = _clean_text_glyphs(value)
    key = (id(font), value, color)
    image = _TEXT_CACHE.get(key)
    if image is None:
        image = font.render(value, True, color)
        _TEXT_CACHE[key] = image
    rect = image.get_rect()
    setattr(rect, anchor, (round(pos[0]), round(pos[1])))
    if shadow is not None:
        shade_key = (id(font), value, shadow)
        shade = _TEXT_CACHE.get(shade_key)
        if shade is None:
            shade = font.render(value, True, shadow)
            _TEXT_CACHE[shade_key] = shade
        shadow_rect = shade.get_rect()
        setattr(shadow_rect, anchor, (round(pos[0] + 2), round(pos[1] + 3)))
        surface.blit(shade, shadow_rect)
    surface.blit(image, rect)
    return rect


def panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    fill: tuple[int, int, int],
    outline: tuple[int, int, int] = C_INK,
    radius: int = 12,
    width: int = 3,
    shadow: bool = True,
) -> None:
    if shadow:
        shadow_rect = rect.move(3, 4)
        pygame.draw.rect(surface, (25, 34, 27, 115), shadow_rect, border_radius=radius)
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    pygame.draw.rect(surface, outline, rect, width=width, border_radius=radius)


def draw_sun_shape(
    surface: pygame.Surface,
    center: tuple[float, float],
    radius: float,
    spin: float = 0.0,
    glow: bool = True,
) -> None:
    try:
        sun_surf = pvz_graphics.get_sun_frame(spin if spin != 0.0 else pygame.time.get_ticks() / 1000.0, radius)
        if sun_surf:
            surface.blit(sun_surf, sun_surf.get_rect(center=center))
            return
    except Exception:
        pass
    cx, cy = center
    if glow:
        dims = int(radius * 4)
        glow_surface = _SUN_GLOW_CACHE.get(dims)
        if glow_surface is None:
            glow_surface = pygame.Surface((dims, dims), pygame.SRCALPHA)
            for i in range(8, 0, -1):
                alpha = int(7 + i * 2.5)
                pygame.draw.circle(
                    glow_surface,
                    (255, 221, 72, alpha),
                    (dims // 2, dims // 2),
                    radius * (1.0 + i * 0.12),
                )
            _SUN_GLOW_CACHE[dims] = glow_surface
        surface.blit(
            glow_surface,
            (cx - glow_surface.get_width() / 2, cy - glow_surface.get_height() / 2),
        )
    for i in range(12):
        angle = spin + i * math.tau / 12
        inner = radius * 1.12
        outer = radius * (1.35 if i % 2 == 0 else 1.25)
        points = [
            (cx + math.cos(angle - 0.10) * inner, cy + math.sin(angle - 0.10) * inner),
            (cx + math.cos(angle) * outer, cy + math.sin(angle) * outer),
            (cx + math.cos(angle + 0.10) * inner, cy + math.sin(angle + 0.10) * inner),
        ]
        pygame.draw.polygon(surface, (255, 192, 36), points)
    pygame.draw.circle(surface, (255, 173, 25), (cx, cy), radius * 1.12)
    pygame.draw.circle(surface, C_SUN, (cx, cy), radius)
    pygame.draw.circle(surface, (255, 248, 170), (cx - radius * 0.28, cy - radius * 0.30), radius * 0.40)
    pygame.draw.circle(surface, (234, 146, 18), (cx, cy), radius * 1.20, max(2, int(radius * 0.10)))


def draw_leaf(
    surface: pygame.Surface,
    center: tuple[float, float],
    width: float,
    height: float,
    angle: float,
    color: tuple[int, int, int] = (80, 164, 67),
) -> None:
    key = (round(width, 2), round(height, 2), angle, color)
    leaf = _LEAF_CACHE.get(key)
    if leaf is None:
        leaf = pygame.Surface((max(4, int(width * 2)), max(4, int(height * 2))), pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, int(width * 2), int(height * 2))
        pygame.draw.ellipse(leaf, (33, 91, 44), rect)
        pygame.draw.ellipse(leaf, color, rect.inflate(-4, -4))
        pygame.draw.line(leaf, (37, 94, 45), (width * 0.25, height * 1.2), (width * 1.8, height * 0.85), 2)
        leaf = pygame.transform.rotate(leaf, angle)
        _LEAF_CACHE[key] = leaf
    surface.blit(leaf, leaf.get_rect(center=center))


def draw_face(
    surface: pygame.Surface,
    cx: float,
    cy: float,
    scale: float,
    angry: bool = False,
    sleepy: bool = False,
) -> None:
    eye_dx = 7 * scale
    eye_y = cy - 2 * scale
    for direction in (-1, 1):
        ex = cx + direction * eye_dx
        pygame.draw.ellipse(
            surface,
            (246, 247, 214),
            (ex - 3.3 * scale, eye_y - 4.5 * scale, 6.6 * scale, 9 * scale),
        )
        if sleepy:
            pygame.draw.line(
                surface, C_INK,
                (ex - 3 * scale, eye_y),
                (ex + 3 * scale, eye_y),
                max(1, int(1.5 * scale)),
            )
        else:
            pygame.draw.circle(surface, (28, 38, 30), (ex, eye_y + 0.8 * scale), 1.6 * scale)
    if angry:
        pygame.draw.line(surface, C_INK, (cx - 12 * scale, cy - 9 * scale), (cx - 4 * scale, cy - 6 * scale), 2)
        pygame.draw.line(surface, C_INK, (cx + 12 * scale, cy - 9 * scale), (cx + 4 * scale, cy - 6 * scale), 2)
    pygame.draw.arc(
        surface,
        C_INK,
        (cx - 7 * scale, cy + 3 * scale, 14 * scale, 9 * scale),
        0.15 if not angry else math.pi + 0.2,
        math.pi - 0.15 if not angry else math.tau - 0.2,
        max(1, int(1.6 * scale)),
    )


def draw_plant(
    surface: pygame.Surface,
    plant_type: str,
    center: tuple[float, float],
    scale: float,
    time_value: float,
    hp_ratio: float = 1.0,
    age: float = 10.0,
    plant: "Plant" | None = None,
) -> None:
    try:
        if pvz_graphics.render_plant_sprite(surface, plant_type, center, scale, time_value, hp_ratio, age, plant):
            return
    except Exception:
        pass
    cx, cy = center
    sway = math.sin(time_value * 2.0 + cx * 0.02) * 2.2 * scale
    shadow_width = 68 * scale
    pygame.draw.ellipse(
        surface,
        (30, 65, 39, 90),
        (cx - shadow_width / 2, cy + 28 * scale, shadow_width, 18 * scale),
    )

    if plant_type in {"sunflower", "peashooter", "snowpea", "repeater"}:
        pygame.draw.line(
            surface, (46, 117, 48),
            (cx + sway * 0.2, cy + 28 * scale),
            (cx + sway, cy - 7 * scale),
            max(2, int(7 * scale)),
        )
        draw_leaf(surface, (cx - 15 * scale, cy + 15 * scale), 19 * scale, 11 * scale, 28)
        draw_leaf(surface, (cx + 16 * scale, cy + 20 * scale), 18 * scale, 10 * scale, -30)

    if plant_type == "sunflower":
        head = (cx + sway, cy - 25 * scale)
        for i in range(12):
            angle = time_value * 0.35 + i * math.tau / 12
            px = head[0] + math.cos(angle) * 29 * scale
            py = head[1] + math.sin(angle) * 27 * scale
            pygame.draw.circle(surface, (57, 94, 40), (px, py), 13 * scale)
            pygame.draw.circle(surface, (255, 184, 43), (px, py), 11 * scale)
            pygame.draw.circle(surface, (255, 216, 73), (px - 2 * scale, py - 2 * scale), 7 * scale)
        pygame.draw.circle(surface, (94, 61, 32), head, 23 * scale)
        pygame.draw.circle(surface, (133, 82, 36), head, 20 * scale)
        for i in range(10):
            angle = i * math.tau / 10
            pygame.draw.circle(
                surface, (90, 56, 30),
                (head[0] + math.cos(angle) * 13 * scale, head[1] + math.sin(angle) * 13 * scale),
                2.1 * scale,
            )
        draw_face(surface, head[0], head[1], scale)
        return

    if plant_type in {"peashooter", "snowpea", "repeater"}:
        is_snow = plant_type == "snowpea"
        body = (91, 198, 75) if not is_snow else (92, 201, 230)
        body_dark = (43, 126, 49) if not is_snow else (47, 135, 177)
        head = (cx + sway - 2 * scale, cy - 27 * scale)
        pygame.draw.circle(surface, body_dark, (head[0], head[1] + 2 * scale), 28 * scale)
        pygame.draw.circle(surface, body, head, 26 * scale)
        pygame.draw.circle(surface, (158, 224, 105), (head[0] - 8 * scale, head[1] - 9 * scale), 9 * scale)
        snout_y = head[1] - 2 * scale
        pygame.draw.ellipse(
            surface, body_dark,
            (head[0] + 13 * scale, snout_y - 11 * scale, 29 * scale, 22 * scale),
        )
        pygame.draw.ellipse(
            surface, body,
            (head[0] + 14 * scale, snout_y - 10 * scale, 27 * scale, 20 * scale),
        )
        pygame.draw.ellipse(
            surface, (33, 74, 38),
            (head[0] + 37 * scale, snout_y - 7 * scale, 8 * scale, 14 * scale),
        )
        if plant_type == "repeater":
            pygame.draw.ellipse(
                surface, body_dark,
                (head[0] + 8 * scale, snout_y + 8 * scale, 25 * scale, 17 * scale),
            )
            pygame.draw.ellipse(
                surface, body,
                (head[0] + 10 * scale, snout_y + 9 * scale, 23 * scale, 15 * scale),
            )
        pygame.draw.circle(surface, (244, 247, 215), (head[0] - 3 * scale, head[1] - 4 * scale), 6 * scale)
        pygame.draw.circle(surface, C_INK, (head[0] + 1 * scale, head[1] - 4 * scale), 2.3 * scale)
        if is_snow:
            for i in range(6):
                angle = i * math.tau / 6 + time_value
                x1 = head[0] + math.cos(angle) * 16 * scale
                y1 = head[1] + math.sin(angle) * 16 * scale
                x2 = head[0] + math.cos(angle) * 22 * scale
                y2 = head[1] + math.sin(angle) * 22 * scale
                pygame.draw.line(surface, (225, 252, 255), (x1, y1), (x2, y2), max(1, int(2 * scale)))
        return

    if plant_type == "wallnut":
        shell = (157, 99, 52) if hp_ratio > 0.45 else (132, 83, 47)
        pygame.draw.ellipse(
            surface, (81, 54, 35),
            (cx - 35 * scale, cy - 42 * scale, 70 * scale, 86 * scale),
        )
        pygame.draw.ellipse(
            surface, shell,
            (cx - 32 * scale, cy - 40 * scale, 64 * scale, 80 * scale),
        )
        pygame.draw.ellipse(
            surface, (191, 129, 72),
            (cx - 21 * scale, cy - 31 * scale, 27 * scale, 43 * scale),
        )
        draw_face(surface, cx, cy - 7 * scale, scale)
        if hp_ratio < 0.66:
            pygame.draw.lines(
                surface, (83, 56, 37), False,
                [(cx + 19 * scale, cy - 35 * scale), (cx + 11 * scale, cy - 16 * scale),
                 (cx + 19 * scale, cy - 2 * scale)],
                max(1, int(2 * scale)),
            )
        if hp_ratio < 0.33:
            pygame.draw.lines(
                surface, (83, 56, 37), False,
                [(cx - 27 * scale, cy + 6 * scale), (cx - 13 * scale, cy + 18 * scale),
                 (cx - 19 * scale, cy + 32 * scale)],
                max(1, int(2 * scale)),
            )
        return

    if plant_type == "squash":
        jump_offset = 0.0
        if plant and plant.squash_state == "jump":
            prog = clamp(plant.squash_timer, 0.0, 1.0)
            jump_offset = -math.sin(prog * math.pi) * 85 * scale
        sy = cy + jump_offset
        body_rect = pygame.Rect(int(cx - 30 * scale), int(sy - 38 * scale), int(60 * scale), int(76 * scale))
        pygame.draw.ellipse(surface, (34, 75, 42), body_rect.inflate(6 * scale, 6 * scale))
        pygame.draw.ellipse(surface, (88, 172, 76), body_rect)
        pygame.draw.arc(surface, (45, 102, 48), (cx - 24 * scale, sy - 34 * scale, 48 * scale, 30 * scale), 0.2, math.pi - 0.2, max(2, int(3 * scale)))
        for dx in (-10, 10):
            ex = cx + dx * scale
            ey = sy - 10 * scale
            pygame.draw.polygon(surface, (250, 252, 230), [(ex - 6 * scale, ey - 7 * scale), (ex + 6 * scale, ey - 7 * scale), (ex, ey + 6 * scale)])
            pygame.draw.circle(surface, C_INK, (ex + 1 * scale, ey - 1 * scale), 2.2 * scale)
        pygame.draw.arc(surface, C_INK, (cx - 14 * scale, sy + 6 * scale, 28 * scale, 18 * scale), 0.3, math.pi - 0.3, max(2, int(2.5 * scale)))
        pygame.draw.line(surface, (42, 95, 45), (cx, sy - 38 * scale), (cx - 6 * scale, sy - 52 * scale), max(2, int(4 * scale)))
        draw_leaf(surface, (cx - 7 * scale, sy - 50 * scale), 12 * scale, 7 * scale, 35)
        return

    if plant_type == "chomper":
        swallow = plant.swallow_timer if plant else 0.0
        is_chewing = swallow > 0
        chew_offset = math.sin(time_value * 7.0) * 5 * scale if is_chewing else 0.0
        pygame.draw.line(surface, (46, 117, 48), (cx, cy + 28 * scale), (cx, cy - 8 * scale), max(2, int(8 * scale)))
        for angle in (-50, -20, 20, 50):
            draw_leaf(surface, (cx + math.sin(math.radians(angle)) * 22 * scale, cy + 16 * scale), 16 * scale, 9 * scale, angle)
        head_x = cx + sway
        head_y = cy - 25 * scale + chew_offset
        pygame.draw.ellipse(surface, (72, 32, 95), (head_x - 30 * scale, head_y - 28 * scale, 60 * scale, 56 * scale))
        pygame.draw.ellipse(surface, (142, 68, 173), (head_x - 27 * scale, head_y - 25 * scale, 54 * scale, 50 * scale))
        if is_chewing:
            pygame.draw.ellipse(surface, (46, 125, 50), (head_x - 4 * scale, head_y - 5 * scale, 32 * scale, 18 * scale), max(2, int(3 * scale)))
            pygame.draw.line(surface, C_INK, (head_x - 2 * scale, head_y + 4 * scale), (head_x + 26 * scale, head_y + 4 * scale), 2)
            for i in range(2):
                bubble_y = head_y - 24 * scale - (time_value * 15 + i * 12) % 24
                bubble_x = head_x + math.sin(time_value * 3 + i) * 12 * scale
                pygame.draw.circle(surface, (145, 225, 95), (bubble_x, bubble_y), 3.5 * scale, 1)
        else:
            jaw_open = 18 * scale
            pygame.draw.polygon(surface, (88, 24, 40), [
                (head_x + 6 * scale, head_y),
                (head_x + 36 * scale, head_y - jaw_open),
                (head_x + 36 * scale, head_y + jaw_open),
            ])
            for t in range(3):
                tx = head_x + (14 + t * 7) * scale
                pygame.draw.polygon(surface, (250, 252, 240), [(tx - 3 * scale, head_y - 12 * scale), (tx + 3 * scale, head_y - 12 * scale), (tx, head_y - 4 * scale)])
                pygame.draw.polygon(surface, (250, 252, 240), [(tx - 3 * scale, head_y + 12 * scale), (tx + 3 * scale, head_y + 12 * scale), (tx, head_y + 4 * scale)])
            pygame.draw.line(surface, (52, 140, 56), (head_x + 4 * scale, head_y - 2 * scale), (head_x + 36 * scale, head_y - jaw_open), max(2, int(4 * scale)))
            pygame.draw.line(surface, (52, 140, 56), (head_x + 4 * scale, head_y + 2 * scale), (head_x + 36 * scale, head_y + jaw_open), max(2, int(4 * scale)))
        pygame.draw.circle(surface, (250, 252, 220), (head_x - 12 * scale, head_y - 14 * scale), 5 * scale)
        pygame.draw.circle(surface, C_INK, (head_x - 10 * scale, head_y - 14 * scale), 2.2 * scale)
        return

    if plant_type == "cherrybomb":
        pulse = 1 + math.sin(time_value * 9) * 0.04 * min(1.0, age)
        pygame.draw.line(surface, (55, 112, 43), (cx - 14 * scale, cy - 28 * scale), (cx - 5 * scale, cy - 54 * scale), 4)
        pygame.draw.line(surface, (55, 112, 43), (cx + 16 * scale, cy - 26 * scale), (cx + 7 * scale, cy - 54 * scale), 4)
        draw_leaf(surface, (cx + 2 * scale, cy - 52 * scale), 15 * scale, 8 * scale, 5)
        for dx, face_x, color in [(-15, -1, (214, 48, 56)), (17, 1, (235, 66, 66))]:
            r = 25 * scale * pulse
            pygame.draw.circle(surface, (93, 30, 34), (cx + dx * scale, cy - 7 * scale), r + 2.5 * scale)
            pygame.draw.circle(surface, color, (cx + dx * scale, cy - 7 * scale), r)
            pygame.draw.circle(surface, (255, 118, 102), (cx + (dx - 7) * scale, cy - 16 * scale), 6 * scale)
            draw_face(surface, cx + dx * scale, cy - 3 * scale, scale * 0.78, angry=True)
        return

    if plant_type == "potatomine":
        armed = age >= 6.0
        pygame.draw.ellipse(surface, (60, 47, 36), (cx - 31 * scale, cy + 13 * scale, 62 * scale, 20 * scale))
        pygame.draw.ellipse(surface, (107, 72, 42), (cx - 31 * scale, cy - 10 * scale, 62 * scale, 43 * scale))
        pygame.draw.ellipse(surface, (161, 105, 55), (cx - 27 * scale, cy - 12 * scale, 54 * scale, 36 * scale))
        pygame.draw.circle(surface, C_INK, (cx - 10 * scale, cy + 1 * scale), 2.5 * scale)
        pygame.draw.circle(surface, C_INK, (cx + 10 * scale, cy + 1 * scale), 2.5 * scale)
        pygame.draw.arc(surface, C_INK, (cx - 8 * scale, cy + 2 * scale, 16 * scale, 10 * scale), 0.1, math.pi - 0.1, 2)
        light = (242, 65, 50) if armed else (90, 70, 59)
        if armed:
            draw_glow_circle(surface, (cx, cy - 22 * scale), 6 * scale, (247, 82, 70))
        pygame.draw.circle(surface, light, (cx, cy - 22 * scale), 5 * scale)
        pygame.draw.line(surface, C_INK, (cx, cy - 17 * scale), (cx, cy - 8 * scale), 2)
        return

    if plant_type == "jalapeno":
        body_rect = pygame.Rect(int(cx - 17 * scale), int(cy - 35 * scale), int(35 * scale), int(77 * scale))
        pygame.draw.ellipse(surface, (98, 33, 35), body_rect.inflate(5 * scale, 5 * scale))
        pygame.draw.ellipse(surface, (218, 47, 43), body_rect)
        pygame.draw.arc(surface, (255, 131, 81), body_rect.inflate(-10 * scale, -10 * scale), 1.4, 3.6, 3)
        pygame.draw.line(surface, (55, 112, 43), (cx, cy - 35 * scale), (cx - 5 * scale, cy - 52 * scale), 4)
        draw_face(surface, cx, cy - 11 * scale, scale * 0.8, angry=True)


def draw_glow_circle(
    surface: pygame.Surface,
    center: tuple[float, float],
    radius: float,
    color: tuple[int, int, int],
) -> None:
    dims = int(radius * 5)
    key = (dims, color)
    glow = _GLOW_CACHE.get(key)
    if glow is None:
        glow = pygame.Surface((dims, dims), pygame.SRCALPHA)
        for i in range(7, 0, -1):
            pygame.draw.circle(
                glow, (*color, int(8 + i * 5)),
                (dims // 2, dims // 2),
                radius * (0.5 + i * 0.32),
            )
        _GLOW_CACHE[key] = glow
    surface.blit(glow, (center[0] - glow.get_width() / 2, center[1] - glow.get_height() / 2))


def draw_zombie(
    surface: pygame.Surface,
    zombie: "Zombie",
    time_value: float,
    alpha: int = 255,
    dy_offset: float = 0.0,
    cell_h: int = CELL_H,
) -> None:
    ground = lane_ground(zombie.row, cell_h=cell_h)
    try:
        if pvz_graphics.render_zombie_sprite(surface, zombie, time_value, ground, alpha, dy_offset):
            return
    except Exception:
        pass
    x = zombie.x
    ground += dy_offset
    
    # Check vault jump
    vault_y = 0.0
    if zombie.ztype == "pole" and zombie.vault_state == "jumping":
        prog = clamp(zombie.vault_progress, 0.0, 1.0)
        vault_y = -math.sin(prog * math.pi) * 65.0
    ground += vault_y

    walk_speed = 8.7 if zombie.ztype in ("runner", "pole") else (10.5 if zombie.enraged else 5.0)
    walk = math.sin(time_value * walk_speed + zombie.phase)
    lean = walk * 1.3
    if zombie.enraged:
        lean += 6.0  # forward aggressive sprint lean

    slow_tint = (176, 221, 227) if zombie.slow_timer > 0 else None
    skin = slow_tint or (153, 177, 143)
    skin_dark = (84, 108, 82) if not slow_tint else (98, 145, 164)
    coat = (82, 91, 91)
    shirt = (118, 90, 77)
    pants = (61, 72, 78)

    if zombie.ztype == "pole":
        coat = (220, 68, 62)
        shirt = (245, 245, 240)
        pants = (45, 52, 60)
    elif zombie.ztype == "newspaper":
        coat = (108, 122, 137)
        shirt = (178, 190, 195)
        pants = (85, 95, 105)

    pygame.draw.ellipse(surface, (31, 47, 37, 100), (x - 33, ground - 3, 70, 16))
    leg_swing = walk * (10 if zombie.enraged else 7)
    pygame.draw.line(surface, pants, (x - 4, ground - 38), (x - 10 + leg_swing, ground - 5), 9)
    pygame.draw.line(surface, pants, (x + 7, ground - 38), (x + 15 - leg_swing, ground - 5), 9)
    pygame.draw.ellipse(surface, (36, 42, 38), (x - 20 + leg_swing, ground - 9, 20, 8))
    pygame.draw.ellipse(surface, (36, 42, 38), (x + 7 - leg_swing, ground - 9, 20, 8))

    body_rect = pygame.Rect(int(x - 22 + lean), int(ground - 76), 45, 41)
    pygame.draw.rect(surface, (38, 47, 44), body_rect.inflate(5, 5), border_radius=12)
    pygame.draw.rect(surface, coat, body_rect, border_radius=10)
    pygame.draw.polygon(
        surface, shirt,
        [(x - 7 + lean, ground - 75), (x + 7 + lean, ground - 75),
         (x + 11 + lean, ground - 39), (x - 12 + lean, ground - 39)],
    )
    pygame.draw.line(surface, (46, 53, 49), (x + lean, ground - 69), (x + lean, ground - 42), 3)

    arm_swing = walk * (15 if zombie.enraged else 11)
    arm_color = skin_dark
    pygame.draw.line(
        surface, arm_color,
        (x - 17 + lean, ground - 68),
        (x - 43 + arm_swing, ground - 47),
        9,
    )
    pygame.draw.line(
        surface, arm_color,
        (x + 18 + lean, ground - 66),
        (x + 43 - arm_swing, ground - 56),
        9,
    )
    pygame.draw.circle(surface, skin, (x - 45 + arm_swing, ground - 46), 6)
    pygame.draw.circle(surface, skin, (x + 45 - arm_swing, ground - 56), 6)

    head_x = x + lean + 2
    head_y = ground - 94 + abs(walk) * 1.4
    pygame.draw.circle(surface, (52, 66, 55), (head_x, head_y), 24)
    pygame.draw.circle(surface, skin, (head_x, head_y), 22)
    pygame.draw.ellipse(surface, skin_dark, (head_x - 23, head_y - 9, 14, 21))

    # Eyes & Mouth
    if zombie.enraged:
        # Fiery red eyes!
        pygame.draw.circle(surface, (255, 30, 30), (head_x - 8, head_y - 3), 4.5)
        pygame.draw.circle(surface, (255, 230, 50), (head_x - 8, head_y - 3), 2.0)
        pygame.draw.circle(surface, (255, 30, 30), (head_x + 8, head_y - 4), 4.0)
        pygame.draw.circle(surface, (255, 230, 50), (head_x + 8, head_y - 4), 1.8)
        # Savage open roaring mouth
        pygame.draw.ellipse(surface, (120, 20, 20), (head_x - 10, head_y + 3, 20, 14))
        pygame.draw.polygon(surface, (250, 250, 240), [(head_x - 5, head_y + 3), (head_x - 3, head_y + 8), (head_x - 1, head_y + 3)])
    else:
        pygame.draw.circle(surface, (33, 48, 38), (head_x - 8, head_y - 3), 3)
        pygame.draw.circle(surface, (33, 48, 38), (head_x + 8, head_y - 4), 2.6)
        pygame.draw.ellipse(surface, (49, 47, 40), (head_x - 7, head_y + 6, 16, 9))
        pygame.draw.line(surface, (66, 61, 50), (head_x - 3, head_y + 7), (head_x - 3, head_y + 12), 1)
        pygame.draw.line(surface, (66, 61, 50), (head_x + 4, head_y + 7), (head_x + 4, head_y + 12), 1)
        pygame.draw.line(surface, skin_dark, (head_x - 6, head_y + 17), (head_x + 12, head_y + 14), 2)

    # Hats & Props
    if zombie.ztype == "cone":
        pygame.draw.polygon(
            surface, (86, 66, 44),
            [(head_x - 24, head_y - 15), (head_x + 2, head_y - 62), (head_x + 24, head_y - 13)],
        )
        pygame.draw.polygon(
            surface, (229, 126, 39),
            [(head_x - 18, head_y - 17), (head_x + 2, head_y - 56), (head_x + 18, head_y - 15)],
        )
        pygame.draw.line(surface, (255, 177, 72), (head_x - 9, head_y - 29), (head_x + 11, head_y - 28), 5)
    elif zombie.ztype == "bucket":
        hat_rect = pygame.Rect(int(head_x - 24), int(head_y - 42), 48, 31)
        pygame.draw.rect(surface, (63, 75, 76), hat_rect.inflate(4, 4), border_radius=8)
        pygame.draw.rect(surface, (155, 168, 164), hat_rect, border_radius=6)
        pygame.draw.rect(surface, (191, 202, 194), (head_x - 27, head_y - 17, 54, 7), border_radius=3)
        pygame.draw.line(surface, (97, 109, 106), (head_x - 14, head_y - 34), (head_x - 11, head_y - 15), 3)
        pygame.draw.line(surface, (97, 109, 106), (head_x + 12, head_y - 34), (head_x + 10, head_y - 15), 3)
    elif zombie.ztype == "runner":
        pygame.draw.line(surface, (229, 72, 64), (head_x - 22, head_y - 14), (head_x + 22, head_y - 17), 6)
        pygame.draw.polygon(surface, (244, 226, 166), [(head_x - 19, head_y - 16), (head_x - 34, head_y - 5), (head_x - 19, head_y - 5)])
        pygame.draw.circle(surface, (224, 232, 216), (head_x - 13, head_y - 30), 3)
        pygame.draw.circle(surface, (224, 232, 216), (head_x + 15, head_y - 28), 2)
    elif zombie.ztype == "pole":
        # White headband
        pygame.draw.line(surface, (245, 245, 245), (head_x - 20, head_y - 14), (head_x + 20, head_y - 16), 5)
        # Vaulting Pole
        if zombie.has_pole:
            pole_color = (168, 112, 62)
            if zombie.vault_state == "jumping":
                # Pole planted into the ground
                pole_tip = (x - 20, ground - vault_y)
                pole_top = (x - 45 + arm_swing, ground - 46)
                pygame.draw.line(surface, pole_color, pole_tip, pole_top, 5)
            else:
                # Carried forward
                pole_p1 = (x - 55, ground - 30)
                pole_p2 = (x + 35, ground - 90)
                pygame.draw.line(surface, pole_color, pole_p1, pole_p2, 5)
                pygame.draw.circle(surface, (220, 220, 220), pole_p1, 4)
    elif zombie.ztype == "newspaper":
        # Reading glasses
        pygame.draw.rect(surface, (50, 50, 50), (head_x - 13, head_y - 8, 11, 8), 1)
        pygame.draw.rect(surface, (50, 50, 50), (head_x + 2, head_y - 8, 11, 8), 1)
        pygame.draw.line(surface, (50, 50, 50), (head_x - 2, head_y - 5), (head_x + 2, head_y - 5), 1)
        # Newspaper shield
        if zombie.has_newspaper:
            np_x = x - 42 + lean
            np_y = ground - 76
            np_rect = pygame.Rect(int(np_x), int(np_y), 36, 48)
            pygame.draw.rect(surface, (245, 246, 242), np_rect, border_radius=3)
            pygame.draw.rect(surface, (120, 120, 120), np_rect, 1, border_radius=3)
            # Headline & text lines
            pygame.draw.line(surface, (40, 40, 40), (np_x + 4, np_y + 8), (np_x + 32, np_y + 8), 3)
            for li in range(4):
                pygame.draw.line(surface, (130, 130, 130), (np_x + 4, np_y + 16 + li * 7), (np_x + 30, np_y + 16 + li * 7), 1)

    if zombie.eating > 0:
        pygame.draw.arc(
            surface, (89, 57, 46),
            (head_x - 9, head_y + 1, 18, 18),
            0.1, math.pi - 0.1, 3,
        )

    if zombie.hp < zombie.max_hp:
        ratio = clamp(zombie.hp / zombie.max_hp, 0, 1)
        bar = pygame.Rect(int(x - 26), int(head_y - (74 if zombie.ztype == "cone" else 55)), 52, 6)
        pygame.draw.rect(surface, (48, 35, 33), bar, border_radius=3)
        fill = bar.inflate(-2, -2)
        fill.width = int(fill.width * ratio)
        color = (97, 198, 92) if ratio > 0.55 else (241, 186, 58) if ratio > 0.25 else (226, 73, 59)
        pygame.draw.rect(surface, color, fill, border_radius=2)


def draw_mower(surface: pygame.Surface, mower: "Mower", is_pool: bool = False, cell_h: int = CELL_H) -> None:
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


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: tuple[int, int, int]
    size: float
    life: float
    max_life: float
    gravity: float = 90.0
    alive: bool = True

    def update(self, dt: float) -> None:
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt


@dataclass
class FloatingText:
    x: float
    y: float
    value: str
    color: tuple[int, int, int]
    life: float = 0.95
    max_life: float = 0.95
    alive: bool = True
    image: pygame.Surface | None = None

    def update(self, dt: float) -> None:
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        self.y -= 26 * dt


@dataclass
class SunToken:
    x: float
    y: float
    target_y: float
    value: int = 25
    speed: float = 120.0
    age: float = 0.0
    phase: float = field(default_factory=lambda: random.random() * 6.0)
    collected: bool = False

    def update(self, dt: float) -> None:
        self.age += dt
        if self.y < self.target_y:
            self.y = min(self.target_y, self.y + self.speed * dt)

    def center(self) -> tuple[int, int]:
        return int(self.x), int(self.y + math.sin(self.age * 3 + self.phase) * 2)

    def contains(self, pos: tuple[int, int]) -> bool:
        cx, cy = self.center()
        return (pos[0] - cx) ** 2 + (pos[1] - cy) ** 2 <= 38 ** 2


@dataclass
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
    cannon_ready: bool = True
    cannon_timer: float = 0.0
    agave_state: str = "idle"
    agave_timer: float = 0.0
    laser_timer: float = 0.0
    laser_active: float = 0.0

    is_pool: bool = False

    def __post_init__(self) -> None:
        self._x, self._y = cell_center(self.col, self.row, cell_h=self.cell_h, is_pool=self.is_pool)

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
    hypnotized: bool = False
    has_imp: bool = True
    flying: bool = True
    jackbox_timer: float = 7.0
    digging: bool = False
    emerged: bool = False
    is_pool: bool = False

    @property
    def y(self) -> float:
        return lane_ground(self.row, cell_h=self.cell_h, is_pool=self.is_pool) - 50.0

    def rect(self) -> pygame.Rect:
        ground = lane_ground(self.row, cell_h=self.cell_h, is_pool=self.is_pool)
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
        if not getattr(self, "rewarded_gold", False) and "golden_mower" in game.artifacts:
            self.rewarded_gold = True
            game.sun += 200
            game.float_text(self.x + 30, lane_ground(self.row, cell_h=self.cell_h) - 40, "+200 镀金奖励！", C_GOLD)
            game.burst(self.x + 30, lane_ground(self.row, cell_h=self.cell_h) - 20, (255, 220, 80), 20)
            game.audio.play("collect")
        self.x += 520 * dt
        for zombie in game.zombies:
            if zombie.row == self.row and not zombie.dead and abs(zombie.x - self.x) < 62:
                game.kill_zombie(zombie, mower=True)
        if self.x > WIDTH + 60:
            self.spent = True


class Game:
    def __init__(self, screen: pygame.Surface, headless: bool = False) -> None:
        self.screen = screen
        pvz_graphics.init_graphics()
        self.fonts = FontBook()
        self.audio = AudioBank()
        self.is_pool = False
        self.rows = ROWS
        self.cell_h = CELL_H
        self.pool_rows: list[int] = []
        self.grid_bottom = GRID_BOTTOM
        self.save_data = load_save()
        self.artifacts = set(self.save_data.get("artifacts", [])).union(getattr(self, "artifacts", set()))
        self.slot_capacity = 10 if "master_belt" in self.artifacts else 9
        self.reward_overlay_data: dict | None = None
        self.clock = pygame.time.Clock()
        self.running = True
        self.headless = headless
        self.mode = "menu"
        self.time_value = 0.0
        self.ambient = 0.0
        self.game_speed = 1.0
        self.level_index = 0
        self.level_buttons: list[tuple[pygame.Rect, int]] = []
        self.seed_rects: dict[str, pygame.Rect] = {}
        self.selected_seeds: list[str] = []
        self.slot_capacity: int = 9
        self.catalog_rects: dict[str, pygame.Rect] = {}
        self.slot_rects: list[pygame.Rect] = []
        self.seed_btn_back = pygame.Rect(160, 642, 130, 48)
        self.seed_btn_clear = pygame.Rect(310, 642, 130, 48)
        self.seed_btn_start = pygame.Rect(460, 638, 280, 56)
        self.seed_btn_recommend = pygame.Rect(760, 642, 150, 48)
        self.topright_panel_rect = pygame.Rect(915, 10, 275, 80)
        self.speed_rect = pygame.Rect(925, 46, 48, 36)
        self.pause_rect = pygame.Rect(978, 46, 48, 36)
        self.shovel_rect = pygame.Rect(1031, 46, 48, 36)
        self.audio_rect = pygame.Rect(1084, 46, 48, 36)
        self.skip_rect = pygame.Rect(1137, 46, 48, 36)
        self.warp_buttons: list[tuple[pygame.Rect, int]] = []
        self.warp_next_btn = pygame.Rect(0, 0, 0, 0)
        self.warp_close_btn = pygame.Rect(0, 0, 0, 0)
        self._reset_runtime()
        self.background_cache: dict[str, pygame.Surface] = {}
        self.menu_background: pygame.Surface | None = None
        self.stars = [(random.randint(0, WIDTH), random.randint(HUD_H, GRID_BOTTOM), random.random()) for _ in range(70)]
        self.save_data = load_save()
        if not self.headless:
            self.audio.play_music("menu")

    def _reset_runtime(self) -> None:
        self.plants: list[Plant] = []
        self.zombies: list[Zombie] = []
        self.projectiles: list[Projectile] = []
        self.suns: list[SunToken] = []
        self.particles: list[Particle] = []
        self.floating_texts: list[FloatingText] = []
        self.mowers = [
            Mower(row, cell_h=self.cell_h, is_pool=(self.is_pool and row in self.pool_rows))
            for row in range(self.rows)
        ]
        self.sun = 150
        self.cooldowns = {name: 0.0 for name in UNLOCK_ORDER}
        self.selected_plant: str | None = None
        self.shovel_selected = False
        self.elapsed = 0.0
        self.intro_timer = 2.2
        self.natural_sun_timer = 3.0
        self.waves: list[Wave] = []
        self.current_wave_index = -1
        self.wave_started_at = 0.0
        self.next_wave_at = FIRST_WAVE_DELAY
        self.pending_wave_spawns: list[tuple[float, int, WaveMember]] = []
        self.spawned_count = 0
        self.total_zombies = 0
        self.banner = ""
        self.banner_timer = 0.0
        self.banner_warm = False
        self.overlay = ""
        self.overlay_age = 0.0
        self.audio_on = getattr(self, "audio_on", True)
        self.lose_reason = ""
        self.wave_flash = 0.0
        self.endless_wave_record = 0

    def start_level(self, index: int) -> None:
        self.level_index = int(clamp(index, 0, len(LEVELS) - 1))
        level = LEVELS[self.level_index]
        self.is_pool = bool(level.get("pool", False))
        self.rows = 6 if self.is_pool else 5
        self.cell_h = 96 if self.is_pool else 116
        self.pool_rows = [2, 3] if self.is_pool else []
        self.grid_bottom = GRID_Y + self.rows * self.cell_h
        self.save_data = load_save()
        self.artifacts = set(self.save_data.get("artifacts", [])).union(getattr(self, "artifacts", set()))
        self.slot_capacity = 10 if "master_belt" in self.artifacts else 9
        self._reset_runtime()
        bonus_sun = 100 if "sun_vault" in self.artifacts else 0
        self.sun = level["sun"] + bonus_sun
        self.waves = self._build_waves()
        self.total_zombies = sum(len(wave.members) for wave in self.waves)
        self.banner = f"第 {self.level_index + 1} 关  {level['name']}"
        self.banner_timer = 3.0
        self.banner_warm = False
        self.audio.enabled = self.audio_on
        self.audio.play("click")

        unlocked = self.available_plants()
        if self.headless or len(unlocked) <= self.slot_capacity:
            self.selected_seeds = list(unlocked[:self.slot_capacity])
            self._begin_battle_music()
            self.mode = "playing"
        else:
            if not self.selected_seeds or not all(p in unlocked for p in self.selected_seeds):
                self._recommend_seeds()
            self.mode = "seed_select"
            if not self.headless:
                self.audio.play_music("seeds")

    def _begin_battle_music(self) -> None:
        if self.headless:
            return
        level = LEVELS[self.level_index]
        if getattr(level, "get", lambda k, d=None: d)("endless", False) or self.level_index == len(LEVELS) - 1:
            self.audio.play_music("endless")
        elif level.get("theme") == "night":
            self.audio.play_music("night")
        else:
            self.audio.play_music("day")

    def _recommend_seeds(self) -> None:
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
        self.selected_seeds = picks[:self.slot_capacity]

    def _confirm_seeds_and_start(self) -> None:
        if not self.selected_seeds:
            self._recommend_seeds()
        self.audio.play("click")
        self._begin_battle_music()
        self.mode = "playing"

    def go_to_menu(self) -> None:
        self.mode = "menu"
        self.overlay = ""
        self.selected_plant = None
        self.shovel_selected = False
        if not self.headless:
            self.audio.play_music("menu")

    def _build_waves(self) -> list[Wave]:
        level = LEVELS[self.level_index]
        rng = random.Random(2718 + self.level_index * 97)
        count = int(level["count"])
        mix = list(level["mix"])
        types = list(ZOMBIES)
        wave_count = min(6, 3 + self.level_index // 3)

        weights = [0.75 + i * 0.12 for i in range(wave_count)]
        weights[-1] *= 1.35
        weight_sum = sum(weights)
        counts = [max(1, round(count * weight / weight_sum)) for weight in weights]
        while sum(counts) > count:
            candidates = [i for i, value in enumerate(counts) if value > 1]
            if not candidates:
                break
            largest = max(candidates, key=lambda i: counts[i])
            counts[largest] -= 1
        counts[-1] += count - sum(counts)

        waves: list[Wave] = []
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

                # 水路僵尸严格阵营划分：绝不允许水路僵尸走到陆地！
                pool_lanes = [2, 3] if self.is_pool else []
                land_lanes = [r for r in range(rows) if r not in pool_lanes]
                if ztype in ("ducky", "snorkel", "dolphin"):
                    if pool_lanes:
                        lane = rng.choice(pool_lanes)
                    else:
                        ztype = "basic"
                        lane = rng.randrange(rows)
                elif ztype in ("pole", "newspaper", "runner"):
                    lane = rng.choice(land_lanes) if land_lanes else rng.randrange(rows)
                else:
                    if wave_index == wave_count - 1 and member_index < rows:
                        lane = member_index
                    else:
                        lane = rng.randrange(rows)
                        if member_index > 0 and rng.random() < 0.3 and lane == last_lane:
                            lane = (lane + rng.randint(1, rows - 1)) % rows
                    if pool_lanes and lane in pool_lanes and ztype in ("basic", "cone", "bucket"):
                        ztype = "ducky"
                last_lane = lane
                members.append(WaveMember(delay, ztype, lane))
                is_final_level = self.level_index >= 9
                step_min = 1.6 if is_final_level else 1.2
                step_max = 2.8 if is_final_level else 2.2
                delay += rng.uniform(step_min, step_max)

            total_hp = sum(float(ZOMBIES[member.ztype]["hp"]) for member in members)
            is_last = wave_index == wave_count - 1
            advance_ratio = 0.0 if is_last else max(0.58, 0.76 - wave_index * 0.025)
            gap_low = max(20.0, 24.0 - self.level_index * 0.35)
            gap_high = max(gap_low + 2.0, 30.0 - self.level_index * 0.35)
            waves.append(
                Wave(
                    index=wave_index,
                    members=members,
                    total_hp=total_hp,
                    advance_ratio=advance_ratio,
                    fallback_gap=rng.uniform(gap_low, gap_high),
                )
            )
        return waves

    def available_plants(self) -> list[str]:
        # 植物逐步赠送解锁系统：第一关仅基础植物，随后每通关一关解锁赠送新植物
        unlocked = list(DEFAULT_INITIAL_PLANTS)
        save = load_save()
        completed = set(save.get("completed", []))
        for c_idx in sorted(completed):
            rewards = LEVEL_REWARDS.get(c_idx, {}).get("plants", [])
            for p in rewards:
                if p in UNLOCK_ORDER and p not in unlocked:
                    unlocked.append(p)

        # 自由跳关关卡体验保障：
        # 当跳关到关卡 level_index 时，自动享有截止到该关卡为止的所有战利品植物与神器！
        # 避免跳到后面关卡却因为没打前面关卡而没有植物可用！
        for prev_idx in range(self.level_index):
            for p in LEVEL_REWARDS.get(prev_idx, {}).get("plants", []):
                if p not in unlocked:
                    unlocked.append(p)
            art = LEVEL_REWARDS.get(prev_idx, {}).get("artifact")
            if art and art not in self.artifacts:
                self.artifacts.add(art)

        # 如果直接跳到第 16 关无尽挑战，直接全植物与大师腰带大满贯！
        if self.level_index >= 15:
            unlocked = list(UNLOCK_ORDER)
            self.artifacts.add("master_belt")

        # 泳池关卡（11关及以后，即 level_index >= 10）必须自动保证拥有睡莲作为水生载体
        if getattr(self, "is_pool", False) and "lilypad" not in unlocked:
            unlocked.append("lilypad")

        return [p for p in UNLOCK_ORDER if p in unlocked]

    def begin_loop(self) -> None:
        while self.running:
            raw_dt = min(0.05, self.clock.tick(FPS) / 1000.0)
            self.time_value += raw_dt
            self.ambient += raw_dt
            self.handle_events()
            self.update(raw_dt)
            self.draw()
            pygame.display.flip()

    def handle_events(self) -> None:
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
                self.shovel_selected = False

    def _handle_key(self, key: int) -> None:
        # 任意快捷跳关快捷键
        if key in (pygame.K_TAB, pygame.K_n):
            next_lvl = (self.level_index + 1) % len(LEVELS)
            self.start_level(next_lvl)
            self.float_text(600, 80, f"跳关前往：第 {next_lvl + 1:02d} 关 · {LEVELS[next_lvl]['name']}", C_GOLD)
            return
        elif key == pygame.K_p:
            prev_lvl = (self.level_index - 1) % len(LEVELS)
            self.start_level(prev_lvl)
            self.float_text(600, 80, f"跳关前往：第 {prev_lvl + 1:02d} 关 · {LEVELS[prev_lvl]['name']}", C_GOLD)
            return
        elif key == pygame.K_l:
            self.overlay = "" if self.overlay == "warp" else "warp"
            return

        if key == pygame.K_ESCAPE:
            if self.mode == "menu":
                self.running = False
            elif self.overlay in ("paused", "warp"):
                self.overlay = ""
                self.audio.unpause_music()
            elif self.overlay:
                self.go_to_menu()
            elif self.selected_plant or self.shovel_selected:
                self.selected_plant = None
                self.shovel_selected = False
            else:
                self.overlay = "paused"
                self.audio.pause_music()
            return
        if self.mode == "seed_select":
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self._confirm_seeds_and_start()
            elif key == pygame.K_r:
                self._recommend_seeds()
                self.audio.play("click")
            elif key == pygame.K_c:
                self.selected_seeds.clear()
                self.audio.play("click")
            elif key == pygame.K_ESCAPE:
                self.go_to_menu()
            return
        if self.mode == "menu":
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_level(0)
            elif pygame.K_1 <= key <= pygame.K_9:
                self.start_level(key - pygame.K_1)
            elif key == pygame.K_0:
                self.start_level(9)
            elif key == pygame.K_e:
                self.start_level(10)
            return
        if key == pygame.K_p:
            if self.overlay in ("", "paused"):
                if self.overlay == "paused":
                    self.overlay = ""
                    self.audio.unpause_music()
                else:
                    self.overlay = "paused"
                    self.audio.pause_music()
        elif key in (pygame.K_SPACE, pygame.K_f):
            # 切换 1x / 2x 倍速
            self.game_speed = 2.0 if self.game_speed == 1.0 else 1.0
            self.float_text(self.speed_rect.centerx, self.speed_rect.bottom + 15, f"{self.game_speed:0.0f}x 速度", C_GOLD)
        elif key == pygame.K_c:
            # 一键吸附全屏阳光
            count = 0
            for token in self.suns:
                if not token.collected:
                    self.collect_sun(token)
                    count += 1
            if count > 0:
                self.audio.play("collect")
        elif key == pygame.K_r:
            self.start_level(self.level_index)
        elif key == pygame.K_m and self.audio_on is not None:
            self.audio_on = not self.audio_on
            self.audio.enabled = self.audio_on
        elif pygame.K_1 <= key <= pygame.K_9:
            idx = key - pygame.K_1
            deck = self.selected_seeds if self.selected_seeds else self.available_plants()[:self.slot_capacity]
            if idx < len(deck):
                self._select_plant(deck[idx])

    def _select_plant(self, plant_name: str) -> None:
        if self.overlay:
            return
        deck = self.selected_seeds if self.selected_seeds else self.available_plants()[:self.slot_capacity]
        if plant_name not in deck:
            return
        if self.cooldowns[plant_name] > 0 or self.sun < PLANTS[plant_name]["cost"]:
            return
        self.selected_plant = None if self.selected_plant == plant_name else plant_name
        self.shovel_selected = False

    def _handle_click(self, pos: tuple[int, int]) -> None:
        if self.overlay == "warp":
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
        if self.mode == "menu":
            for rect, index in self.level_buttons:
                if rect.collidepoint(pos):
                    self.start_level(index)
                    return
            return

        if self.mode == "seed_select":
            if hasattr(self, "seed_btn_back") and self.seed_btn_back.collidepoint(pos):
                self.go_to_menu()
                return
            if self.seed_btn_start.collidepoint(pos):
                self._confirm_seeds_and_start()
                return
            if self.seed_btn_recommend.collidepoint(pos):
                self._recommend_seeds()
                self.audio.play("click")
                return
            if self.seed_btn_clear.collidepoint(pos):
                self.selected_seeds.clear()
                self.audio.play("click")
                return
            for i, rect in enumerate(self.slot_rects):
                if rect.collidepoint(pos) and i < len(self.selected_seeds):
                    self.selected_seeds.pop(i)
                    self.audio.play("click")
                    return
            unlocked = set(self.available_plants())
            for name, rect in self.catalog_rects.items():
                if rect.collidepoint(pos):
                    if name not in unlocked:
                        return
                    if name in self.selected_seeds:
                        self.selected_seeds.remove(name)
                        self.audio.play("click")
                    elif len(self.selected_seeds) < self.slot_capacity:
                        self.selected_seeds.append(name)
                        self.audio.play("click")
                    return
            return

        if self.overlay == "paused":
            if pygame.Rect(474, 476, 252, 52).collidepoint(pos):
                self.overlay = ""
                self.audio.unpause_music()
            elif pygame.Rect(474, 540, 252, 48).collidepoint(pos):
                self.start_level(self.level_index)
            elif pygame.Rect(474, 600, 252, 48).collidepoint(pos):
                self.go_to_menu()
            return
        if self.overlay == "won":
            if pygame.Rect(470, 526, 252, 54).collidepoint(pos):
                if self.level_index < len(LEVELS) - 1:
                    self.start_level(self.level_index + 1)
                else:
                    self.start_level(0)
            elif pygame.Rect(470, 592, 252, 44).collidepoint(pos):
                self.go_to_menu()
            return
        if self.overlay == "lost":
            if pygame.Rect(470, 526, 252, 54).collidepoint(pos):
                self.start_level(self.level_index)
            elif pygame.Rect(470, 592, 252, 44).collidepoint(pos):
                self.go_to_menu()
            return

        for token in reversed(self.suns):
            if token.contains(pos):
                self.collect_sun(token)
                return

        if pos[1] < HUD_H:
            if self.speed_rect.collidepoint(pos):
                self.game_speed = 2.0 if self.game_speed == 1.0 else 1.0
                return
            if self.pause_rect.collidepoint(pos):
                self.overlay = "paused"
                self.audio.pause_music()
                return
            if self.shovel_rect.collidepoint(pos):
                self.shovel_selected = not self.shovel_selected
                self.selected_plant = None
                return
            if self.audio_rect.collidepoint(pos):
                self.audio_on = not self.audio_on
                self.audio.enabled = self.audio_on
                self.audio.play("click")
                return
            if getattr(self, "skip_rect", None) and self.skip_rect.collidepoint(pos):
                self.overlay = "warp"
                self.audio.play("click")
                return
            for name, rect in self.seed_rects.items():
                if rect.collidepoint(pos):
                    self._select_plant(name)
                    return
            return

        col, row = self._cell_at(pos)
        if col is None or row is None:
            return

        is_water = getattr(self, "is_pool", False) and (row in getattr(self, "pool_rows", []))
        carrier = self._carrier_at(col, row)
        top_plant = self._top_plant_at(col, row)

        if self.shovel_selected:
            if top_plant is not None:
                cost = PLANTS[top_plant.ptype]["cost"]
                has_gold = "golden_shovel" in self.artifacts
                top_plant.alive = False
                self.burst(top_plant.x, top_plant.y, (255, 215, 80) if has_gold else (141, 98, 54), 16)
                if has_gold:
                    self.sun += cost
                    self.float_text(top_plant.x, top_plant.y - 30, f"+{cost} 黄金阳光返还！", C_GOLD)
                    self.audio.play("collect")
                else:
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
        new_plant = Plant(name, col, row, max_hp, max_hp, cell_h=self.cell_h, is_pool=self.is_pool)
        if is_water and carrier is not None and name not in ("lilypad", "cattail"):
            new_plant.carrier = carrier
            carrier.carried_plant = new_plant
        self.plants.append(new_plant)
        self.sun -= cost
        cd_mult = 0.70 if "rapid_seeds" in self.artifacts else 1.0
        self.cooldowns[name] = PLANTS[name]["cooldown"] * cd_mult
        self.selected_plant = None
        self.burst(new_plant.x, new_plant.y, (119, 176, 74), 12, upward=True)
        self.audio.play("plant")

    def _cell_at(self, pos: tuple[int, int]) -> tuple[int | None, int | None]:
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
        return next((p for p in self.plants if p.alive and p.col == col and p.row == row), None)

    def collect_sun(self, token: SunToken) -> None:
        if token.collected:
            return
        token.collected = True
        self.sun += token.value
        self.float_text(token.x, token.y - 12, f"+{token.value}", C_SUN)
        self.burst(token.x, token.y, (255, 220, 75), 8, upward=True)
        self.audio.play("collect", cooldown=0.04)

    def float_text(self, x: float, y: float, value: str, color: tuple[int, int, int]) -> None:
        item = FloatingText(x, y, value, color)
        item.image = self.fonts.get(19, True).render(value, True, color)
        self.floating_texts.append(item)

    def burst(
        self,
        x: float,
        y: float,
        color: tuple[int, int, int],
        amount: int,
        upward: bool = False,
        speed: float = 100.0,
    ) -> None:
        for _ in range(amount):
            angle = random.uniform(math.pi, math.tau) if upward else random.uniform(0, math.tau)
            velocity = random.uniform(speed * 0.35, speed)
            life = random.uniform(0.35, 0.9)
            self.particles.append(
                Particle(
                    x, y,
                    math.cos(angle) * velocity,
                    math.sin(angle) * velocity,
                    color,
                    random.uniform(2.2, 5.4),
                    life, life,
                    gravity=80 if upward else 120,
                )
            )

    def update(self, dt: float) -> None:
        if self.mode != "playing":
            return
        eff_dt = dt * self.game_speed
        self.overlay_age += eff_dt
        if self.banner_timer > 0:
            self.banner_timer -= eff_dt
        self.wave_flash = max(0.0, self.wave_flash - eff_dt * 1.8)
        if self.overlay:
            if self.overlay in ("won", "lost"):
                self._update_visuals(eff_dt)
            return

        self.elapsed += eff_dt
        self.intro_timer = max(0.0, self.intro_timer - eff_dt)
        for name in self.cooldowns:
            self.cooldowns[name] = max(0.0, self.cooldowns[name] - eff_dt)
        self._update_plants(eff_dt)
        self._update_zombies(eff_dt)
        self._update_projectiles(eff_dt)
        self._spawn_natural_sun(eff_dt)
        self._update_waves()
        for mower in self.mowers:
            mower.update(eff_dt, self)
        self._update_mowers()
        self._update_visuals(eff_dt)
        self._remove_dead()
        self._check_progress()

    def _update_visuals(self, dt: float) -> None:
        for token in self.suns:
            if not token.collected:
                token.update(dt)
        self.suns = [s for s in self.suns if not s.collected]
        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.alive]
        for item in self.floating_texts:
            item.update(dt)
        self.floating_texts = [t for t in self.floating_texts if t.alive]
        for zombie in self.zombies:
            zombie.flash = max(0.0, zombie.flash - dt)
            if zombie.dead:
                zombie.death_timer += dt
        self.zombies = [z for z in self.zombies if not z.dead or z.death_timer < 0.7]

    def _update_plants(self, dt: float) -> None:
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
            elif plant.ptype == "twinsunflower":
                # 双子向日葵：双倍产出 50 阳光
                if plant.action_timer >= (4.0 if plant.age < 8 else 6.8):
                    plant.action_timer = 0
                    target1 = lane_ground(plant.row, cell_h=self.cell_h) - 34 + random.randint(-15, 15)
                    target2 = lane_ground(plant.row, cell_h=self.cell_h) - 34 + random.randint(-15, 15)
                    self.suns.append(SunToken(plant.x - 22, plant.y - 45, target1))
                    self.suns.append(SunToken(plant.x + 22, plant.y - 45, target2))
            elif plant.ptype == "fumeshroom":
                # 大喷菇：喷射大范围紫色穿透孢子气雾
                if plant.action_timer >= 1.45:
                    has_target = any(
                        z.row == plant.row and not z.dead and z.x > plant.x - 20 and z.x < plant.x + 420
                        for z in self.zombies
                    )
                    if has_target:
                        plant.action_timer = 0
                        y = lane_ground(plant.row, cell_h=self.cell_h) - 62
                        self.projectiles.append(Projectile(plant.x + 45, y, plant.row, 20, bullet_type="fume"))
                        self.burst(plant.x + 40, y, (190, 85, 220), 8)
            elif plant.ptype == "starfruit":
                # 杨桃：5 方向散射金星
                if plant.action_timer >= 1.4:
                    if any(not z.dead for z in self.zombies):
                        plant.action_timer = 0
                        y = lane_ground(plant.row, cell_h=self.cell_h) - 58
                        for vx, vy in [(420, 0), (-420, 0), (0, -380), (0, 380), (-300, -300)]:
                            proj = Projectile(plant.x, y, plant.row, 20, bullet_type="star")
                            proj.speed = math.hypot(vx, vy)
                            proj.lob_progress = 0.0
                            # We will handle vx/vy in update_projectiles
                            setattr(proj, "vx", vx)
                            setattr(proj, "vy", vy)
                            self.projectiles.append(proj)
                        self.burst(plant.x, y, (255, 235, 80), 6)
            elif plant.ptype == "doomshroom":
                # 毁灭菇：1 秒后引发末日核爆
                if plant.age >= 1.0:
                    plant.alive = False
                    self.burst(plant.x, plant.y, (40, 20, 50), 30, speed=250.0)
                    self.burst(plant.x, plant.y, (255, 60, 40), 20, speed=200.0)
                    self.audio.play("cherrybomb")
                    self.float_text(plant.x, plant.y - 40, "末日核爆！", (255, 80, 60))
                    for z in self.zombies:
                        if not z.dead:
                            dist = math.hypot(z.x - plant.x, (lane_ground(z.row, cell_h=self.cell_h) - 40) - plant.y)
                            if dist <= 280:
                                self._damage_zombie(z, 1800.0)
            elif plant.ptype == "cobcannon":
                if not getattr(plant, "cannon_ready", True):
                    plant.cannon_timer -= dt
                    if plant.cannon_timer <= 0:
                        plant.cannon_ready = True
                        self.float_text(plant.x, plant.y - 45, "加农炮就绪！", C_GOLD)
                else:
                    threats = [z for z in self.zombies if not z.dead and 300 <= z.x <= 950]
                    if len(threats) >= 2 or any(z.ztype in ("gargantuar", "bucket", "runner") for z in threats):
                        target_z = max(threats, key=lambda z: z.hp)
                        plant.cannon_ready = False
                        plant.cannon_timer = 15.0
                        proj = Projectile(plant.x + 20, plant.y - 30, target_z.row, 1800.0, bullet_type="cob_missile")
                        proj.is_lobbed = True
                        proj.start_x = plant.x + 20
                        proj.start_y = plant.y - 30
                        proj.target_x = target_z.x
                        proj.target_y = lane_ground(target_z.row, cell_h=self.cell_h) - 40
                        proj.lob_progress = 0.0
                        proj.lob_duration = 0.8
                        proj.apex_h = 240.0
                        self.projectiles.append(proj)
                        self.float_text(plant.x, plant.y - 50, "发射玉米核弹！", (255, 215, 60))
                        self.audio.play("cherrybomb")
            elif plant.ptype == "magicshroom":
                plant.action_timer += dt
                if plant.action_timer >= 1.3:
                    targets = [z for z in self.zombies if z.row == plant.row and not z.dead and z.x >= plant.x - 20]
                    if targets:
                        plant.action_timer = 0.0
                        y = lane_ground(plant.row, cell_h=self.cell_h) - 52
                        proj = Projectile(plant.x + 20, y, plant.row, 35.0, bullet_type="magic_card")
                        proj.suit = random.choice(["heart", "spade", "diamond", "club"])
                        self.projectiles.append(proj)
                        self.audio.play("plant")
            elif plant.ptype == "agave":
                # 龙舌兰：近战 2 格蓄力二连斩
                close_z = [z for z in self.zombies if z.row == plant.row and not z.dead and plant.x <= z.x <= plant.x + CELL_W * 2.2]
                if close_z:
                    plant.agave_timer += dt
                    if plant.agave_timer >= 0.8:
                        plant.agave_timer = 0.0
                        for cz in close_z:
                            if cz.hp <= 100:
                                self._damage_zombie(cz, 200.0)
                                self.float_text(cz.x, cz.y - 40, "苍翠绝杀！", (120, 255, 180))
                            else:
                                self._damage_zombie(cz, 150.0)
                                self.float_text(cz.x, cz.y - 35, "-150 剑气！", (150, 240, 200))
                        self.burst(plant.x + 50, plant.y, (120, 255, 180), 20, upward=True)
                        self.audio.play("mower")
                else:
                    plant.agave_timer = 0.0
            elif plant.ptype == "laserbean":
                plant.laser_timer += dt
                if plant.laser_active > 0:
                    plant.laser_active -= dt
                elif plant.laser_timer >= 1.6:
                    row_z = [z for z in self.zombies if z.row == plant.row and not z.dead and z.x >= plant.x - 20]
                    if row_z:
                        plant.laser_timer = 0.0
                        plant.laser_active = 0.35
                        for lz in row_z:
                            self._damage_zombie(lz, 45.0)
                            self.float_text(lz.x, lz.y - 25, "激光穿透！", (80, 220, 255))
                        self.burst(plant.x + 60, plant.y, (80, 220, 255), 15)
                        self.audio.play("mower")
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
            elif plant.ptype == "gatlingpea":
                if plant.action_timer >= 1.45:
                    has_target = any(
                        z.row == plant.row and not z.dead and z.x > plant.x - 20 and z.x < GRID_RIGHT + 180
                        for z in self.zombies
                    )
                    if has_target:
                        plant.action_timer = 0
                        y = lane_ground(plant.row, cell_h=self.cell_h) - 70
                        # 四连发强力机枪扫射
                        for b_i in range(4):
                            self.projectiles.append(Projectile(plant.x + 24 - b_i * 12, y + (b_i % 2) * 4, plant.row, 25))
                        self.audio.play("plant", cooldown=0.1)
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

    def _update_zombies(self, dt: float) -> None:
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
                        if target_plant.ptype == "tallnut":
                            # 高坚果拦截撑杆跳！
                            zombie.has_pole = False
                            zombie.vault_state = "done"
                            zombie.speed = 16.0
                            self.audio.play("groan")
                            self.float_text(zombie.x, zombie.y - 30, "撞上高坚果！", (255, 120, 100))
                            self.burst(zombie.x, zombie.y, (180, 140, 90), 12)
                        else:
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
                        if target_plant.ptype == "tallnut":
                            # 高坚果拦截撑杆跳！
                            zombie.has_pole = False
                            zombie.vault_state = "done"
                            zombie.speed = 16.0
                            self.audio.play("groan")
                            self.float_text(zombie.x, zombie.y - 30, "撞上高坚果！", (255, 120, 100))
                            self.burst(zombie.x, zombie.y, (180, 140, 90), 12)
                        else:
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

            # 巨人半血抛掷小鬼
            if zombie.ztype == "gargantuar" and getattr(zombie, "has_imp", True) and zombie.hp <= 1500:
                zombie.has_imp = False
                throw_col = 3
                throw_x = GRID_X + throw_col * CELL_W + 40
                imp = Zombie("imp", zombie.row, throw_x, 90, 90, 38.0, 25.0, cell_h=self.cell_h)
                self.zombies.append(imp)
                self.float_text(zombie.x, zombie.y - 50, "抛掷小鬼！", (255, 100, 80))

            # 小丑八音盒倒计时自爆
            if zombie.ztype == "jackbox":
                zombie.jackbox_timer = getattr(zombie, "jackbox_timer", 7.0) - dt
                if zombie.jackbox_timer <= 0:
                    zombie.hp = 0
                    zombie.dead = True
                    self.burst(zombie.x, zombie.y, (255, 80, 50), 30)
                    self.audio.play("cherrybomb")
                    self.float_text(zombie.x, zombie.y - 40, "八音盒自爆！", (255, 60, 40))
                    for p_item in self.plants:
                        if p_item.alive and abs(p_item.x - zombie.x) <= CELL_W * 1.5 and abs(p_item.row - zombie.row) <= 1:
                            p_item.alive = False
                    continue

            # 矿工遁地潜行破土
            if zombie.ztype == "digger":
                if not getattr(zombie, "emerged", False):
                    zombie.digging = True
                    zombie.x -= zombie.speed * dt
                    if zombie.x <= GRID_X + 25:
                        zombie.emerged = True
                        zombie.digging = False
                        zombie.speed = -abs(zombie.speed)
                        self.float_text(zombie.x, zombie.y - 40, "破土而出！", (180, 130, 80))
                        self.burst(zombie.x, zombie.y, (140, 90, 40), 20)
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
                    dmg = 1500.0 if zombie.ztype == "gargantuar" else (zombie.damage * (1.5 if zombie.enraged else 1.0))
                    plant.hp -= dmg
                    if zombie.ztype == "gargantuar":
                        self.burst(plant.x, plant.y, (140, 180, 80), 16)
                        self.audio.play("squash")
                    plant.flash = 0.18
                    self.burst(plant.x, plant.y, (120, 185, 75), 2)

                    # 魅惑菇：啃食即刻被魅惑倒戈
                    if plant.ptype == "hypnoshroom":
                        plant.alive = False
                        zombie.eating = 0.0
                        setattr(zombie, "hypnotized", True)
                        zombie.speed = -abs(zombie.speed) # 调头倒戈！
                        self.burst(plant.x, plant.y, (255, 120, 220), 16)
                        self.float_text(zombie.x, zombie.y - 25, "已被魅惑！", (255, 120, 220))
                        self.audio.play("groan")

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
                # 魅惑僵尸为玩家反向作战
                if getattr(zombie, "hypnotized", False):
                    for ez in self.zombies:
                        if not ez.dead and not getattr(ez, "hypnotized", False) and ez.row == zombie.row:
                            if abs(ez.x - zombie.x) < 32:
                                self._damage_zombie(ez, 60.0 * dt)
                                break
                    if zombie.x > WIDTH + 80:
                        zombie.dead = True
                        continue
                elif zombie.x < MOWER_X - 6:
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
            if hasattr(projectile, "vx") and hasattr(projectile, "vy"):
                projectile.x += getattr(projectile, "vx") * dt
                projectile.y += getattr(projectile, "vy") * dt
                if projectile.x < -60 or projectile.x > WIDTH + 60 or projectile.y < -60 or projectile.y > HEIGHT + 60:
                    projectile.alive = False
                    continue
            else:
                projectile.update(dt)

            # 大喷菇穿透气雾判定
            if projectile.bullet_type == "fume":
                hit_set = getattr(projectile, "hit_set", set())
                setattr(projectile, "hit_set", hit_set)
                for ez in self.zombies:
                    if not ez.dead and ez.row == projectile.row and abs(ez.x - projectile.x) < 38 and id(ez) not in hit_set:
                        hit_set.add(id(ez))
                        self._damage_zombie(ez, projectile.damage)
                        self.burst(ez.x, ez.y - 15, (210, 110, 230), 4)
                if projectile.x > old_x + 420 or projectile.x > WIDTH:
                    projectile.alive = False
                continue

            # 杨桃金星碰撞判定
            if projectile.bullet_type == "star":
                for ez in self.zombies:
                    if not ez.dead and math.hypot(ez.x - projectile.x, (lane_ground(ez.row, cell_h=self.cell_h) - 40) - projectile.y) < 32:
                        projectile.alive = False
                        self._damage_zombie(ez, projectile.damage)
                        self.burst(projectile.x, projectile.y, (255, 235, 90), 8)
                        break
                if not projectile.alive:
                    continue

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

                    if main_target and getattr(main_target, "ztype", "") == "balloon" and getattr(main_target, "flying", True):
                        main_target.flying = False
                        self.float_text(main_target.x, main_target.y - 35, "气球击破！", (255, 80, 80))
                        self.burst(main_target.x, main_target.y - 20, (255, 60, 60), 16)

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
                    elif projectile.bullet_type == "cob_missile":
                        self.burst(impact_x, impact_y, (255, 215, 60), 36)
                        self.burst(impact_x, impact_y, (255, 120, 40), 24)
                        self.audio.play("cherrybomb")
                        self.float_text(impact_x, impact_y - 45, "核弹轰炸！", (255, 215, 60))
                        for z in self.zombies:
                            if not z.dead:
                                if abs(z.row - projectile.row) <= 1 and abs(z.x - impact_x) <= 150:
                                    self._damage_zombie(z, 1800.0)
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

                # 浮空气球僵尸免疫普通水平直射豌豆
                if getattr(zombie, "ztype", "") == "balloon" and getattr(zombie, "flying", True):
                    if projectile.bullet_type in ("pea", "fire_pea", "snowpea"):
                        continue
                    else:
                        zombie.flying = False
                        self.float_text(zombie.x, zombie.y - 35, "气球击破！", (255, 80, 80))
                        self.burst(zombie.x, zombie.y - 20, (255, 60, 60), 16)

                # 矿工遁地潜行免疫正面子弹
                if getattr(zombie, "ztype", "") == "digger" and getattr(zombie, "digging", False):
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

    def _spawn_natural_sun(self, dt: float) -> None:
        level = LEVELS[self.level_index]
        is_night = level["theme"] == "night"
        self.natural_sun_timer -= dt
        if self.natural_sun_timer <= 0:
            if is_night:
                self.natural_sun_timer = random.uniform(14.0, 18.0)
                x = random.randint(GRID_X + 20, GRID_RIGHT - 20)
                target = random.randint(GRID_Y + 40, GRID_BOTTOM - 40)
                self.suns.append(SunToken(x, -30, target, value=25))
            else:
                self.natural_sun_timer = random.uniform(6.5, 9.5)
                x = random.randint(GRID_X + 20, GRID_RIGHT - 20)
                target = random.randint(GRID_Y + 40, GRID_BOTTOM - 40)
                self.suns.append(SunToken(x, -30, target))

    def _update_waves(self) -> None:
        if not self.waves:
            return
        if self.current_wave_index < 0:
            if self.elapsed >= self.next_wave_at:
                self._start_next_wave()
            return

        now = self.elapsed
        spawned_any = False
        remaining_spawns: list[tuple[float, int, WaveMember]] = []
        for spawn_time, wave_id, member in self.pending_wave_spawns:
            if now >= spawn_time:
                self._spawn_wave_member(wave_id, member)
                spawned_any = True
            else:
                remaining_spawns.append((spawn_time, wave_id, member))
        self.pending_wave_spawns = remaining_spawns

        if self.current_wave_index < len(self.waves) - 1:
            current_wave = self.waves[self.current_wave_index]
            hp_ratio = self._wave_hp_ratio(self.current_wave_index)
            advance_by_hp = hp_ratio <= current_wave.advance_ratio
            advance_by_timer = now >= self.next_wave_at
            if (advance_by_hp or advance_by_timer) and not self.pending_wave_spawns:
                self._start_next_wave()
        elif getattr(LEVELS[self.level_index], "get", lambda k: False)("endless"):
            # 无尽模式：持续动态扩增新波次
            if not self.pending_wave_spawns and not any(not z.dead for z in self.zombies):
                self._spawn_endless_wave()

    def _spawn_endless_wave(self) -> None:
        self.endless_wave_record += 1
        wave_idx = len(self.waves)
        rng = random.Random(9999 + wave_idx * 43)
        count = min(35, 12 + wave_idx * 2)
        members: list[WaveMember] = []
        delay = 0.0
        types = list(ZOMBIES)
        for _ in range(count):
            ztype = rng.choice(types)
            lane = rng.randrange(ROWS)
            members.append(WaveMember(delay, ztype, lane))
            delay += rng.uniform(0.25, 0.45)
        total_hp = sum(float(ZOMBIES[m.ztype]["hp"]) for m in members)
        new_wave = Wave(wave_idx, members, total_hp, 0.65, 25.0)
        self.waves.append(new_wave)
        self.current_wave_index = wave_idx
        self.total_zombies += count
        for m in members:
            self.pending_wave_spawns.append((self.elapsed + m.delay, wave_idx, m))
        self._show_banner(f"无尽浪潮 · 第 {self.endless_wave_record} 轮", warm=True)
        self.wave_flash = 0.8
        self.sun += 150
        record_win(self.level_index, self.endless_wave_record)

    def _start_next_wave(self) -> None:
        next_index = self.current_wave_index + 1
        if next_index >= len(self.waves):
            return
        self.current_wave_index = next_index
        wave = self.waves[next_index]
        self.wave_started_at = self.elapsed
        for member in wave.members:
            self.pending_wave_spawns.append(
                (self.elapsed + member.delay, next_index, member)
            )
        self.next_wave_at = self.elapsed + wave.fallback_gap

        if next_index == 0:
            self._show_banner("第一波僵尸来袭", warm=True)
            self.wave_flash = 0.55
        elif next_index == len(self.waves) - 1:
            self._show_banner("最后一波僵尸来袭", warm=True)
            self.wave_flash = 0.9
        else:
            self._show_banner(f"第 {next_index + 1} 波僵尸来袭", warm=True)
            self.wave_flash = 0.65

    def _spawn_wave_member(self, wave_id: int, member: WaveMember) -> None:
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
        self.spawned_count += 1

    def _wave_hp_ratio(self, wave_index: int) -> float:
        wave = self.waves[wave_index]
        if wave.total_hp <= 0:
            return 0.0
        remaining = sum(
            max(0.0, zombie.hp)
            for zombie in self.zombies
            if zombie.wave_id == wave_index and not zombie.dead
        )
        remaining += sum(
            float(ZOMBIES[member.ztype]["hp"])
            for _, wave_id, member in self.pending_wave_spawns
            if wave_id == wave_index
        )
        return remaining / wave.total_hp

    def _show_banner(self, message: str, warm: bool = False) -> None:
        self.banner = message
        self.banner_timer = 2.4
        self.banner_warm = warm

    def _update_mowers(self) -> None:
        for zombie in self.zombies:
            if not zombie.dead and zombie.x <= MOWER_X + 18 and not self.mowers[zombie.row].spent:
                mower = self.mowers[zombie.row]
                if not mower.triggered:
                    mower.triggered = True
                    self.audio.play("mower")

    def kill_zombie(self, zombie: Zombie, mower: bool = False) -> None:
        if zombie.dead:
            return
        zombie.dead = True
        zombie.death_timer = 0.0
        color = (130, 160, 120) if not mower else (210, 60, 50)
        self.burst(zombie.x, lane_ground(zombie.row) - 60, color, 14 if not mower else 26)

    def _explode_radius(
        self,
        cx: float,
        cy: float,
        radius: float,
        damage: float,
        burst_color: tuple[int, int, int],
    ) -> None:
        self.audio.play("explode")
        for zombie in self.zombies:
            if zombie.dead:
                continue
            zx = zombie.x
            zy = lane_ground(zombie.row) - 50
            if (zx - cx) ** 2 + (zy - cy) ** 2 <= radius ** 2:
                zombie.hp -= damage
                if zombie.hp <= 0:
                    self.kill_zombie(zombie)
        self.burst(cx, cy, burst_color, 45, speed=220)
        self.burst(cx, cy, (255, 230, 110), 25, speed=160)

    def _burn_lane(self, row: int) -> None:
        self.audio.play("explode")
        y = lane_ground(row) - 50
        for zombie in self.zombies:
            if zombie.row == row and not zombie.dead:
                zombie.hp = 0
                self.kill_zombie(zombie)
        for x in range(GRID_X, GRID_RIGHT, 48):
            self.burst(x, y, (255, 82, 45), 6, upward=True, speed=180)
            self.burst(x + 12, y + 10, (255, 214, 72), 4, upward=True, speed=140)

    def _remove_dead(self) -> None:
        self.plants = [p for p in self.plants if p.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]
        self.zombies = [z for z in self.zombies if not z.dead or z.death_timer < 0.7]

    def _check_progress(self) -> None:
        if self.overlay:
            return
        if getattr(LEVELS[self.level_index], "get", lambda k: False)("endless"):
            return
        if (
            self.waves
            and self.current_wave_index >= len(self.waves) - 1
            and not self.pending_wave_spawns
            and not any(not zombie.dead for zombie in self.zombies)
        ):
            self.overlay = "won"
            self.overlay_age = 0
            self.audio.stop_music()
            self.audio.play("win")
            record_win(self.level_index)
            for _ in range(32):
                self.burst(
                    random.randint(GRID_X + 100, GRID_RIGHT - 100),
                    random.randint(GRID_Y + 80, GRID_BOTTOM - 80),
                    random.choice([(255, 212, 68), (108, 199, 90), (255, 243, 191)]),
                    2,
                    upward=True,
                    speed=130,
                )

    def draw(self) -> None:
        self.screen.fill(C_BG)
        if self.mode == "menu":
            self._draw_menu()
            return
        elif self.mode == "seed_select":
            self._draw_seed_select()
            return
        self._draw_game_background()
        self._draw_entities()
        self._draw_hud()
        self._draw_overlays()
        self._draw_mouse()

    def _background(self, theme: str) -> pygame.Surface:
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
        return surface

    def _draw_house_edge(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (78, 59, 44), (0, GRID_Y - 14, GRID_X, ROWS * CELL_H + 28))
        pygame.draw.rect(surface, (114, 88, 64), (0, GRID_Y - 14, GRID_X - 12, ROWS * CELL_H + 28))
        for row in range(ROWS):
            y = GRID_Y + row * CELL_H
            pygame.draw.rect(surface, (91, 70, 52), (GRID_X - 18, y + 8, 12, CELL_H - 16), border_radius=3)
            pygame.draw.line(surface, (54, 40, 30), (0, y), (GRID_X, y), 2)

    def _draw_right_garden(self, surface: pygame.Surface, theme: str) -> None:
        fence_color = (196, 189, 162) if theme != "night" else (120, 130, 125)
        shadow = (42, 68, 48)
        for x in range(GRID_RIGHT + 8, WIDTH + 20, 26):
            pygame.draw.polygon(
                surface, shadow,
                [(x - 2, GRID_Y - 8), (x + 10, GRID_Y - 18), (x + 22, GRID_Y - 8), (x + 22, GRID_BOTTOM + 8), (x - 2, GRID_BOTTOM + 8)],
            )
            pygame.draw.polygon(
                surface, fence_color,
                [(x, GRID_Y - 10), (x + 10, GRID_Y - 20), (x + 20, GRID_Y - 10), (x + 20, GRID_BOTTOM + 6), (x, GRID_BOTTOM + 6)],
            )
        pygame.draw.line(surface, fence_color, (GRID_RIGHT + 2, GRID_Y + 50), (WIDTH, GRID_Y + 50), 6)
        pygame.draw.line(surface, fence_color, (GRID_RIGHT + 2, GRID_BOTTOM - 60), (WIDTH, GRID_BOTTOM - 60), 6)

    def _draw_menu(self) -> None:
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
                text(self.screen, "[已通关]", self.fonts.get(12, True), (195, 130, 20), (rect.x + 8, rect.y + 54))
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
                text(self.screen, "[已通关]", self.fonts.get(12, True), (195, 130, 20), (rect.x + 8, rect.y + 54))
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
        text(self.screen, "【无尽挑战】第 16 关 · 水陆无尽大挑战 (ENDLESS POOL)", self.fonts.get(20, True), (255, 235, 140), (endless_rect.x + 24, endless_rect.y + 10))
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

    def _draw_seed_select(self) -> None:
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
        bank_rect = pygame.Rect(230, 12, 740, 84)
        panel(self.screen, bank_rect, (82, 54, 30), (45, 28, 14), radius=10, width=3, shadow=True)

        text(self.screen, "出战卡槽", self.fonts.get(17, True), (255, 235, 140), (bank_rect.x - 16, bank_rect.y + 16), "topright", (40, 30, 20))
        text(self.screen, f"{len(self.selected_seeds)}/{self.slot_capacity} (点击下阵)", self.fonts.get(12), (210, 210, 190), (bank_rect.x - 16, bank_rect.y + 44), "topright")

        slot_w = 66
        slot_h = 70
        slot_gap = 6
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
            "点击植物卡牌加入出战槽，至多选择 9 种；快捷键: [R] 智能推荐  [C] 清空卡槽  [Enter] 确认开打",
            self.fonts.get(12), (120, 92, 55), (cat_rect.centerx, cat_rect.y + 34), "midtop",
        )
        pygame.draw.line(self.screen, (185, 160, 125), (cat_rect.x + 24, cat_rect.y + 54), (cat_rect.right - 24, cat_rect.y + 54), 2)

        # 34 Plants Catalog Grid (9 cols x 4 rows)
        unlocked = set(self.available_plants())
        cw = 88
        ch = 72
        gap_x = 8
        gap_y = 6
        gx0 = cat_rect.x + (cat_rect.width - (9 * cw + 8 * gap_x)) // 2
        gy0 = cat_rect.y + 60

        self.catalog_rects = {}
        hovered_plant = None
        for idx, name in enumerate(UNLOCK_ORDER):
            col = idx % 9
            row = idx // 9
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

    def _cloud(self, x: float, y: float, scale: float) -> None:
        color = (242, 246, 214)
        pygame.draw.ellipse(self.screen, color, (x, y, 126 * scale, 42 * scale))
        pygame.draw.circle(self.screen, color, (x + 35 * scale, y + 12 * scale), 29 * scale)
        pygame.draw.circle(self.screen, color, (x + 76 * scale, y + 5 * scale), 35 * scale)
        pygame.draw.circle(self.screen, color, (x + 107 * scale, y + 18 * scale), 25 * scale)

    def _draw_game_background(self) -> None:
        self.screen.blit(self._background(LEVELS[self.level_index]["theme"]), (0, 0))

    def _draw_entities(self) -> None:
        for mower in self.mowers:
            is_pool_mower = getattr(self, "is_pool", False) and mower.row in getattr(self, "pool_rows", [])
            draw_mower(self.screen, mower, is_pool=is_pool_mower, cell_h=self.cell_h)
        for plant in sorted(self.plants, key=lambda p: (p.row, 0 if p.ptype == 'lilypad' else 1, p.y)):
            if not plant.alive:
                continue
            # 水面荷叶保障：水面陆生植物必须且必然站在睡莲上
            if getattr(self, "is_pool", False) and plant.row in getattr(self, "pool_rows", ()):
                if plant.ptype not in ("lilypad", "cattail"):
                    has_lily = any(p.alive and p.col == plant.col and p.row == plant.row and p.ptype == "lilypad" for p in self.plants)
                    if not has_lily:
                        draw_plant(self.screen, "lilypad", (plant.x, plant.y), 0.92, self.ambient, 1.0, 10.0)
            draw_plant(
                self.screen, plant.ptype, (plant.x, plant.y), 0.92,
                self.ambient, max(0.0, plant.hp / plant.max_hp), plant.age,
                plant=plant,
            )
            if plant.flash > 0:
                overlay = pygame.Surface((76, 90), pygame.SRCALPHA)
                overlay.fill((255, 85, 72, int(80 * plant.flash / 0.18)))
                self.screen.blit(overlay, (plant.x - 38, plant.y - 45))
        for zombie in sorted(self.zombies, key=lambda z: (z.row, z.x)):
            if zombie.dead:
                fall = min(1.0, zombie.death_timer / 0.5)
                alpha = int(220 * (1.0 - fall))
                draw_zombie(self.screen, zombie, self.time_value, alpha=alpha, dy_offset=fall * 12, cell_h=self.cell_h)
            else:
                draw_zombie(self.screen, zombie, self.time_value, cell_h=self.cell_h)
        for projectile in self.projectiles:
            bullet_surf = pvz_graphics.get_bullet_surface(projectile.freeze, 22, bullet_type=projectile.bullet_type)
            if bullet_surf:
                if projectile.freeze:
                    draw_glow_circle(self.screen, (projectile.x, projectile.y), 7, (125, 225, 246))
                self.screen.blit(bullet_surf, bullet_surf.get_rect(center=(projectile.x, projectile.y)))
            else:
                if projectile.freeze:
                    draw_glow_circle(self.screen, (projectile.x, projectile.y), 8, (125, 225, 246))
                    color, highlight = C_BLUE, (220, 252, 255)
                elif projectile.bullet_type == "mushroom":
                    color, highlight = (165, 75, 175), (235, 185, 245)
                else:
                    color, highlight = (115, 196, 70), (205, 239, 143)
                pygame.draw.circle(self.screen, (41, 101, 49), (projectile.x, projectile.y), 9)
                pygame.draw.circle(self.screen, color, (projectile.x - 1, projectile.y - 1), 7)
                pygame.draw.circle(self.screen, highlight, (projectile.x - 3, projectile.y - 3), 2.5)

        for token in self.suns:
            draw_sun_shape(self.screen, token.center(), 20, token.age * 1.2)
        for particle in self.particles:
            alpha = int(255 * clamp(particle.life / particle.max_life, 0, 1))
            dims = max(3, int(particle.size * 3))
            key = (particle.color, dims)
            sprite = _PARTICLE_CACHE.get(key)
            if sprite is None:
                sprite = pygame.Surface((dims, dims), pygame.SRCALPHA)
                pygame.draw.circle(
                    sprite, (*particle.color, 255),
                    (dims // 2, dims // 2), max(1, int(particle.size)),
                )
                _PARTICLE_CACHE[key] = sprite
            sprite.set_alpha(alpha)
            self.screen.blit(sprite, (particle.x - dims / 2, particle.y - dims / 2))
        for item in self.floating_texts:
            alpha = int(255 * clamp(item.life / item.max_life, 0, 1))
            image = item.image
            if image is None:
                image = self.fonts.get(19, True).render(item.value, True, item.color)
                item.image = image
            image.set_alpha(alpha)
            rect = image.get_rect(center=(item.x, item.y))
            self.screen.blit(image, rect)

        if self.selected_plant:
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
                    self.screen.blit(ghost, rect)

    def _draw_hud(self) -> None:
        hud = pygame.Rect(0, 0, WIDTH, HUD_H)
        pygame.draw.rect(self.screen, (50, 102, 53), hud)
        pygame.draw.rect(self.screen, (27, 58, 35), (0, HUD_H - 5, WIDTH, 5))
        for x in range(0, WIDTH, 28):
            pygame.draw.line(self.screen, (58, 118, 58), (x, 8), (x + 18, HUD_H - 10), 1)

        sun_rect = pygame.Rect(12, 12, 126, 76)
        panel(self.screen, sun_rect, (238, 224, 163), (67, 79, 45), radius=10, width=2)
        draw_sun_shape(self.screen, (48, 50), 23, self.time_value, glow=True)
        text(self.screen, str(self.sun), self.fonts.get(31, True), (51, 65, 42), (77, 24))
        text(self.screen, "阳光 [C吸附]", self.fonts.get(12, True), (115, 104, 68), (78, 62))

        self.seed_rects = {}
        deck = self.selected_seeds if self.selected_seeds else self.available_plants()[:self.slot_capacity]
        x = 146
        card_w = 72
        gap = 4
        for i, name in enumerate(deck):
            rect = pygame.Rect(x + i * (card_w + gap), 12, card_w, 76)
            self.seed_rects[name] = rect
            config = PLANTS[name]
            ready = self.cooldowns[name] <= 0 and self.sun >= config["cost"]
            selected = self.selected_plant == name
            hover = rect.collidepoint(pygame.mouse.get_pos())
            card_img = pvz_graphics.get_card_surface(name, (card_w, 76))
            if card_img:
                self.screen.blit(card_img, rect)
                if selected or hover:
                    pygame.draw.rect(self.screen, C_GOLD, rect, 3 if selected else 2, border_radius=6)
                if self.cooldowns[name] > 0:
                    ratio = self.cooldowns[name] / config["cooldown"]
                    shade_h = int(rect.height * ratio)
                    shade = pygame.Surface((rect.width, shade_h), pygame.SRCALPHA)
                    shade.fill((20, 20, 20, 180))
                    self.screen.blit(shade, (rect.x, rect.y + rect.height - shade_h))
                elif not ready:
                    shade = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    shade.fill((30, 30, 30, 120))
                    self.screen.blit(shade, rect)
            else:
                fill = (247, 235, 184) if ready else (194, 200, 163)
                outline = C_GOLD if selected or hover else (66, 75, 44)
                panel(self.screen, rect, fill, outline, radius=8, width=4 if selected else 2, shadow=False)
                draw_plant(self.screen, name, (rect.centerx - 4, rect.y + 32), 0.30, self.time_value)
                text(self.screen, config["name"], self.fonts.get(12, True), (58, 60, 42), (rect.centerx, rect.y + 49), "midtop")
                sun_badge = pygame.Rect(rect.centerx - 18, rect.y + 66, 36, 17)
                pygame.draw.rect(self.screen, (54, 75, 44), sun_badge, border_radius=5)
                text(
                    self.screen, str(config["cost"]), self.fonts.get(11, True),
                    C_SUN if self.sun >= config["cost"] else (241, 127, 106),
                    sun_badge.center, "center",
                )
                if self.cooldowns[name] > 0:
                    ratio = self.cooldowns[name] / config["cooldown"]
                    shade_h = int(rect.height * ratio)
                    shade = pygame.Surface((rect.width, shade_h), pygame.SRCALPHA)
                    shade.fill((31, 45, 39, 155))
                    self.screen.blit(shade, (rect.x, rect.y + rect.height - shade_h))
                if not ready and self.cooldowns[name] <= 0:
                    shade = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    shade.fill((51, 47, 39, 85))
                    self.screen.blit(shade, rect)

            # Hotkey badge on top-left of each HUD card: [1] ~ [8]
            hk_rect = pygame.Rect(rect.x + 3, rect.y + 3, 16, 16)
            pygame.draw.rect(self.screen, (20, 28, 22, 210), hk_rect, border_radius=4)
            pygame.draw.rect(self.screen, (90, 120, 95), hk_rect, 1, border_radius=4)
            text(self.screen, str(i + 1), self.fonts.get(10, True), C_CREAM, hk_rect.center, "center")

        level = LEVELS[self.level_index]
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
        self._small_control(self.skip_rect, "跳关", highlight=True)

        bar = pygame.Rect(84, 728, 1004, 21)
        pygame.draw.rect(self.screen, (37, 59, 43), bar, border_radius=8)
        progress = self.spawned_count / max(1, self.total_zombies)
        fill = bar.inflate(-4, -4)
        fill.width = int(fill.width * clamp(progress, 0, 1))
        if fill.width > 0:
            pygame.draw.rect(self.screen, (135, 192, 82), fill, border_radius=6)
        wave_count = max(1, len(self.waves))
        for i in range(1, wave_count):
            gx = bar.x + bar.width * i / wave_count
            pygame.draw.line(self.screen, (213, 216, 183), (gx, bar.y - 4), (gx, bar.bottom + 3), 2)
            pygame.draw.polygon(
                self.screen,
                (255, 210, 95) if self.current_wave_index >= i - 1 else (104, 111, 91),
                [(gx + 1, bar.y - 8), (gx + 16, bar.y - 4), (gx + 16, bar.y + 4), (gx + 1, bar.y + 8)],
            )
        if self.current_wave_index < 0:
            wave_status = f"首波倒计时 {math.ceil(max(0.0, self.next_wave_at - self.elapsed))}s"
        else:
            wave_status = f"波次 {self.current_wave_index + 1}/{wave_count}"
        text(
            self.screen, f"{wave_status} · 僵尸 {self.spawned_count}/{self.total_zombies} · [{self.game_speed:0.0f}x速]",
            self.fonts.get(13, True), (231, 238, 202), (bar.right, bar.y - 17), "topright",
        )

        if self.banner_timer > 0 and self.banner:
            self._draw_banner()
        if self.wave_flash > 0:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 224, 166, int(45 * self.wave_flash)))
            self.screen.blit(flash, (0, 0))

    def _small_control(self, rect: pygame.Rect, title: str, active: bool = False, highlight: bool = False) -> None:
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
            text(self.screen, title, self.fonts.get(13, True), text_c, rect.center, "center")

    def _draw_banner(self) -> None:
        alpha = clamp(self.banner_timer * 1.5, 0, 1)
        width = 460
        height = 68
        rect = pygame.Rect((WIDTH - width) // 2, 230, width, height)
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        fill = (148, 48, 44, int(220 * alpha)) if self.banner_warm else (43, 85, 52, int(220 * alpha))
        pygame.draw.rect(surface, fill, surface.get_rect(), border_radius=14)
        pygame.draw.rect(
            surface, (255, 224, 137, int(255 * alpha)), surface.get_rect(), 3, border_radius=14
        )
        self.screen.blit(surface, rect)
        text(self.screen, self.banner, self.fonts.get(25, True), C_CREAM, (600, 264), "center", (25, 30, 24))

    def _draw_overlays(self) -> None:
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
                text(self.screen, f"【荣获通关神器】{art_name}", self.fonts.get(18, True), (180, 95, 10), (600, 322), "center")
                text(self.screen, art_desc or "", self.fonts.get(12), (80, 60, 40), (600, 350), "center")
            
            if new_plants:
                p_names = "、".join(PLANTS.get(p, {}).get("name", p) for p in new_plants)
                text(self.screen, f"【解锁全新植物】{p_names}", self.fonts.get(16, True), (42, 115, 48), (600, 385 if art_name else 335), "center")
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
            text(self.screen, label, self.fonts.get(20, True), C_CREAM, rect.center, "center")

    def _draw_mouse(self) -> None:
        if self.shovel_selected:
            x, y = pygame.mouse.get_pos()
            pygame.draw.line(self.screen, (115, 85, 58), (x - 6, y - 6), (x - 24, y - 24), 6)
            pygame.draw.polygon(
                self.screen, (194, 207, 194),
                [(x + 3, y + 4), (x + 20, y + 16), (x + 13, y + 25), (x - 4, y + 13)],
            )

    def setup_preview(self, level_index: int) -> None:
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
            # 泳池 6 行豪华演示阵容：顶栏卡槽与场上植物严格一一对应！
            self.selected_seeds = [
                "sunflower", "lilypad", "cattail", "cabbagepult",
                "kernelpult", "torchwood", "garlic", "melonpult", "wallnut"
            ]
            demo_plants = [
                ("sunflower", 0, 0), ("sunflower", 0, 1),
                ("lilypad", 0, 2), ("cattail", 0, 2),
                ("lilypad", 0, 3), ("cattail", 0, 3),
                ("sunflower", 0, 4), ("sunflower", 0, 5),
                ("cabbagepult", 1, 0), ("torchwood", 3, 0), ("wallnut", 5, 0),
                ("melonpult", 1, 1), ("garlic", 4, 1),
                ("lilypad", 1, 2), ("kernelpult", 1, 2),
                # 水面第 4 列坚果严格种在荷叶（睡莲）上！
                ("lilypad", 4, 3), ("wallnut", 4, 3),
                ("kernelpult", 1, 4), ("torchwood", 3, 4), ("garlic", 4, 4),
                ("cabbagepult", 1, 5), ("wallnut", 5, 5),
            ]
            self.plants = []
            for name, col, row in demo_plants:
                p = Plant(name, col, row, PLANTS[name]["hp"], PLANTS[name]["hp"], age=8.0, cell_h=self.cell_h)
                self.plants.append(p)

            # 水路僵尸严格在水域内 (x <= 810) 悠游与飞跃，绝对禁止在陆地上！
            demo_zombies = [
                ("basic", 0, 1020), ("cone", 0, 1140),
                ("bucket", 1, 880), ("pole", 1, 1090),
                ("ducky", 2, 680), ("snorkel", 2, 790),
                ("dolphin", 3, 720), ("ducky", 3, 810),
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="植物大战僵尸风格 pygame 豪华版原型")
    parser.add_argument("--level", type=int, default=None, help="直接启动指定关卡（1-16）")
    parser.add_argument("--smoke-test", action="store_true", help="无窗口冒烟测试")
    parser.add_argument("--screenshot", type=str, default="", help="保存游戏内预览图")
    parser.add_argument("--preview", action="store_true", help="填充演示场景后截图")
    parser.add_argument("--seed-select", action="store_true", help="进入选卡界面截图测试")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    headless = args.smoke_test or bool(args.screenshot)
    if headless:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    pygame.init()
    pygame.display.set_caption("植物大战僵尸 · 豪华增强版 · pygame")
    flags = 0
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    game = Game(screen, headless=headless)

    if args.seed_select:
        level = max(0, min(len(LEVELS) - 1, (args.level or 10) - 1))
        game.start_level(level)
        game.mode = "seed_select"
        for _ in range(15):
            game.time_value += 1 / FPS
            game.draw()
        pygame.display.flip()
        if args.screenshot:
            screenshot_path = Path(args.screenshot).expanduser().resolve()
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            pygame.image.save(screen, str(screenshot_path))
            print(f"SEED_SELECT_SAVED {screenshot_path}")
        pygame.quit()
        return 0

    if args.smoke_test:
        level = max(0, min(len(LEVELS) - 1, (args.level or 7) - 1))
        game.setup_preview(level)
        for _ in range(90):
            game.time_value += 1 / FPS
            game.update(1 / FPS)
        game.banner_timer = 0
        game.wave_flash = 0
        game.draw()
        pygame.display.flip()
        if args.screenshot:
            screenshot_path = Path(args.screenshot).expanduser().resolve()
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            pygame.image.save(screen, str(screenshot_path))
            print(f"SMOKE_OK screenshot={screenshot_path}")
        else:
            print(
                "SMOKE_OK "
                f"level={level + 1} plants={len(game.plants)} "
                f"zombies={len(game.zombies)} particles={len(game.particles)}"
            )
        pygame.quit()
        return 0

    if args.preview:
        level = max(0, min(len(LEVELS) - 1, (args.level or 7) - 1))
        game.setup_preview(level)
        for _ in range(45):
            game.time_value += 1 / FPS
            game.draw()
        pygame.display.flip()
        if args.screenshot:
            screenshot_path = Path(args.screenshot).expanduser().resolve()
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            pygame.image.save(screen, str(screenshot_path))
            print(f"PREVIEW_SAVED {screenshot_path}")
        pygame.time.wait(800)
        pygame.quit()
        return 0

    if args.level:
        game.start_level(max(0, min(len(LEVELS) - 1, args.level - 1)))
    game.begin_loop()
    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
