#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")
base = root / "src/main/java/com/baroxvs/client"
catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
cosmetic_catalog = (base / "cosmetic/CosmeticCatalog.java").read_text(encoding="utf-8")
engine = (base / "cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
sky = (base / "render/SkyboxEngine.java").read_text(encoding="utf-8")
config = (base / "config/BaroxConfig.java").read_text(encoding="utf-8")
settings = (base / "gui/ModuleSettingsScreen.java").read_text(encoding="utf-8")
ui = (base / "gui/Ui.java").read_text(encoding="utf-8")
menu = (base / "gui/BaroxMenuScreen.java").read_text(encoding="utf-8")

module_ids = re.findall(r'(?:toggle|styled|cycle)\("([^"]+)"', catalog)
assert len(module_ids) == 78, f"Expected 78 consolidated module entries, got {len(module_ids)}"
assert len(module_ids) == len(set(module_ids)), "Duplicate module IDs remain"

for old in ["ambient_orbs", "ambient_cubes", "ambient_white", "defeat_dissolve", "crown_sparkles", "hit_numbers"]:
    assert f'toggle("{old}"' not in catalog and f'styled("{old}"' not in catalog, f"Retired module still visible: {old}"

for new in ["glint", "music_aura_sync", "ambient_forms", "butterfly_companion", "jump_crystal"]:
    assert f'"{new}"' in catalog, f"Missing v020 module: {new}"

sky_names = cosmetic_catalog[cosmetic_catalog.index("SKIES"):cosmetic_catalog.index("AMBIENT_DENSITIES")]
assert len(re.findall(r'"[^"]+"', sky_names)) == 44, "Sky catalogue must contain 44 presets"

palette_start = sky.index("SKY_PALETTES")
palette_end = sky.index("};", palette_start)
palette_body = sky[palette_start:palette_end]
assert len(re.findall(r"0xFF[0-9A-Fa-f]{6}", palette_body)) == 44 * 3, "Sky palette count must match 44 three-stop presets"
assert "preset >= 32 ? 164" in sky

for feature in [
    "private void renderGlints(", "private void renderMusicAura(",
    "private void renderButterflyCompanion(", "private void emitJumpBurst(",
    'config.isOn("music_aura_sync")', 'config.isOn("butterfly_companion")',
    'config.isOn("ambient_forms")', "drawButterflyParticle(out, camera, centre",
    "drawGlassOrb(out, camera, spark.position"
]:
    assert feature in engine, f"Missing engine feature: {feature}"

assert 'new String[]{"Crystal Halo", "Sakura Petals", "Butterfly Lift", "Moon Hearts", "Liquid Rings", "Prism Stars"}' in catalog
assert "migrateV020Modules" in config and "cosmeticVersion" in config
assert all(x in settings for x in ["ambient_forms", "glint", "butterfly_companion", "music_aura_sync"])
assert "Shared liquid-glass finish" in ui and "public static void glassPanel" in ui
assert "MusicEngine.audioLevel()" in menu and "AURA SYNC" in menu
assert "knife" not in engine.lower(), "Butterfly cosmetic must remain non-weapon geometry"
print("v020 passed: 78 modules, 44 skies, liquid-glass UI, glints, synced music aura, jump shapes, animated butterfly companion and config migration.")
