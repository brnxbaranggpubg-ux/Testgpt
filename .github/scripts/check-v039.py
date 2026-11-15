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
assert len(ids) == len(set(ids)) == 99, f'expected 99 unique modules; got {len(ids)} declarations / {len(set(ids))} ids'
groups = re.findall(r'group\("([a-z0-9_]+)"\s*,([^;]+)\);', catalog)
children = []
for parent, raw in groups:
    child_ids = re.findall(r'"([a-z0-9_]+)"', raw)
    assert parent in ids, f'missing group parent: {parent}'
    assert child_ids, f'empty group: {parent}'
    children.extend(child_ids)
assert len(groups) == 14, f'expected 14 groups, got {len(groups)}'
assert len(children) == len(set(children)) == 50, f'expected 50 uniquely grouped children, got {len(children)}'
assert len(set(ids) - set(children)) == 49, 'top-level menu count must be 49'
assert 'public static synchronized List<Module> all()' in catalog
assert 'public static synchronized List<Module> visible()' in catalog
assert 'public static synchronized List<Module> childrenOf(String parentId)' in catalog
assert 'GROUP_PARENT.containsKey(m.id())' in catalog
assert 'GROUP_PARENT.containsKey(module.id())' in catalog
assert 'validateCatalog()' in catalog

# Validate each group identity and its owning master switch.
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
assert found == expected, 'group membership mismatch'

# Every grouped feature must be removed from the standalone module browser and searchable via its parent.
for src, name in ((click,'ClickGUI'), (menu,'main menu'), (hud,'Active Visuals')):
    assert 'ModuleCatalog.visible()' in src or 'ModuleCatalog.inCategory(' in src, f'{name} does not use grouped catalogue'
assert 'ModuleCatalog.childrenOf(module.id())' in click, 'nested search missing in ClickGUI'
assert 'ModuleCatalog.childrenOf(m.id())' in menu, 'nested search missing in main menu'
assert 'ModuleCatalog.childrenOf(parentId)' in settings
assert 'Control.childToggle(child)' in settings and 'Control.childStyle(child)' in settings
assert 'config.isOn("player_glass")' in engine
assert 'config.isOn("head_accessories")' in engine
assert 'config.isOn("pet") && config.isOn("butterfly_companion")' in engine
assert 'config.isOn("halo") && config.isOn("cosmic_halo")' in engine
assert 'config.isOn("aura") && config.isOn("music_aura_sync")' in engine
assert 'if (!config.isOn("ambient_forms")) return;' in engine
assert 'if (!cfg.isOn("sky_studio")) return;' in sky
assert 'cfg.isOn("music_card") && cfg.isOn("lyric_flow")' in hud
assert 'cfg.isOn("crosshair_ring") && cfg.isOn("crosshair_studio")' in hud
assert 'for (ModuleCatalog.Module module : ModuleCatalog.all())' in read('src/main/java/com/baroxvs/client/config/BaroxConfig.java'), 'config must keep legacy child IDs'

# Parent settings must expose each child's switches/styles and preserve child-owned setting keys.
for token in ('settings.integrated_components','headwearExtraScale','chineseHatExtraScale','hanfuScale',
              'butterflyScale','cosmicHaloScale','musicAuraScale','handGlowScale','armGlowScale',
              'heldGlowScale','selfGlassScale','auroraOpacity','starDensity','constellationOpacity'):
    assert token in settings, f'missing grouped setting: {token}'
assert 'config.setModuleValue("headwear", "scale"' in settings
assert 'config.setModuleValue("chinese_hat", "scale"' in settings
assert 'config.setModuleValue("hanfu_ornament", "scale"' in settings
assert 'config.setModuleValue("butterfly_companion", "scale"' in settings
assert 'config.setModuleValue("cosmic_halo", "scale"' in settings

# Legacy external settings pages must not expose the same grouped children as standalone controls.
for forbidden in ('"wing_membrane"','"wing_outline"','"wing_harness"','"wing_runes"','"headwear"'):
    assert forbidden not in cloth, f'legacy standalone child still in Cloth Config: {forbidden}'
assert 'drawCyclePill' not in menu, 'old ambient controls still shown outside Ambient Glass parent'

lang = root / 'src/main/resources/assets/baroxvs/lang'
data = {name: json.loads((lang/name).read_text(encoding='utf-8')) for name in ('en_us.json','de_de.json','tr_tr.json')}
keys = set(data['en_us.json'])
assert all(set(value) == keys for value in data.values()), 'locale keys differ'
assert all('baroxvs.module.head_accessories' in value for value in data.values())
assert all('baroxvs.settings.integrated_components' in value for value in data.values())

assert 'BAROX-VS-v039.jar' in read('build.gradle')
assert 'mod_version=0.39.0' in read('gradle.properties')
assert read('VERSION').strip() == 'BAROX VS v039'
assert read('BUILD_VERSION.txt').strip() == 'BAROX VS v039'
assert read('README.md').startswith('# BAROX VS — v039')
assert '49 top-level modules across 14 groups' in read('README.md')

print('v039 checks passed: 99 modules, 14 parent groups, 50 nested features, 49 visible modules, render gates, settings, config compatibility and locale parity')