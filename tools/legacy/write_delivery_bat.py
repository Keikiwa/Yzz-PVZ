# -*- coding: utf-8 -*-
from pathlib import Path

bat_content = """@chcp 936 >nul
@echo off
title 植物大战僵尸 · 豪华增强版 (34种植物+15种僵尸+时空任意跳关)
echo =======================================================================
echo          植物大战僵尸 · 豪华增强版 (PVZ DELUXE EXPANSION)
echo =======================================================================
echo.
echo  【新功能亮点】
echo   1. 彻底根除右上角乱码重影：单行精致对齐 [1x速][暂停][铲子][音效][跳关]
echo   2. 任意跳关系统实装：点击 [跳关] 按钮或按快捷键随时任意跳关！
echo      - [Tab] / [N] ：秒跳下一关
echo      - [P]         ：返回上一关
echo      - [L]         ：呼出 / 关闭【时空穿梭·任意跳关传送门】（16关直达）
echo   3. 跳关战力无缝继承：跳至对应关卡自动配齐前序战利品植物与神器！
echo   4. 34 种植物阵容（玉米加农炮、魔术菇、龙舌兰、激光豆全量出战）
echo   5. 15 种僵尸兵团（巨人僵尸砸击抛鬼、气球浮空、小丑自爆、矿工遁地）
echo.
echo 正在启动游戏引擎，请稍候...
echo =======================================================================

cd /d "F:\\Desktop\\.DeskBox\\文件夹\\项目与开发\\小游戏开发\\10-pvz"
python pvz_ten_levels.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] 游戏退出异常，错误码：%ERRORLEVEL%
    pause
)
"""

crlf_content = bat_content.replace("\r\n", "\n").replace("\n", "\r\n")
gbk_bytes = crlf_content.encode("cp936")

# 1. 写入反重力产出目录
p_deskbox = Path(r"F:\Desktop\.DeskBox\文件夹\反重力产出\脚本\启动植物大战僵尸.bat")
p_deskbox.write_bytes(gbk_bytes)
print(f"Written GBK BAT to {p_deskbox}")

# 2. 写入工程目录
p_proj = Path(r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\启动植物大战僵尸.bat")
p_proj.write_bytes(gbk_bytes)
print(f"Written GBK BAT to {p_proj}")
