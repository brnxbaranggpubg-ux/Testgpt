#!/usr/bin/env python3
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
hud = (root / "src/main/java/com/baroxvs/client/hud/HudRenderer.java").read_text(encoding="utf-8")
catalog = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([^"]+)"', catalog)
assert len(ids) == 99, f"expected 99 module declarations, found {len(ids)}"
assert len(set(ids)) == 99, "module IDs must stay unique"
checks = {
    "Coordinates axis gyro": "double axisPhase = ticks * 0.14;" in hud and "axisPhase + i * Math.PI * 2.0 / 3.0" in hud,
    "KeyBinds pressed-key ripples": "double ripplePhase = ticks * 0.22 + ly * 0.09;" in hud and "rippleY = ly - 2" in hud,
    "Active Visuals row beacons": "double beaconPhase = ticks * 0.16 + i * 0.72;" in hud and "beaconPulse" in hud,
    "Diagnostics FPS satellites": "double fpsOrbit = ticks * 0.13;" in hud and "fpsBeaconX" in hud,
    "Watermark emblem orbit": "double emblemPhase = ticks * 0.075;" in hud and "orbitPulse" in hud,
    "All five existing module IDs retained": all(re.search(r'\b(?:toggle|styled|cycle)\("' + re.escape(module_id) + r'"', catalog) for module_id in ("coordinates", "keybinds", "active_modules", "debug_overlay", "watermark")),
    "Version archive": "archiveFileName = 'BAROX-VS-v093.jar'" in (root / "build.gradle").read_text(encoding="utf-8"),
    "Version property": "mod_version=0.93.0" in (root / "gradle.properties").read_text(encoding="utf-8"),
    "Version markers": "BAROX VS v093" in (root / "VERSION").read_text(encoding="utf-8") and "BAROX VS v093" in (root / "BUILD_VERSION.txt").read_text(encoding="utf-8"),
}
for label, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + label)
assert all(checks.values()), "one or more v093 invariants failed"
print(f"PASS: {len(ids)} unique module IDs retained")
