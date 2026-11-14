#!/usr/bin/env python3
from pathlib import Path
import json
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")
catalog = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
engine = (root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
metadata = json.loads((root / "src/main/resources/fabric.mod.json").read_text(encoding="utf-8"))

required_modules = ['"hand_glow"', '"arm_glow"', '"held_item_glow"', '"self_glass"']
for item in required_modules:
    assert item in catalog, f"Missing glass cosmetic module: {item}"

for kasa in ["Frost Jade Kasa", "Rose Quartz Kasa", "Moonlit Crane Kasa", "Golden Lotus Kasa"]:
    assert kasa in catalog, f"Missing Chinese Kasa style: {kasa}"

for color in ["Pearl Glass", "Aurora Glass", "Rose Glass", "Jade Glass", "Ice Glass", "Sunset Glass"]:
    assert color in catalog, f"Missing glass palette: {color}"

assert "renderGlowCosmetics" in engine
assert "glassColor" in engine
assert "drawGlassOrb" in engine
assert "getPerspective().isFirstPerson()" in engine
assert "getMainHandStack().isEmpty()" in engine and "getOffHandStack().isEmpty()" in engine

hat = engine[engine.index("private void renderChineseHat("):engine.index("/**\n     * Wide ceremonial straw kasa", engine.index("private void renderChineseHat("))]
for style in range(7, 11):
    assert f"style == {style}" in hat, f"Missing Chinese Kasa renderer branch {style}"

start = engine.index("private void renderGlowCosmetics(")
end = engine.index("private int glassColor(", start)
glow = engine[start:end]
assert "drawGlassOrb(" in glow and "drawRing(" in glow and "ribbon(" in glow
assert "add(" not in glow, "Glass aura must be geometry-only (no Spark/particle spawning)."

assert str(metadata.get("version")) == "0.19.0", f"Wrong mod version: {metadata.get('version')}"
print("v019 glass aura, held-item highlights, dual-arm glow and 11 Chinese Kasa styles passed.")
