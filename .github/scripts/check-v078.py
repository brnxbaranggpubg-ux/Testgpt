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
assert "BAROX-VS-v078.jar" in build
assert "mod_version=0.78.0" in props
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v078"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v078"

checks = [
    ("double crownSway = Math.sin(renderAnimationTime * 0.047) * 0.014", "headwear sway"),
    ("double sweep = positiveMod(renderAnimationTime * 0.018, 1.0);", "glint travelling sweep"),
    ("int satellites = activeRenderQuality == 0 ? 2 : 3;", "music aura satellites"),
    ("double beaconOrbit = rotation * 0.72 + progress * Math.PI * 0.9;", "jump-circle orbital beacons"),
    ("int bars = activeRenderQuality == 0 ? 4 : activeRenderQuality == 1 ? 5 : 6;", "audio visualizer radial bars"),
]
for needle, label in checks:
    assert needle in engine, f"Missing v078 animation invariant: {label}"

for signature in (
    "private void renderHeadwear(",
    "private void renderGlints(",
    "private void renderMusicAura(",
    "private void renderJumpPulse(",
    "private void renderMusicVisualizerGeometry(",
):
    assert engine.count(signature) == 1, f"Expected one implementation: {signature}"

assert "new Particle" not in engine, "Do not introduce new particle emitters in v078"
print("v078 validated: five animated cosmetic systems; 99 unique module IDs preserved")
