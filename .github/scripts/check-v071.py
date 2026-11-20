#!/usr/bin/env python3
from pathlib import Path
import re, sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")
engine = (root / "src/main/java/com/baroxvs/client/render/SkyboxEngine.java").read_text(encoding="utf-8")
catalog = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
build = (root / "build.gradle").read_text(encoding="utf-8")
props = (root / "gradle.properties").read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([^"]+)"', catalog)
assert len(ids) == 99, f"Expected 99 preserved module registrations; got {len(ids)}"
assert len(ids) == len(set(ids)), "Module IDs must remain unique"
assert "BAROX-VS-v071.jar" in build
assert "mod_version=0.71.0" in props
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v071"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v071"
checks = [
    "float phase = worldTime * 0.0032f",
    "drawSoftSkyBlobRotated(out, matrix, -15f",
    "drawCelestialHaze(matrices, consumers, cfg, night, worldTime, dayTime)",
    'int count = cfg.style("sky_meteors") == 2 ? 3 : 2',
    "drawHorizonGlow(matrices, consumers, cfg, dayTime, worldTime)",
    "private static void drawSoftSkyBlobRotated",
]
for needle in checks:
    assert needle in engine, f"Missing v071 visual invariant: {needle}"
assert "private static void drawCelestialHaze" in engine
assert "private static void drawHorizonGlow" in engine
assert "private static void drawMeteorGlow" in engine
print("v071 validated: five animated sky systems; 99 unique module IDs preserved")
