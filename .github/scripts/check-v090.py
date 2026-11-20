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

for module_id in ("fps", "direction", "biome", "ping", "local_clock"):
    assert re.search(r'\b(?:toggle|styled|cycle)\("' + re.escape(module_id) + r'"', catalog), module_id

checks = {
    "FPS adaptive equalizer": 'case "fps" ->' in hud and 'fps / (float) (48 * (i + 1))' in hud,
    "Direction yaw compass needle": 'case "direction" ->' in hud and 'Math.toRadians(mc.player.getYaw())' in hud,
    "Biome orbiting nodes": 'case "biome" ->' in hud and 'double orbit = ticks * 0.075;' in hud,
    "Ping latency pulse": 'case "ping" ->' in hud and 'latency / 300f' in hud,
    "Local clock second hand": 'case "clock" ->' in hud and 'now.getSecond() * Math.PI / 30.0' in hud,
    "Status row kind bindings": 'cachedStatusKinds.add("fps")' in hud and 'cachedStatusKinds.add("clock")' in hud,
    "version archive": "archiveFileName = 'BAROX-VS-v090.jar'" in (root / "build.gradle").read_text(encoding="utf-8"),
    "version property": "mod_version=0.90.0" in (root / "gradle.properties").read_text(encoding="utf-8"),
    "version markers": "BAROX VS v090" in (root / "VERSION").read_text(encoding="utf-8") and "BAROX VS v090" in (root / "BUILD_VERSION.txt").read_text(encoding="utf-8"),
}
for label, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + label)
assert all(checks.values()), "one or more v090 invariants failed"
print(f"PASS: {len(ids)} unique module IDs retained")
