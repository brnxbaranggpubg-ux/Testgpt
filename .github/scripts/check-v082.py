#!/usr/bin/env python3
from pathlib import Path
import re
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "project")
hud=(root/"src/main/java/com/baroxvs/client/hud/HudRenderer.java").read_text(encoding="utf-8")
catalog=(root/"src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
build=(root/"build.gradle").read_text(encoding="utf-8")
props=(root/"gradle.properties").read_text(encoding="utf-8")
ids=re.findall(r'\b(?:toggle|styled|cycle)\("([^\"]+)"',catalog)
assert len(ids)==99, f"expected 99 module registrations, found {len(ids)}"
assert len(ids)==len(set(ids)), "module IDs must remain unique"
assert "mod_version=0.82.0" in props
assert "archiveFileName = 'BAROX-VS-v082.jar'" in build
assert (root/"VERSION").read_text(encoding="utf-8").strip()=="BAROX VS v082"
assert (root/"BUILD_VERSION.txt").read_text(encoding="utf-8").strip()=="BAROX VS v082"
checks=[
 ("private void drawCrosshairStudio(", "Crosshair Studio renderer"),
 ("double orbitPhase = now * (style == 3 ? -0.00165 : 0.00125)", "Crosshair Studio orbit"),
 ("private void drawKeyCap(", "Keystrokes HUD renderer"),
 ("int sheenW = Math.max(3, Math.min(7, w / 3));", "Keystrokes HUD moving sheen"),
 ("private void drawFpsGraph(", "FPS Graph renderer"),
 ("int echoX = graphX + Math.floorMod(ticks * 2 - 5, graphW);", "FPS Graph echo sweep"),
 ("private void drawCompassBar(", "Compass Bar renderer"),
 ("double pearlPhase = ticks * 0.095;", "Compass Bar orbiting pearls"),
 ("private void drawSpeed(", "Speed Graph renderer"),
 ("int crestX = graphX + Math.floorMod(ticks * 2, crestTravel);", "Speed Graph travelling crest"),
]
for needle,label in checks:
 assert needle in hud, f"missing v082 animation invariant: {label}"
for signature in ("private void drawCrosshairStudio(", "private void drawKeyCap(", "private void drawFpsGraph(", "private void drawCompassBar(", "private void drawSpeed("):
 assert hud.count(signature)==1, f"expected exactly one {signature}"
print("v082 validated: five animated HUD modules; 99 unique module IDs and version metadata preserved")
