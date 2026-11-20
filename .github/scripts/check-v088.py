#!/usr/bin/env python3
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
cosmetic = (root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
sky = (root / "src/main/java/com/baroxvs/client/render/SkyboxEngine.java").read_text(encoding="utf-8")
hud = (root / "src/main/java/com/baroxvs/client/hud/HudRenderer.java").read_text(encoding="utf-8")
catalog = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([^"]+)"', catalog)
assert len(ids) == 99, f"expected 99 registered module declarations, found {len(ids)}"
assert len(set(ids)) == 99, "module IDs must remain unique"

checks = {
    "Footprint FX counter-moving sole glint": "double reverseSweep = (1.0 - soleSweep + 0.28) % 1.0;" in cosmetic,
    "Sky Stars orbital glass stars": "Three slow orbital glass stars add depth" in sky,
    "Sky Constellations moving glass nodes": "drawConstellationNode(out, matrix, nodeAX, nodeAY, phase, 0" in sky,
    "World Card animated row beacons": "float beaconPulse = 0.55f + 0.45f * (float)Math.sin(ticks * 0.13f + rowIndex * 1.37f);" in hud,
    "Player Status orbital pearl markers": "double pearlPhase = ticks * 0.12 + i * 1.83;" in hud,
    "version archive": "archiveFileName = 'BAROX-VS-v088.jar'" in (root / "build.gradle").read_text(encoding="utf-8"),
    "version property": "mod_version=0.88.0" in (root / "gradle.properties").read_text(encoding="utf-8"),
    "version markers": "BAROX VS v088" in (root / "VERSION").read_text(encoding="utf-8") and "BAROX VS v088" in (root / "BUILD_VERSION.txt").read_text(encoding="utf-8"),
}
for label, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + label)
assert all(checks.values()), "one or more v088 invariants failed"
print(f"PASS: {len(ids)} unique module IDs retained")
