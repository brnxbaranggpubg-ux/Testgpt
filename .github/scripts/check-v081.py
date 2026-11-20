#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")
engine = (root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
catalog = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
build = (root / "build.gradle").read_text(encoding="utf-8")
props = (root / "gradle.properties").read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([^"]+)"', catalog)
assert len(ids) == 99, f"Expected 99 preserved module registrations; got {len(ids)}"
assert len(ids) == len(set(ids)), "Module IDs must remain unique"
assert "BAROX-VS-v081.jar" in build
assert "mod_version=0.81.0" in props
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v081"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v081"
checks = [
    "double heartBeat = 0.5 + 0.5 * Math.sin(renderAnimationTime * 0.072);",
    "double orbitPhase = angle * 1.65 + progress * Math.PI * 2.0;",
    "double soleSweep = (time * 0.022 * frequency + age * 0.075) % 1.0;",
    "double lowerSweep = 0.5 + 0.5 * Math.sin(time * 0.039 - 0.7);",
    "double shimmer = 0.5 + 0.5 * Math.sin(time * 0.048 * frequency - i * 0.34);",
]
for needle in checks:
    assert needle in engine, f"Missing v081 animation invariant: {needle}"
print("v081 validated: five animated refinements; 99 unique module IDs preserved")
