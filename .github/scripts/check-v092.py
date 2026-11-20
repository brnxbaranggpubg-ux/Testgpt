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
    "Health Meter heartbeat halo": 'case "health_status" ->' in hud and 'ticks * 0.34f' in hud,
    "Hunger Meter orbiting crumbs": 'case "hunger_status" ->' in hud and 'crumbPhase = ticks * 0.13' in hud,
    "Experience Meter traveling XP mote": 'case "experience_status" ->' in hud and 'moteX = cellX + 3 + Math.floorMod(ticks * 2, moteTravel)' in hud,
    "Armor HUD dual satellite orbit": 'armorOrbit = ticks * 0.085' in hud and 'satellite < 2' in hud,
    "Target Card animated lock brackets": 'lockPulse = 0.5f + 0.5f' in hud and 'Four short corner brackets' in hud,
    "Status metric kind mapping": all(f'new StatusMetric("{kind}"' in hud for kind in ("health_status", "hunger_status", "experience_status")),
    "Version archive": "archiveFileName = 'BAROX-VS-v092.jar'" in (root / "build.gradle").read_text(encoding="utf-8"),
    "Version property": "mod_version=0.92.0" in (root / "gradle.properties").read_text(encoding="utf-8"),
    "Version markers": "BAROX VS v092" in (root / "VERSION").read_text(encoding="utf-8") and "BAROX VS v092" in (root / "BUILD_VERSION.txt").read_text(encoding="utf-8"),
}
for label, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + label)
assert all(checks.values()), "one or more v092 invariants failed"
print(f"PASS: {len(ids)} unique module IDs retained")
