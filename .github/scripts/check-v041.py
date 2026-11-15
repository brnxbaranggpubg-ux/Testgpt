#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
read = lambda p: (root / p).read_text(encoding='utf-8')
client = read('src/main/java/com/baroxvs/client/BaroxVsClient.java')
commands = read('src/main/java/com/baroxvs/client/HudChatCommands.java')
hud = read('src/main/java/com/baroxvs/client/hud/HudRenderer.java')
engine = read('src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java')
catalog = read('src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java')

# Preserve the complete v040 catalogue and the existing config-backed independent transforms.
ids = set(re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog))
assert len(ids) == 99, f'expected 99 stable module IDs, got {len(ids)}'
renderer_widgets = set(re.findall(r'withWidget\(c, sw, sh, "([a-z0-9_]+)"', hud))
command_widgets = set(re.findall(r'"([a-z0-9_]+)"', commands.split('private static final List<String> GLASS')[0].split('WIDGETS = List.of(')[1]))
assert command_widgets == renderer_widgets - {'hit_numbers'}, 'chat widget map must cover every live HUD widget except the retired module'
assert command_widgets <= ids, f'chat references widgets missing from the module catalogue: {sorted(command_widgets - ids)}'
for setting in ('"x"', '"y"', '"scale"', '"opacity"', '"glass"'):
    assert setting in commands
for token in ('/barox hud move', '/barox hud scale', '/barox hud opacity', '/barox hud glass',
              '/barox hud toggle', '/barox hud visible', '/barox hud reset'):
    assert token in commands, f'missing chat command help: {token}'
assert 'ClientCommandRegistrationCallback.EVENT.register' in commands
assert 'HudChatCommands.register(CONFIG)' in client
assert 'GLFW_KEY_T' not in client and 'openHudEditorKey' not in client
assert 'new HudEditorScreen' not in client, 'T must not open the full-screen editor'

# Each widget uses independent X/Y, scale, opacity and a selected glass material.
for token in ('moduleValue(moduleId, "scale"', 'moduleValue(moduleId, "x"',
              'moduleValue(moduleId, "y"', 'moduleValue(moduleId, "opacity"',
              'moduleValue(moduleId, "glass"'):
    assert token in hud, f'missing per-widget renderer property: {token}'
assert 'activeWidgetGlassStyle = Math.round' in hud
assert 'int style = activeWidgetGlassStyle' in hud
assert 'config.values.remove("module." + id + "." + property)' in commands

# The redesigned Chinese Kasa keeps its original module ID/configuration while upgrading its shape.
assert 'private void renderChineseHat(' in engine
for token in ('double[] crownRadii', 'gently curved, double-layer canopy', 'lotus-and-pearl crown ornament',
              'Symmetric jade side drops', 'tasselBottom', 'config.moduleValue("chinese_hat", "tassel"'):
    assert token in engine, f'missing Chinese Kasa redesign feature: {token}'
assert 'chinese_hat' in catalog

# Locale parity and release metadata remain valid.
lang = root / 'src/main/resources/assets/baroxvs/lang'
data = {name: json.loads((lang / name).read_text(encoding='utf-8'))
        for name in ('en_us.json', 'de_de.json', 'tr_tr.json')}
keys = set(data['en_us.json'])
assert all(set(values) == keys for values in data.values()), 'TR/DE/EN locale keys differ'
assert 'BAROX-VS-v041.jar' in read('build.gradle')
assert 'mod_version=0.41.0' in read('gradle.properties')
assert read('VERSION').strip() == 'BAROX VS v041'
assert read('BUILD_VERSION.txt').strip() == 'BAROX VS v041'
assert read('README.md').startswith('# BAROX VS — v041')
assert '## v041 — Chat HUD Studio & Imperial Kasa' in read('README.md')

print(f'v041 checks passed: {len(ids)} stable module IDs; {len(command_widgets)} individually editable HUD widgets; T keeps vanilla chat; per-widget Liquid Glass; Chinese Kasa redesign; TR/DE/EN locale parity')
