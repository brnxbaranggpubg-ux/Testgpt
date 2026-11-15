#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
read = lambda p: (root / p).read_text(encoding='utf-8')
catalog = read('src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java')
engine = read('src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java')
settings = read('src/main/java/com/baroxvs/client/gui/ModuleSettingsScreen.java')
click = read('src/main/java/com/baroxvs/client/gui/ModuleClickGuiScreen.java')
menu = read('src/main/java/com/baroxvs/client/gui/BaroxMenuScreen.java')
hud = read('src/main/java/com/baroxvs/client/hud/HudRenderer.java')
sky = read('src/main/java/com/baroxvs/client/render/SkyboxEngine.java')
cloth = read('src/main/java/com/baroxvs/client/gui/BaroxClothConfigScreen.java')

ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(ids) == len(set(ids)) == 99, f'expected 99 unique module IDs, got {len(ids)} declarations / {len(set(ids))} unique'
groups = re.findall(r'group\("([a-z0-9_]+)"\s*,([^;]+)\);', catalog)
children = []
for parent, raw in groups:
    child_ids = re.findall(r'"([a-z0-9_]+)"', raw)
    assert parent in ids, f'missing group parent: {parent}'
    assert child_ids, f'empty group: {parent}'
    children.extend(child_ids)
assert len(groups) == 14, f'expected 14 parent groups, got {len(groups)}'
assert len(children) == len(set(children)) == 50, f'expected 50 unique nested features, got {len(children)}'
assert len(set(ids) - set(children)) == 49, 'expected 49 top-level modules'
assert 'public static synchronized List<Module> all()' in catalog
assert 'public static synchronized List<Module> visible()' in catalog
assert 'public static synchronized List<Module> childrenOf(String parentId)' in catalog
assert 'validateCatalog()' in catalog

expected = {
    'wings': {'wing_motion','wing_glints','wing_outline','wing_runes','wing_harness','wing_membrane','wing_size'},
    'head_accessories': {'headwear','chinese_hat','hanfu_ornament'},
    'pet': {'pet_motion','pet_glow','butterfly_companion'},
    'halo': {'cosmic_halo'},
    'sky_studio': {'custom_sky','sky_time_cycle','sky_aurora','sky_stars','sky_fog','sky_horizon_glow','sky_nebula','sky_meteors','sky_constellations'},
    'player_glass': {'hand_glow','arm_glow','held_item_glow','self_glass'},
    'aura': {'aura_pulse','music_aura_sync'},
    'ambient_forms': {'ambient_density','ambient_range','ambient_shape','ambient_palette','ambient_bounce','sky_mood'},
    'status_bar': {'fps','direction','biome','ping','local_clock'},
    'coordinates': {'nether_coords'},
    'world_card': {'world_dimension','world_biome','world_weather','world_time'},
    'player_status': {'health_status','hunger_status','experience_status'},
    'music_card': {'lyric_flow'},
    'crosshair_ring': {'crosshair_studio'},
}
found = {p:set(re.findall(r'"([a-z0-9_]+)"', raw)) for p, raw in groups}
assert found == expected, 'parent/child module family changed unexpectedly'

# Grouped UI and parent settings remain wired.
assert 'ModuleCatalog.childrenOf(module.id())' in click
assert 'ModuleCatalog.childrenOf(m.id())' in menu
assert 'ModuleCatalog.childrenOf(parentId)' in settings
assert 'Control.childToggle(child)' in settings and 'Control.childStyle(child)' in settings
assert 'for (ModuleCatalog.Module module : ModuleCatalog.all())' in read('src/main/java/com/baroxvs/client/config/BaroxConfig.java')
for forbidden in ('"wing_membrane"','"wing_outline"','"wing_harness"','"wing_runes"','"headwear"'):
    assert forbidden not in cloth, f'legacy standalone control still exposed: {forbidden}'

# Zero transient particle systems and no vanilla particle API calls.
for token in ('VisualMote', 'TrailNode', 'JumpRipple', 'activeVisualMoteCount', 'renderVisualMotes(',
              'updateVisualMotes(', 'renderPrismTrailRibbon(', 'addParticle(', 'ParticleTypes.',
              'ParticleEffect', 'ParticleManager'):
    assert token not in engine, f'legacy particle/trail runtime remains: {token}'
# A jump pulse is calculated directly from the player's grounded/airborne state, not queued objects.
assert 'private void renderJumpPulse(' in engine
assert 'jumpPulseTick' in engine
assert 'new ArrayList' not in engine and 'Iterator<' not in engine and 'List<' not in engine

# No line/ring drawing helpers in the cosmetic, sky or HUD renderers.
for source, label in ((engine, 'CosmeticEngine'), (sky, 'SkyboxEngine'), (hud, 'HudRenderer')):
    for token in ('ribbon(', 'drawRing(', 'emitThinQuad(', 'Ui.line(', 'Ui.ring('):
        assert token not in source, f'{label} still uses stroke primitive {token}'
assert 'surfaceBloom(' in engine
assert 'drawSoftDisc(' in engine
assert 'drawGlassOrb(' in engine and 'spherePoint(' in engine
assert 'drawSoftSkyBlob(' in sky
assert 'STAR_DIRECTIONS' not in sky and 'CONSTELLATION_POINTS' not in sky and 'makeStars()' not in sky
assert 'styleGraphLine' not in hud
assert 'Ui.roundRect(c, gx, top' in hud

# Core visual features use surfaces instead of line/point variants.
for token in ('"Wing Surface"', '"Wing Relief"', '"Aura Bloom"', '"Crosshair Bloom"',
              '"Meteor Glow"', '"Ambient Fields"', '"Soft Bars"', '"Diffuse Glow"'):
    assert token in catalog, f'missing new smooth visual option: {token}'

lang = root / 'src/main/resources/assets/baroxvs/lang'
data = {name: json.loads((lang/name).read_text(encoding='utf-8')) for name in ('en_us.json','de_de.json','tr_tr.json')}
keys = set(data['en_us.json'])
assert all(set(value) == keys for value in data.values()), 'locale key sets differ'
assert all('hud.debug.visual' in value and 'hud.debug.smooth' in value for value in data.values())
assert all('baroxvs.module.wing_outline' in value for value in data.values())
assert all('baroxvs.module.sky_aurora.description' in value for value in data.values())

assert 'BAROX-VS-v040.jar' in read('build.gradle')
assert 'mod_version=0.40.0' in read('gradle.properties')
assert read('VERSION').strip() == 'BAROX VS v040'
assert read('BUILD_VERSION.txt').strip() == 'BAROX VS v040'
assert read('README.md').startswith('# BAROX VS — v040')
assert '## v040 — Smooth Surface Visual Rewrite' in read('README.md')
assert (root/'SURFACE_RENDERING_v040.md').exists()

print('v040 checks passed: 99 modules / 14 groups / 50 child features; zero particle runtime; no stroke renderer; soft-surface primitives; locales and version stamps')