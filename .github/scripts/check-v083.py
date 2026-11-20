#!/usr/bin/env python3
from pathlib import Path
import re
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "project")
engine=(root/"src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
sky=(root/"src/main/java/com/baroxvs/client/render/SkyboxEngine.java").read_text(encoding="utf-8")
hud=(root/"src/main/java/com/baroxvs/client/hud/HudRenderer.java").read_text(encoding="utf-8")
catalog=(root/"src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
build=(root/"build.gradle").read_text(encoding="utf-8")
props=(root/"gradle.properties").read_text(encoding="utf-8")
ids=re.findall(r'\b(?:toggle|styled|cycle)\("([^\"]+)"',catalog)
assert len(ids)==99, f"expected 99 module registrations, got {len(ids)}"
assert len(ids)==len(set(ids)), "module IDs must remain unique"
assert "mod_version=0.83.0" in props
assert "archiveFileName = 'BAROX-VS-v083.jar'" in build
assert (root/"VERSION").read_text(encoding="utf-8").strip()=="BAROX VS v083"
assert (root/"BUILD_VERSION.txt").read_text(encoding="utf-8").strip()=="BAROX VS v083"
checks=[
 ("double bloomOrbit = renderAnimationTime * 0.0085;", "Aura Bloom orbit"),
 ("double pearlOrbit = phase * 0.62;", "Butterfly Companion satellites"),
 ("double glowOrbit = phase * 0.82;", "Companion Glow petals"),
 ("double fogBreath = 0.955 + 0.045 * Math.sin(System.currentTimeMillis() * 0.00038);", "Atmospheric Fog Tint breath"),
 ("double portalPhase = ticks * 0.075;", "Nether Coordinates portal motion"),
]
for needle,label in checks:
 assert needle in (engine+sky+hud), f"missing animation invariant: {label}"
print("v083 validated: five added animations and 99 unique module IDs preserved")
