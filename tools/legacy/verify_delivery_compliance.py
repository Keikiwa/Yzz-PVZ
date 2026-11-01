# -*- coding: utf-8 -*-
import os, sys

def check_encoding():
    bat_path = r"F:\Desktop\.DeskBox\文件夹\反重力产出\脚本\启动植物大战僵尸.bat"
    with open(bat_path, "rb") as f:
        bat_bytes = f.read()
    assert b"@chcp 936" in bat_bytes, "bat missing @chcp 936"
    assert b"\r\n" in bat_bytes and b"\r\r" not in bat_bytes, "bat CRLF error"
    try:
        bat_bytes.decode("gbk")
        print("[PASS] 启动植物大战僵尸.bat is valid GBK + CRLF!")
    except UnicodeDecodeError:
        raise AssertionError("bat is not valid GBK!")

    md_path = r"F:\Desktop\.DeskBox\文件夹\反重力产出\文档\植物大战僵尸_Gemini4Argon复刻版本_交付说明.md"
    with open(md_path, "rb") as f:
        md_bytes = f.read()
    assert md_bytes.startswith(b"\xef\xbb\xbf"), "md missing UTF-8 BOM!"
    try:
        md_bytes.decode("utf-8")
        print("[PASS] 交付说明.md is valid UTF-8 with BOM!")
    except UnicodeDecodeError:
        raise AssertionError("md is not valid UTF-8!")

def check_code_syntax():
    import py_compile
    p1 = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_ten_levels.py"
    p2 = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_graphics.py"
    py_compile.compile(p1, doraise=True)
    py_compile.compile(p2, doraise=True)
    print("[PASS] Python source files syntax check passed!")

if __name__ == "__main__":
    check_encoding()
    check_code_syntax()
    print("ALL DELIVERY CHECKS 100% PASSED!")
