#!/usr/bin/env python3
from pathlib import Path
import re
p = Path("project/src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java")
s = p.read_text(encoding="utf-8")
for marker in ["private void renderWings(", "private Vec3d wingPoint(", "private void drawSeraphWing("]:
    m = re.search(re.escape(marker), s)
    print("\n===== " + marker + " =====")
    if not m:
        print("NOT FOUND")
        continue
    start = m.start()
    brace = s.find("{", m.end())
    if brace < 0:
        print("NO BODY")
        continue
    depth = 0
    end = brace
    for end in range(brace, len(s)):
        if s[end] == "{": depth += 1
        elif s[end] == "}":
            depth -= 1
            if depth == 0:
                end += 1
                break
    print(s[start:end])
print("\n===== END WING INSPECTION =====")
