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
assert "BAROX-VS-v073.jar" in build
assert "mod_version=0.73.0" in props
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v073"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v073"

checks = [
    "statusProgressTrail",
    "float badgePulse = 0.5f + 0.5f * (float) Math.sin(now * 0.0065)",
    "int headerSweepW = Math.max(7, headerW / 6)",
    "float rowPulse = 0.5f + 0.5f * (float) Math.sin(ticks * 0.22f + i * 0.85f)",
    "Ui.lerp(metricColor, Ui.WHITE, target < 0.30f",
    "private void drawCrosshairStudio(DrawContext c, MinecraftClient mc",
    "focusTarget = mc.targetedEntity instanceof LivingEntity living && living.isAlive() ? 1f : 0f",
    "targetAcquiredAtMs",
    "targetHealthTrail += (targetHealthBlend - targetHealthTrail)",
    "int scanX = x + 5 + Math.floorMod((int) (now / 9L)",
]
for needle in checks:
    assert needle in hud, f"Missing v073 visual invariant: {needle}"

for method in ("drawBiomeToast", "drawPotions", "drawPlayerStatus", "drawCrosshairStudio", "drawTarget"):
    matches = re.findall(r"private\\s+\\w+\\s+" + method + r"\\(", hud)
    assert len(matches) == 1, f"Expected one {method} implementation, got {len(matches)}"
assert "drawCrosshairStudio(c, mc, sw, sh, th)" in hud
print("v073 validated: five HUD visual systems; 99 unique module IDs preserved")
