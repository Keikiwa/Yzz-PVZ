# -*- coding: utf-8 -*-
from pathlib import Path
p = Path("10-pvz/pvz_ten_levels.py")
s = p.read_text(encoding="utf-8")
old = 'self.artifacts = set(self.save_data.get("artifacts", []))'
new = 'self.artifacts = set(self.save_data.get("artifacts", [])).union(getattr(self, "artifacts", set()))'
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("FIXED")
