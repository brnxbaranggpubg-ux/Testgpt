#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
read = lambda p: (root / p).read_text(encoding='utf-8')

catalog = read('src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java')
engine = read('src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java')
sky = read('src/main/java/com/baroxvs/client/render/SkyboxEngine.java')
ui = read('src/main/java/com/baroxvs/client/gui/Ui.java')
click = read('src/main/java/com/baroxvs/client/gui/ModuleClickGuiScreen.java')
settings = read('src/main/java/com/baroxvs/client/gui/ModuleSettingsScreen.java')
hud = read('src/main/java/com/baroxvs/client/hud/HudRenderer.java')
chat = read('src/main/java/com/baroxvs/client/HudChatCommands.java')

ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(ids) == len(set(ids)) == 99, f'module catalogue changed: {len(ids)} declarations / {len(set(ids))} unique'
groups = re.findall(r'group\("([a-z0-9_]+)"\s*,([^;]+)\);', catalog)
children = []
for parent, raw in groups:
    child_ids = re.findall(r'"([a-z0-9_]+)"', raw)
    assert parent in ids and child_ids
    children.extend(child_ids)
assert len(groups) == 14 and len(children) == len(set(children)) == 50
assert len(set(ids) - set(children)) == 49

# Shared iOS-inspired glass material, layered reflections and low-risk rendering path.
for token in ('roundRectGradient(', 'roundedInset(', 'fillRoundedScanline(',
              'public static void glassPanel(', 'public static void glassButton(',
              'secondaryAlpha', 'innerTravel', '0x00BEEBFF'):
    assert token in ui, f'missing glass material feature: {token}'
assert 'scene-sampling blur' in ui and 'framebuffer blur' in ui
assert 'gl_Frag' not in ui and 'Framebuffer' not in ui and 'PostEffect' not in ui
for token in ('animationTime * 0.075f', 'animationTime * 0.045f', 'Ui.glassPanel', 'Ui.glassButton'):
    assert token in click, f'ClickGUI glass treatment missing: {token}'
for token in ('L10n.tr("settings.visual_enhancement")', 'L10n.tr("settings.visual_power")',
              'case "moduleIntensity" -> config.moduleValue',
              'case "moduleIntensity" -> config.setModuleValue', 'Ui.glassPanel', 'Ui.glassButton'):
    assert token in settings, f'module settings upgrade missing: {token}'

# One visual-power value applies to alpha and exposure, with stable nested-feature ownership.
for token in ('GEOMETRY_INTENSITY', 'intensityOwner(', 'config.moduleValue(owner, "intensity"',
              'alpha * strength', 'float exposure = 1.0f + (strength - 1.0f) * 0.28f',
              'red << 16', 'renderV024ModuleResonance'):
    assert token in engine, f'cosmetic power wiring missing: {token}'
for child, parent in {
    'chinese_hat': 'head_accessories', 'hanfu_ornament': 'head_accessories',
    'butterfly_companion': 'pet', 'cosmic_halo': 'halo', 'sky_aurora': 'sky_studio',
    'hand_glow': 'player_glass', 'music_aura_sync': 'aura', 'sky_mood': 'ambient_forms'
}.items():
    assert re.search(r'case .*"' + re.escape(child) + r'".*-> "' + re.escape(parent) + r'"', engine), f'{child} does not inherit {parent} power'
for module in ('liquid_rain', 'aura', 'player_glass', 'wings', 'chinese_hat', 'silk_ribbons',
               'cape', 'butterfly_companion', 'glint', 'music_aura_sync', 'meteor_shower',
               'energy_shield', 'dragon_aura', 'floating_crystals', 'rgb_outline', 'footprint_fx',
               'nameplate_designer', 'weather_aura', 'cosmic_halo', 'prism_trail', 'jump_circle',
               'music_visualizer', 'orbit_stars', 'ambient_forms', 'sky_mood', 'module_resonance'):
    assert f'withModuleStrength("{module}"' in engine, f'{module} missing per-module exposure wrapper'

# HUD widget groups inherit intensity from the same parent that owns the visible component controls.
for token in ('widgetIntensityOwner(', 'cfg.moduleValue(widgetIntensityOwner(moduleId), "intensity"',
              'activeWidgetGlassStyle', 'Ui.glassPanel', 'float exposure = 1.0f + (intensity - 1.0f) * 0.20f'):
    assert token in hud, f'HUD material/power wiring missing: {token}'
for child, parent in {
    'fps': 'status_bar', 'nether_coords': 'coordinates', 'world_weather': 'world_card',
    'health_status': 'player_status', 'lyric_flow': 'music_card', 'crosshair_studio': 'crosshair_ring'
}.items():
    assert re.search(r'case .*"' + re.escape(child) + r'".*-> "' + re.escape(parent) + r'"', hud), f'{child} does not inherit {parent} HUD power'

# All sky layers, fog tint and panorama brightness use the Sky Studio family control.
for token in ('skyIntensity(cfg)', 'boostedAlpha(cfg,', 'float skyIntensity(',
              'cfg.moduleValue("sky_studio", "intensity"', ' * skyIntensity(cfg)',
              'Math.min(0.65f', 'Math.min(0.72f'):
    assert token in sky, f'Sky Studio power missing: {token}'

# Localized new controls and unchanged existing locale coverage.
lang = root / 'src/main/resources/assets/baroxvs/lang'
data = {name: json.loads((lang / name).read_text(encoding='utf-8'))
        for name in ('en_us.json', 'de_de.json', 'tr_tr.json')}
keys = set(data['en_us.json'])
assert all(set(value) == keys for value in data.values()), 'TR/DE/EN locale keys differ'
for key in ('baroxvs.settings.visual_enhancement', 'baroxvs.settings.visual_power'):
    assert key in keys

assert "archiveFileName = 'BAROX-VS-v042.jar'" in read('build.gradle')
assert 'mod_version=0.42.0' in read('gradle.properties')
assert read('VERSION').strip() == 'BAROX VS v042'
assert read('BUILD_VERSION.txt').strip() == 'BAROX VS v042'
assert read('README.md').startswith('# BAROX VS — v042')
assert '## v042 — Liquid Glass Optical System & Visual Power' in read('README.md')
assert 'private static LiteralArgumentBuilder<FabricClientCommandSource> powerCommand' in chat
assert 'ClientCommandManager.literal("power")' in chat
assert 'config.setModuleValue(owner, "intensity", value, 0.55f, 1.85f)' in chat
assert 'String intensityOwner(String moduleId)' in chat
assert (root / 'LIQUID_GLASS_v042.md').is_file()

print('v042 checks passed: 99 stable module IDs / 14 groups / 50 child features; iOS-inspired layered glass; per-module alpha + exposure power; all cosmetic and sky effect families wired; per-widget HUD inheritance; TR/DE/EN parity; version stamps')
