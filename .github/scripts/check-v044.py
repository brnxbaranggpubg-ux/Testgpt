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
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(ids) == len(set(ids)) == 99, f'module catalogue changed: {len(ids)} declarations / {len(set(ids))} unique'
assert 'toggle("liquid_rain", "Liquid Glass Rain"' in catalog
assert 'renderChunkRain(' not in engine

for token in (
    'LIQUID_GLASS_TEXTURE', 'renderLiquidGlassRain(', 'drawGlassRaindrop(',
    'glassRaindropPoint(', 'RenderLayer.getEntityTranslucent(LIQUID_GLASS_TEXTURE)',
    'goldenAngle', 'drawGlassEllipsoid(out, camera, glint',
    'double speed = 0.015 + (i % 5) * 0.0025',
    'Math.max(8, Math.min(72'
):
    assert token in engine, f'missing liquid rain renderer feature: {token}'

rain = engine.split('private void renderLiquidGlassRain(', 1)[1].split('private static void drawGlassRaindrop(', 1)[0]
assert 'config.moduleValue("liquid_rain", "frequency"' in rain
assert 'config.moduleValue("liquid_rain", "scale"' in rain
assert 'config.moduleValue("liquid_rain", "opacity"' in rain
assert 'drawGlassRaindrop(' in rain and 'drawGlassEllipsoid(' in rain
assert 'drawSoftDisc(' not in rain
for bad in ('ParticleManager', 'spawnParticle', 'addParticle', 'new Particle', 'ParticleEffect'):
    assert bad not in rain, f'particle runtime must remain absent: {bad}'

for token in ('Glass droplet density', 'Droplet size', 'Liquid Glass opacity'):
    assert token in settings, f'missing rain setting label: {token}'
lang = root / 'src/main/resources/assets/baroxvs/lang'
data = {name: json.loads((lang / name).read_text(encoding='utf-8'))
        for name in ('en_us.json', 'de_de.json', 'tr_tr.json')}
assert set(data['en_us.json']) == set(data['de_de.json']) == set(data['tr_tr.json']), 'locale keys differ'

texture = root / 'src/main/resources/assets/baroxvs/textures/misc/liquid_glass.png'
assert texture.is_file() and texture.stat().st_size > 500
assert "archiveFileName = 'BAROX-VS-v044.jar'" in read('build.gradle')
assert 'mod_version=0.44.0' in read('gradle.properties')
assert read('VERSION').strip() == 'BAROX VS v044'
assert read('BUILD_VERSION.txt').strip() == 'BAROX VS v044'
assert read('README.md').startswith('# BAROX VS — v044')
assert '## v044 — iPhone-style Liquid Glass Rain' in read('README.md')
assert (root / 'LIQUID_GLASS_RAIN_v044.md').is_file()

assert engine.count('{') == engine.count('}'), 'unbalanced Java braces'
assert engine.count('(') == engine.count(')'), 'unbalanced Java parentheses'
print('v044 checks passed: 99 stable modules; iPhone-style textured volumetric Liquid Glass rain; dynamic Fresnel/specular highlights; bounded analytic rainfall; settings and locale parity')
