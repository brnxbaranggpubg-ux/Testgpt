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
    "Orbit Glow three-body orbital field": "Three pearls now share a gently precessing, offset orbital field" in cosmetic,
    "Pet Motion secondary spring sway": "double sideSway = Math.sin(phase * 1.7 + 0.4) * 0.045;" in cosmetic,
    "Nebula Clouds counter-flow ribbons": "float counterDrift = (float)Math.sin(phase * 0.22f + 1.1f) * 5.2f;" in sky,
    "Potions List glass badge pulse": "float badgePulse = 0.5f + 0.5f * (float) Math.sin(ticks * 0.16f + i * 0.92f);" in hud,
    "Target Card orbital badge crest": "double crestPhase = now * 0.0024;" in hud,
    "version archive": "archiveFileName = 'BAROX-VS-v087.jar'" in (root / "build.gradle").read_text(encoding="utf-8"),
    "version property": "mod_version=0.87.0" in (root / "gradle.properties").read_text(encoding="utf-8"),
    "version markers": "BAROX VS v087" in (root / "VERSION").read_text(encoding="utf-8") and "BAROX VS v087" in (root / "BUILD_VERSION.txt").read_text(encoding="utf-8"),
}
for label, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + label)
assert all(checks.values()), "one or more v087 invariants failed"
print(f"PASS: {len(ids)} unique module IDs retained")
