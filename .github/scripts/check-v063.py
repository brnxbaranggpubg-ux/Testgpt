import re
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
base = root / "src/main/java/com/baroxvs/client"

catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(ids) == len(set(ids)) == 99, f"module registrations changed: {len(ids)}"
defaults = {}
for line in catalog.splitlines():
    m = re.search(r'\b(?:toggle|styled)\("([a-z0-9_]+)"', line)
    f = re.search(r',\s*(true|false)\s*(?:,|\))', line)
    if m and f:
        defaults[m.group(1)] = f.group(1) == "true"
reduced = """aura aura_pulse glint music_aura_sync orbit_stars halo player_glass hand_glow arm_glow held_item_glow self_glass liquid_rain head_accessories headwear chinese_hat hanfu_ornament silk_ribbons butterfly_companion pet pet_glow jump_circle wing_glints wing_outline wing_runes cape sky_mood custom_sky sky_time_cycle sky_studio sky_aurora sky_stars sky_fog sky_horizon_glow sky_nebula sky_meteors sky_constellations ambient_forms ambient_bounce music_visualizer dragon_aura floating_crystals rgb_outline footprint_fx nameplate_designer weather_aura cosmic_halo prism_trail module_resonance world_card player_status speed_graph potions_list keybinds ticker music_card lyric_flow target_card crosshair_ring toasts fps_graph biome_toast keystrokes_hud active_modules dynamic_island compass_bar debug_overlay""".split()
for module in reduced:
    assert defaults.get(module) is False, f"heavy/extra module default remains on: {module}"
for module in "wings wing_harness wing_membrane status_bar fps direction coordinates armor_hud".split():
    assert defaults.get(module) is True, f"essential visual unexpectedly disabled: {module}"
assert re.search(r'cycle\("geometry_quality",[^\n]*,\s*0\);', catalog)

engine = (base / "cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
render = engine[engine.index("private void renderWorldEffects("):engine.index("/** Local foot aura", engine.index("private void renderWorldEffects("))]
assert "if (!hasRenderableWorldEffects()) return;" in render
assert render.index("if (!hasRenderableWorldEffects()) return;") < render.index("context.consumers().getBuffer")
assert '|| config.isOn("ambient_forms") || config.isOn("sky_mood")' in engine
assert 'if (!(config.isOn("dragon_aura")' in engine
assert 'if (!config.isOn("footprint_fx") && !config.isOn("prism_trail"))' in engine
for token in [
    'case 0 -> 12; case 1 -> 18; default -> 24;',
    'case 0 -> 3; case 1 -> 4; default -> 5;',
    'case 0 -> 6; case 1 -> 8; default -> 10;',
    'case 0 -> 10; case 1 -> 14; default -> 18;',
    'private static int qualityCount(int base, int floor)',
    'case 0 -> 0.34f', 'case 0 -> 0.38f', 'qualityCount(42, 14)',
    'final int count = qualitySegments(28);'
]:
    assert token in engine, f"geometry LOD invariant missing: {token}"

hud = (base / "hud/HudRenderer.java").read_text(encoding="utf-8")
active = hud[hud.index("private void updateActiveModuleBlend()"):hud.index("private int activeModulePanelHeight()")]
assert 'if (!cfg.isOn("active_modules"))' in active
assert 'if (cfg.isOn("music_card") && cfg.isOn("lyric_flow")) LyricFlowOverlay.tick();' in hud
assert 'cfg.isOn("music_visualizer") || cfg.isOn("music_aura_sync")' in hud
assert 'if (cfg.isOn("biome_toast") || (cfg.isOn("status_bar") && cfg.isOn("biome"))' in hud

config = (base / "config/BaroxConfig.java").read_text(encoding="utf-8")
for token in [
    'public int performanceVersion = 0;', 'if (performanceVersion < 1)',
    'styles.put("geometry_quality", 0);',
    'if (loaded.performanceVersion != previousPerformanceVersion) loaded.save();',
    '"dragon_aura", "floating_crystals", "rgb_outline", "footprint_fx"',
    '"music_card", "lyric_flow", "target_card", "crosshair_ring", "toasts"'
]:
    assert token in config, f"one-time mobile preset migration missing: {token}"

assert (root / "PERFORMANCE_REDESIGN_v063.md").is_file()
assert (root / "VERSION").read_text().strip() == "BAROX VS v063"
assert (root / "BUILD_VERSION.txt").read_text().strip() == "BAROX VS v063"
assert "mod_version=0.63.0" in (root / "gradle.properties").read_text()
assert "BAROX-VS-v063.jar" in (root / "build.gradle").read_text()
print("v063 checks passed: performance migration, low mesh LOD, render early-outs, HUD polling guards, 99 module IDs")
