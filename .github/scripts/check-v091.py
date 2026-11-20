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
    "Nether Coordinates counter-rotating portal": 'double innerAngle = -portalPhase * 1.22' in hud and 'portalBreath' in hud,
    "World Dimension orbital core": 'case "dimension" ->' in hud and 'Math.cos(angle) * 4.5' in hud,
    "World Biome habitat bloom": 'case "biome" ->' in hud and 'double orbit = phase * 0.86' in hud,
    "World Weather filled climate animation": 'case "weather" ->' in hud and 'dropY = cy + Math.floorMod' in hud,
    "World Time live day clock": 'case "time" ->' in hud and 'line.progress() * Math.PI * 2.0' in hud,
    "World monitor kinds are explicit": all(f'new WorldInfoLine("{kind}"' in hud for kind in ("dimension", "biome", "weather", "time")),
    "Version archive": "archiveFileName = 'BAROX-VS-v091.jar'" in (root / "build.gradle").read_text(encoding="utf-8"),
    "Version property": "mod_version=0.91.0" in (root / "gradle.properties").read_text(encoding="utf-8"),
    "Version markers": "BAROX VS v091" in (root / "VERSION").read_text(encoding="utf-8") and "BAROX VS v091" in (root / "BUILD_VERSION.txt").read_text(encoding="utf-8"),
}
for label, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + label)
assert all(checks.values()), "one or more v091 invariants failed"
print(f"PASS: {len(ids)} unique module IDs retained")
