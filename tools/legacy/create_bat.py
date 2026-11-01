# -*- coding: utf-8 -*-
from pathlib import Path

bat_content = """@chcp 936 >nul
@echo off
title 植物大战僵尸 - 全功能豪华版
cd /d "%~dp0"
echo ========================================================
echo        植物大战僵尸 · 全功能豪华版 (Pygame)
echo ========================================================
echo [信息] 正在启动游戏引擎...
echo [提示] 按 1-8 快捷选卡，按 空格/F 切换倍速，按 C 吸附阳光
echo [提示] 通关第 5 关解锁【黄金阳光铲】，全额返还阳光！
echo ========================================================
python pvz_ten_levels.py
if errorlevel 1 (
    echo.
    echo [错误] 游戏异常退出，请检查 Python 环境及依赖组件。
    pause
)
"""

bat_path = Path("10-pvz/运行植物大战僵尸.bat")
# 转换为 CRLF + GBK (CP936)
crlf_content = bat_content.replace("\r\n", "\n").replace("\n", "\r\n")
bat_path.write_bytes(crlf_content.encode("gbk"))
print("BAT_WRITTEN_IN_GBK")
