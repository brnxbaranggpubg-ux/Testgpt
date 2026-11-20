#!/usr/bin/env python3
from pathlib import Path
import re
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "project")
catalog=(root/"src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
cosmetic=(root/"src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
sky=(root/"src/main/java/com/baroxvs/client/render/SkyboxEngine.java").read_text(encoding="utf-8")
held=(root/"src/main/java/com/baroxvs/client/render/HeldItemGlassRenderer.java").read_text(encoding="utf-8")
build=(root/"build.gradle").read_text(encoding="utf-8")
props=(root/"gradle.properties").read_text(encoding="utf-8")
ids=re.findall(r'\b(?:toggle|styled|cycle)\("([^"]+)"',catalog)
assert len(ids)==99, f"expected 99 existing module IDs, got {len(ids)}"
assert len(ids)==len(set(ids)), "module IDs must remain unique"
assert "mod_version=0.84.0" in props
assert "archiveFileName = 'BAROX-VS-v084.jar'" in build
assert (root/"VERSION").read_text(encoding="utf-8").strip()=="BAROX VS v084"
assert (root/"BUILD_VERSION.txt").read_text(encoding="utf-8").strip()=="BAROX VS v084"
checks=[
 (sky,"panoramaDrift = (float) Math.sin(panoramaTime * 0.0011) * 1.65f;","Custom Sky panorama drift"),
 (sky,"float counterFlow = -ribbonPhase * 0.58f + 1.15f + i * 0.27f;","Aurora counter-flow ribbon"),
 (sky,"float cycleBreath = 0.994f + 0.006f * (float) Math.sin(dayTime * 0.0065f + channel * 0.82f);","Day/Night Sky palette breathing"),
 (cosmetic,"Vec3d ripplePearl = puddle.add(right.multiply(Math.cos(pearlAngle) * rx * 0.72))","Wet World orbit pearl"),
 (cosmetic,"double markerAngle = time * 0.012 * moodFrequency + marker * Math.PI * 2.0 / 3.0;","Ambient Mood orbit pearls"),
 (held,"float layeredSweep = clamp01(sweep + echo);","Held Item Glass dual sheen"),
]
for source,needle,label in checks:
 assert needle in source, f"missing v084 animation invariant: {label}"
print("v084 validated: five animation systems, 99 unique module IDs preserved")
