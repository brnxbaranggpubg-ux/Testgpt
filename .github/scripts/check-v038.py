#!/usr/bin/env python3
import json, re, sys
from pathlib import Path
root = Path(sys.argv[1])
engine = (root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
catalog = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
hud = (root / "src/main/java/com/baroxvs/client/hud/HudRenderer.java").read_text(encoding="utf-8")
for token in (
    "class VisualMote", "class TrailNode", "updatePrismTrail(player, speed)",
    "renderPrismTrailRibbon(output, camera)", "renderVisualMotes(output, camera, partial)",
    "mote.velocity.multiply(mote.drag)", "mote.velocity.lengthSquared()",
    "wingPoint(playerPos, right, back, side, span, motion, 0.035)",
    "activeVisualMoteCount",
):
    assert token in engine, f"missing v038 effect path: {token}"
assert "CosmeticEngine.activeVisualMoteCount()" in hud
assert "hud.debug.motes" in hud
for forbidden in ("addParticle(", "ParticleTypes.", "ParticleEffect", "ParticleManager"):
    assert forbidden not in engine, f"vanilla particle API used: {forbidden}"
lang = root / "src/main/resources/assets/baroxvs/lang"
data = {name: json.loads((lang / name).read_text(encoding="utf-8"))
        for name in ("en_us.json", "de_de.json", "tr_tr.json")}
keys = set(data["en_us.json"])
assert all(set(value) == keys for value in data.values()), "locale keys differ"
module_ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(module_ids) == len(set(module_ids)) == 97, f"expected 97 unique modules, got {len(module_ids)}"
assert "BAROX-VS-v038.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=0.38.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v038"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v038"
assert "# BAROX VS — v038" in (root / "README.md").read_text(encoding="utf-8")
print("v038 checks passed: motion trail, bounded motes, wing surface highlights, 97 modules and locale parity")
