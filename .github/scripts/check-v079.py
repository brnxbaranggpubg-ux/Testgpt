#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")
engine = (root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
renderer = (root / "src/main/java/com/baroxvs/client/render/SelfGlassRenderer.java").read_text(encoding="utf-8")
catalog = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
build = (root / "build.gradle").read_text(encoding="utf-8")
props = (root / "gradle.properties").read_text(encoding="utf-8")

ids = re.findall(r'\b(?:toggle|styled|cycle)\("([^"]+)"', catalog)
assert len(ids) == 99, f"Expected 99 preserved module registrations; got {len(ids)}"
assert len(ids) == len(set(ids)), "Module IDs must remain unique"
assert "BAROX-VS-v079.jar" in build
assert "mod_version=0.79.0" in props
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v079"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v079"

checks = [
    (renderer, "float counterSweep = clamp01(", "RGB outline counter-sweep"),
    (renderer, "float edgeBreath = 0.90f + 0.10f *", "RGB outline breathing edge"),
    (engine, "double driftPhase = time * 0.0065", "ambient field orientation drift"),
    (engine, "double waveRadius = radius * (0.44 + progress * 0.82);", "Surface Pulse traveling waves"),
    (engine, "double counterScan = -scan * 0.72 + Math.PI;", "Energy Shield counter-scanning beacon"),
    (engine, "int harmonics = Math.min(4, Math.max(2, v024ModuleCacheCount));", "Module Resonance harmonics"),
]
for source, needle, label in checks:
    assert needle in source, f"Missing v079 animation invariant: {label}"

for source, signature in (
    (renderer, "public static void renderRgbOutline("),
    (engine, "private void renderAmbientGeometry("),
    (engine, "private void renderEnergyShield("),
    (engine, "private void renderV024ModuleResonance("),
):
    assert source.count(signature) == 1, f"Expected one implementation: {signature}"

print("v079 validated: five animated systems; 99 unique module IDs preserved")
