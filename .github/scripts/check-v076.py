#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")
hud = (root / "src/main/java/com/baroxvs/client/hud/HudRenderer.java").read_text(encoding="utf-8")
editor = (root / "src/main/java/com/baroxvs/client/gui/HudEditorScreen.java").read_text(encoding="utf-8")
settings = (root / "src/main/java/com/baroxvs/client/gui/ModuleSettingsScreen.java").read_text(encoding="utf-8")
catalog = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
build = (root / "build.gradle").read_text(encoding="utf-8")
props = (root / "gradle.properties").read_text(encoding="utf-8")

ids = re.findall(r'\b(?:toggle|styled|cycle)\("([^"]+)"', catalog)
assert len(ids) == 99, f"Expected 99 preserved module registrations; got {len(ids)}"
assert len(ids) == len(set(ids)), "Module IDs must remain unique"
assert "BAROX-VS-v076.jar" in build
assert "mod_version=0.76.0" in props
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v076"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v076"

checks = [
    (hud, "int shimmerW = Math.max(8, Math.min(18, w / 6));", "watermark specular sweep"),
    (hud, "float eased = 1f - (1f - t) * (1f - t);", "hit-number eased rise"),
    (hud, "int progressW = Math.round(railW * remaining);", "toast lifetime rail"),
    (editor, "int scanTravel = Math.max(1, pw - 14 - scanW);", "HUD editor preview scan"),
    (settings, "float pulse = 0.65f + 0.35f * (float) Math.sin(System.currentTimeMillis() * 0.006f);", "settings slider thumb pulse"),
]
for source, needle, label in checks:
    assert needle in source, f"Missing v076 visual invariant: {label}"

for source, signature in (
    (hud, "private void drawWatermark("),
    (hud, "private void drawPopups("),
    (hud, "private void drawToasts("),
    (editor, "private void drawPreview("),
    (settings, "private void drawSlider("),
):
    assert source.count(signature) == 1, f"Expected one implementation: {signature}"

print("v076 validated: five visual refinements; 99 unique module IDs preserved")
