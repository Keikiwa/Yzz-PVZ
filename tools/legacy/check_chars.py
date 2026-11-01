# -*- coding: utf-8 -*-
from pathlib import Path
import re

text = Path("10-pvz/pvz_ten_levels.py").read_text(encoding="utf-8")

matches = re.findall(r'text\([^,]+,\s*(f?["\'][^,\n]+)', text)
non_ascii = set()
for m in matches:
    for ch in m:
        if ord(ch) > 127:
            non_ascii.add(ch)

weird_chars = [
    ch for ch in non_ascii
    if not (0x4E00 <= ord(ch) <= 0x9FFF or 0x3000 <= ord(ch) <= 0x303F or 0xFF00 <= ord(ch) <= 0xFFEF or 0x2000 <= ord(ch) <= 0x206F)
]
print("Weird characters in text() calls:")
for ch in sorted(weird_chars):
    print(f"  '{ch}' (U+{ord(ch):04X}, code {ord(ch)})")
