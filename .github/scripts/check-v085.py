#!/usr/bin/env python3
from pathlib import Path
import re
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "project")
src=(root/"src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
catalog=(root/"src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
build=(root/"build.gradle").read_text(encoding="utf-8")
props=(root/"gradle.properties").read_text(encoding="utf-8")
ids=re.findall(r'\b(?:toggle|styled|cycle)\("([^\"]+)"',catalog)
assert len(ids)==99, f"expected 99 module registrations, got {len(ids)}"
assert len(ids)==len(set(ids)), "module IDs must remain unique"
assert "mod_version=0.85.0" in props
assert "archiveFileName = 'BAROX-VS-v085.jar'" in build
assert (root/"VERSION").read_text(encoding="utf-8").strip()=="BAROX VS v085"
assert (root/"BUILD_VERSION.txt").read_text(encoding="utf-8").strip()=="BAROX VS v085"
checks=[
 ('double harnessPhase = renderAnimationTime * 0.018;', 'Wing Harness rotating clasp and pulse'),
 ('double runeOrbit = renderAnimationTime * 0.024;', 'Wing Relief orbiting runes'),
 ('double echoSweep = positiveMod(sweep + 0.36, 1.0);', 'Wing Sheen echo sweep'),
 ('double contourPulse = 0.82 + 0.18 * Math.sin(renderAnimationTime * 0.052);', 'Wing Surface breathing contour'),
 ('double membranePulse = 0.86 + 0.14 * Math.sin(renderAnimationTime * 0.046 + bx * 4.2 + side);', 'Wing Membrane breathing surface'),
]
for needle,label in checks:
 assert needle in src, f"missing v085 animation invariant: {label}"
print("v085 validated: five wing modules animated; 99 unique existing module IDs preserved")
