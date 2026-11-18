import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
catalog_path = root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java"
engine_path = root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java"
settings_path = root / "src/main/java/com/baroxvs/client/gui/ModuleSettingsScreen.java"
catalog = catalog_path.read_text(encoding="utf-8")
engine = engine_path.read_text(encoding="utf-8")
settings = settings_path.read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
expected = [
    "dragon_aura", "floating_crystals", "rgb_outline", "footprint_fx", "nameplate_designer",
    "weather_aura", "cosmic_halo", "prism_trail", "module_resonance", "ambient_palette"
]
assert len(ids) == len(set(ids)) == 99, f"module catalogue must retain 99 unique IDs, got {len(ids)}"
assert ids[89:99] == expected, f"last-ten module registration order changed: {ids[89:99]}"
assert 'group("halo", "cosmic_halo")' in catalog
assert 'group("ambient_forms"' in catalog and '"ambient_palette"' in catalog
assert 'parentOf(String id)' in catalog

for symbol in [
    "drawDragonCoil", "drawCrystalPrism", "drawRgbVolume", "renderFootprints", "drawPlayerNameplate",
    "drawGlassTorus", "renderPrismTrail", "updateVisualHistories", "clearVisualHistories",
    "glyphBitmap", "resonanceSources", "AMBIENT_PALETTE_HUES", "V022_PALETTES"
]:
    assert symbol in engine, f"missing renderer feature: {symbol}"
assert "isRaining()" in engine and "isThundering()" in engine
assert "new Vec3d[FOOTPRINT_CAPACITY]" in engine
assert "new Vec3d[PRISM_TRAIL_CAPACITY]" in engine
assert "FOOTPRINT_CAPACITY = 10" in engine and "PRISM_TRAIL_CAPACITY = 18" in engine
assert "V022_GLOBAL_ALPHA.set(previousAlpha *" in engine
assert "V022_GLOBAL_ALPHA.set(previousAlpha);" in engine
assert "new int[][]" not in engine[engine.index("private int v022Color("):engine.index("private int v022WingColor(")]
assert "float[] hues" not in engine[engine.index("private Theme ambientTheme()"):engine.index("private Theme audioTheme()")]
resonance = engine[engine.index("private void renderV024ModuleResonance"):engine.index("private int v022Color(")]
assert "ModuleCatalog.inCategory(" not in resonance
assert 'String[] categories' not in resonance
assert 'ModuleCatalog.parentOf(module.id())' in resonance

for token in [
    'id.equals("dragon_aura")', 'id.equals("floating_crystals")', 'id.equals("rgb_outline")',
    'id.equals("footprint_fx")', 'id.equals("nameplate_designer")', 'id.equals("weather_aura")',
    'id.equals("cosmic_halo")', 'id.equals("prism_trail")', 'id.equals("module_resonance")'
]:
    assert token in settings, f"missing settings branch: {token}"
for key in ["crystalSpread", "crystalCount", "nameplateRaise", "prismLength", "cosmicHaloSpeed"]:
    assert f'case "{key}" ->' in settings, f"missing read/write mapping: {key}"
assert 'addSlider("moduleFrequency"' in settings

lang_dir = root / "src/main/resources/assets/baroxvs/lang"
locales = {name: json.loads((lang_dir / name).read_text(encoding="utf-8")) for name in ("en_us.json", "de_de.json", "tr_tr.json")}
keys = set(locales["en_us.json"])
assert all(set(values) == keys for values in locales.values()), "locale key parity failed"
for key in [
    "baroxvs.settings.visual_size", "baroxvs.settings.visual_opacity", "baroxvs.settings.animation_speed",
    "baroxvs.settings.crystal_orbit_spread", "baroxvs.settings.crystal_count", "baroxvs.settings.nameplate_height",
    "baroxvs.settings.trail_length", "baroxvs.settings.cosmic_halo_speed"
]:
    assert all(key in values and values[key] for values in locales.values()), f"missing localized label: {key}"

version = (root / "VERSION").read_text(encoding="utf-8").strip()
assert version == "BAROX VS v059", f"unexpected source version marker before stamp: {version}"
print("v059 final-ten module checks passed: 99 unique IDs, exact 90–99 registrations, renderer, settings and TR/DE/EN locale parity")
