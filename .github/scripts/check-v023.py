#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "project")
engine=(root/"src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
assert "shoulderRoot = pos.add(back.multiply(0.43)).add(0, 1.30, 0)" in engine
assert "waistRoot = pos.add(back.multiply(0.46)).add(0, 0.94, 0)" in engine
assert "Lower feather fan sits at the waist/hip line" in engine
assert "back.multiply(0.40 + i * 0.045)" in engine
assert "config.isOn(\"celestial_wings\") || config.isOn(\"wings\")" in engine
print("v023 checks passed: rear-offset shoulder wings, waist-level lower feathers, both Wings modules supported.")
