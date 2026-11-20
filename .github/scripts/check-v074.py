#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")
hud = (root / "src/main/java/com/baroxvs/client/hud/HudRenderer.java").read_text(encoding="utf-8")
catalog = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
build = (root / "build.gradle").read_text(encoding="utf-8")
props = (root / "gradle.properties").read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([^\"]+)"', catalog)
assert len(ids) == 99, f"Expected 99 preserved module registrations; got {len(ids)}"
assert len(ids) == len(set(ids)), "Module IDs must remain unique"
assert "BAROX-VS-v074.jar" in build
assert "mod_version=0.74.0" in props
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v074"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v074"

checks = [
    "int headerSweepW = Math.max(8, width / 5)",
    "int rowSweepX = rowX + 5 + Math.floorMod(ticks * 2 + i * 11",
    "int scanWidth = Math.max(6, w / 7)",
    "0.30f + 0.45f * (float) Math.sin(ticks * 0.12f + 4.2f)",
    "float worldPulse = 0.68f + 0.32f * (float) Math.sin(ticks * 0.09f)",
    "float clockPulse = 0.65f + 0.35f * (float) Math.sin(ticks * 0.15f)",
    "float pressPulse = 0.60f + 0.40f * (float) Math.sin(ticks * 0.34f + ly * 0.21f)",
    "float fpsPulse = 0.65f + 0.35f * (float) Math.sin(ticks * 0.18f)",
    "int memoryScanX = barX + Math.floorMod(ticks * 2",
]
for needle in checks:
    assert needle in hud, f"Missing v074 visual invariant: {needle}"

for signature in (
    "private int drawActiveModules(",
    "private void drawCoords(",
    "private void drawWorldCard(",
    "private void drawKeybinds(",
    "private void drawDebugOverlay(",
):
    assert hud.count(signature) == 1, f"Expected one implementation: {signature}"

assert "new Particle" not in hud
assert "addParticle(" not in hud
print("v074 validated: five animated HUD refinements; 99 unique module IDs preserved")
