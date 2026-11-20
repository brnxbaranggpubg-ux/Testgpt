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
assert "BAROX-VS-v080.jar" in build
assert "mod_version=0.80.0" in props
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v080"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v080"

checks = [
    ("double figureEight = Math.sin(angle * 1.55 + time * 0.012) * 0.075;", "Orbit Stars figure-eight drift"),
    ("double coilBreath = 1.0 + Math.sin(crownPhase * 0.72) * 0.035;", "Dragon Aura breathing coil"),
    ("double crystalPulse = 1.0 + Math.sin(phase * 1.35 + i * 0.9) * 0.045;", "Floating Crystals pulse"),
    ("double windPhase = weatherPhase * 0.34;", "Weather Aura wind sweep"),
    ("Vec3d tiltedUp = forward.crossProduct(tiltedAxis).normalize();", "Cosmic Halo tilted orbital ring"),
    ("Vec3d trailingPearl = centre.add(right.multiply", "Orbit Stars trailing pearl"),
]
for needle, label in checks:
    assert needle in engine, f"Missing v080 animation invariant: {label}"

for signature in (
    "private void renderV022Cosmetics(",
    "private void renderAttachedGeometryEffects(",
):
    assert engine.count(signature) == 1, f"Expected one implementation: {signature}"

print("v080 validated: five animated visual systems; 99 unique module IDs preserved")
