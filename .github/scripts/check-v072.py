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
assert "BAROX-VS-v072.jar" in build
assert "mod_version=0.72.0" in props
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v072"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v072"
checks = [
    "A slim scanning cursor tracks the newest sample",
    "float cursorPulse = 0.62f + 0.38f * (float) Math.sin(ticks * 0.24f)",
    "if (pct <= 25)",
    "float warning = 0.55f + 0.45f * (float) Math.sin(ticks * 0.18f + i * 0.9f)",
    "float pressure = active * (0.88f + 0.12f * (float) Math.sin(ticks * 0.30f))",
    "int sixtyY = graphY + graphH - Math.round(60f / ceiling * graphH)",
    "int scanX = graphX + Math.floorMod(ticks * 2, graphW)",
    "float fraction = step - (float) Math.floor(step)",
    "float needlePulse = 0.66f + 0.34f * (float) Math.sin(ticks * 0.16f)",
]
for needle in checks:
    assert needle in hud, f"Missing v072 HUD animation invariant: {needle}"
assert hud.count("private void drawSpeed(") == 1
assert hud.count("private void drawArmor(") == 1
assert hud.count("private void drawKeystrokes(") == 1
assert hud.count("private void drawFpsGraph(") == 1
assert hud.count("private void drawCompassBar(") == 1
print("v072 validated: five animated HUD systems; 99 unique module IDs preserved")
