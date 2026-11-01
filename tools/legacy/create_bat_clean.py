# -*- coding: utf-8 -*-
from pathlib import Path

lines = [
    "@chcp 936 >nul",
    "@echo off",
    "title 植物大战僵尸 - 全功能豪华版",
    r'cd /d "F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz"',
    "echo ========================================================",
    "echo        植物大战僵尸 · 全功能豪华版 (Pygame)",
    "echo ========================================================",
    "echo [信息] 正在启动游戏引擎...",
    "echo [提示] 按 1-9 快捷选卡，按 空格/F 切换倍速，按 C 吸附阳光",
    "echo [提示] 通关第 5 关解锁【黄金阳光铲】（100%%全额返还阳光）！",
    "echo [提示] 每关拥有 9 格出战卡槽，第 15 关腰带可扩至 10 格！",
    "echo ========================================================",
    "python pvz_ten_levels.py",
    "if errorlevel 1 (",
    "    echo.",
    "    echo [错误] 游戏异常退出，请检查 Python 环境及依赖组件。",
    "    pause",
    ")",
    "",
]

bat_raw = "\r\n".join(lines).encode("gbk")

p1 = Path(r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\运行植物大战僵尸.bat")
p1.write_bytes(bat_raw)

p2 = Path(r"F:\Desktop\.DeskBox\文件夹\反重力产出\脚本\启动植物大战僵尸.bat")
p2.write_bytes(bat_raw)

print("BAT_SCRIPTS_WRITTEN_IN_GBK")
