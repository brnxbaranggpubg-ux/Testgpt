#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")
engine = (root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
catalog = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
build = (root / "build.gradle").read_text(encoding="utf-8")
props = (root / "gradle.properties").read_text(encoding="utf-8")

ids = re.findall(r'\b(?:toggle|styled|cycle)\("([^\"]+)"', catalog)
assert len(ids) == 99, f"Expected 99 preserved module registrations; got {len(ids)}"
assert len(ids) == len(set(ids)), "Module IDs must remain unique"
assert "BAROX-VS-v077.jar" in build
assert "mod_version=0.77.0" in props
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v077"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v077"

checks = [
    ("double weavePhase = renderAnimationTime * (0.013 + capeMoveState * 0.003);", "kasa weave shimmer"),
    ("double strandSwing = Math.sin(strandPhase) * (0.026 + capeMoveState * 0.012) * scale;", "Hanfu tassel pendulum"),
    ("double secondaryWave = Math.sin(phase * 0.73 + t * 6.1 + side * 0.58);", "silk ribbon secondary wave"),
    ("double satinWave = Math.pow(Math.max(0.0,", "cape traveling satin sheen"),
    ("double orbitPhase = phase * 0.46;", "companion orbital animation"),
]
for needle, label in checks:
    assert needle in engine, f"Missing v077 animation invariant: {label}"

for signature in (
    "private void renderChineseHat(",
    "private void renderHanfuOrnament(",
    "private void renderSilkRibbons(",
    "private void renderCape(",
    "private void renderCompanionShape(",
):
    assert engine.count(signature) == 1, f"Expected one implementation: {signature}"

print("v077 validated: five cosmetic animation refinements; 99 unique module IDs preserved")
