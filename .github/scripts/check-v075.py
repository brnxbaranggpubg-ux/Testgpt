#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")
hud = (root / "src/main/java/com/baroxvs/client/hud/HudRenderer.java").read_text(encoding="utf-8")
catalog = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
build = (root / "build.gradle").read_text(encoding="utf-8")
props = (root / "gradle.properties").read_text(encoding="utf-8")

ids = re.findall(r'\b(?:toggle|styled|cycle)\("([^"]+)"', catalog)
assert len(ids) == 99, f"Expected 99 preserved module registrations; got {len(ids)}"
assert len(ids) == len(set(ids)), "Module IDs must remain unique"
assert "BAROX-VS-v075.jar" in build
assert "mod_version=0.75.0" in props
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v075"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v075"

checks = [
    "int sparkW = Math.max(2, Math.min(9, progressW / 4))",
    "int underlineW = Math.max(3, wordWidth / 3)",
    "int orbitX = x + 21 + Math.round((float) Math.cos(ticks * 0.075f) * 10f)",
    "int lyricSweepW = Math.max(8, w / 7)",
    "float markerPulse = 0.72f + 0.28f * (float) Math.sin(ticks * 0.22f)",
    "float brandPulse = 0.70f + 0.30f * (float) Math.sin(ticks * 0.13f)",
    "float rowPulse = 0.5f + 0.5f * (float) Math.sin(ticks * 0.18f + rowIndex * 1.1f)",
]
for needle in checks:
    assert needle in hud, f"Missing v075 animation invariant: {needle}"

for signature in (
    "private void drawDynamicIsland(",
    "private void drawTicker(",
    "private void drawMusic(",
    "private void drawLyricFlow(",
    "private int[] drawInfoPanel(",
):
    assert hud.count(signature) == 1, f"Expected one implementation: {signature}"

print("v075 validated: five animated HUD panels; 99 unique module IDs preserved")
