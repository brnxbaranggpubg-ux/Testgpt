#!/usr/bin/env python3
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
engine = (root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text()
hud = (root / "src/main/java/com/baroxvs/client/hud/HudRenderer.java").read_text()
assert "class VisualMote" in engine
assert "updateVisualMotes(player)" in engine
assert "renderVisualMotes(output, camera, partial)" in engine
assert "mote.velocity.multiply(0.965)" in engine
assert "activeVisualMoteCount" in engine
assert "drawStar(out, camera, glint" in engine
assert "CosmeticEngine.activeVisualMoteCount()" in hud
assert "hud.debug.motes" in hud
for forbidden in ("addParticle(", "ParticleTypes.", "ParticleEffect", "ParticleManager"):
    assert forbidden not in engine, f"Vanilla particle API reintroduced: {forbidden}"
lang = root / "src/main/resources/assets/baroxvs/lang"
data = {name: json.loads((lang / name).read_text(encoding="utf-8"))
        for name in ("en_us.json", "de_de.json", "tr_tr.json")}
keys = set(data["en_us.json"])
assert all(set(value) == keys for value in data.values()), "locale key parity failed"
assert all("hud.debug.motes" in value for value in data.values())
assert "BAROX-VS-v037.jar" in (root / "build.gradle").read_text()
assert "mod_version=0.37.0" in (root / "gradle.properties").read_text()
print("v037 realistic mote checks passed")
