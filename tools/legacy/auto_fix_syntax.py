# -*- coding: utf-8 -*-
import py_compile
import re
from pathlib import Path

p = Path(r"10-pvz\pvz_ten_levels.py")

for attempt in range(50):
    try:
        py_compile.compile(str(p), doraise=True)
        print(f"SUCCESS: py_compile succeeded without errors at attempt {attempt}!")
        break
    except py_compile.PyCompileError as pe:
        msg = str(pe)
        print(f"[Attempt {attempt}] Error: {msg}")
        
        # 提取行号
        m = re.search(r"line (\d+)", msg)
        if not m:
            print("Cannot find line number in error message.")
            break
        lineno = int(m.group(1))
        
        lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
        idx = lineno - 1
        
        start = max(0, idx - 3)
        end = min(len(lines), idx + 3)
        print("Context:")
        for k in range(start, end):
            prefix = "--> " if k == idx else "    "
            print(f"{prefix}{k+1}: {repr(lines[k])}")
            
        if "unexpected indent" in msg:
            if lines[idx].startswith("    "):
                lines[idx] = lines[idx][4:]
                p.write_text("".join(lines), encoding="utf-8")
                print(f"Reduced indent at line {lineno}")
                continue
        elif "unindent does not match any outer indentation level" in msg or "expected an indented block" in msg:
            prev_line = lines[idx - 1]
            prev_indent = len(prev_line) - len(prev_line.lstrip(" "))
            if "expected an indented block" in msg:
                lines[idx] = " " * (prev_indent + 4) + lines[idx].lstrip(" ")
            else:
                lines[idx] = " " * prev_indent + lines[idx].lstrip(" ")
            p.write_text("".join(lines), encoding="utf-8")
            print(f"Adjusted indent at line {lineno} to match prev")
            continue
        elif "invalid syntax" in msg and lines[idx].strip() == "else:":
            prev_line = lines[idx - 1]
            prev_indent = len(prev_line) - len(prev_line.lstrip(" "))
            lines[idx] = " " * (prev_indent - 4) + lines[idx].lstrip(" ")
            p.write_text("".join(lines), encoding="utf-8")
            print(f"Adjusted else: indent at line {lineno}")
            continue
        else:
            print(f"Cannot auto-resolve {msg} at line {lineno}, stopping.")
            break
