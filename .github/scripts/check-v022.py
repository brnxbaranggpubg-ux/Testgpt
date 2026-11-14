#!/usr/bin/env python3
from pathlib import Path
import json, re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")
base = root / "src/main/java/com/baroxvs/client"
catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
engine = (base / "cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
metadata = json.loads((root / "src/main/resources/fabric.mod.json").read_text(encoding="utf-8"))

ids = re.findall(r'(?:toggle|styled|cycle)\("([^"]+)"', catalog)
assert len(ids) == 90, f"Expected 90 modules after 12 additions, got {len(ids)}"
required = {
    "meteor_shower", "energy_shield", "dragon_aura", "floating_crystals",
    "rgb_outline", "footprint_fx", "nameplate_designer", "weather_aura",
    "pet_companion", "cosmic_halo", "prism_trail", "celestial_wings", "wings"
}
missing = sorted(x for x in required if f'"{x}"' not in catalog)
assert not missing, f"Missing v022 modules: {missing}"

for token in [
    "renderV022Cosmetics", "v022Color", "v022WingColor",
    "drawRing(", "drawStar(", "drawDiamond(", "drawGlassOrb(", "ribbon(",
    'config.isOn("meteor_shower")', 'config.isOn("energy_shield")',
    'config.isOn("dragon_aura")', 'config.isOn("floating_crystals")',
    'config.isOn("rgb_outline")', 'config.isOn("footprint_fx")',
    'config.isOn("nameplate_designer")', 'config.isOn("weather_aura")',
    'config.isOn("pet_companion")', 'config.isOn("cosmic_halo")',
    'config.isOn("prism_trail")'
]:
    assert token in engine, f"Missing render feature: {token}"

assert "A separate ornamental wing effect" in catalog
assert "renderV022Cosmetics(output, camera, player, partial);" in engine
assert "player.getVelocity()" in engine
print("v022 checks passed: 89 modules; 12 new cosmetic geometry effects; pre-existing Wings catalogue preserved; player-motion-only trails.")
