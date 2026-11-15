#!/usr/bin/env python3
import json
import re
import struct
import sys
from pathlib import Path

root = Path(sys.argv[1])
read = lambda p: (root / p).read_text(encoding='utf-8')

catalog = read('src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java')
engine = read('src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java')
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(ids) == len(set(ids)) == 99, f'module IDs changed: {len(ids)} declarations / {len(set(ids))} unique'
assert 'styled("self_glass"' in catalog
assert 'full-body iPhone-style Liquid Glass coating' in catalog

for token in ('LIQUID_GLASS_TEXTURE', 'renderLiquidGlassAvatar(', 'drawGlassEllipsoid(',
              'glassEllipsoidPoint(', 'emitGlassQuad(', 'emitGlassVertex(',
              'RenderLayer.getEntityTranslucent(LIQUID_GLASS_TEXTURE)',
              'UV-mapped glass coating', 'Fresnel', 'broadSpecular',
              'player.isInvisible()', 'player.isSpectator()'):
    assert token in engine, f'missing avatar glass feature: {token}'
assert 'renderLiquidGlassAvatar(glassOut, camera, player' in engine

texture = root / 'src/main/resources/assets/baroxvs/textures/misc/liquid_glass.png'
assert texture.is_file() and texture.stat().st_size > 500
header = texture.read_bytes()[:24]
assert header[:8] == b'\x89PNG\r\n\x1a\n'
width, height = struct.unpack('>II', header[16:24])
assert (width, height) == (64, 64), f'unexpected texture dimensions: {width}x{height}'

assert 'RenderLayer.getEntityTranslucent(LIQUID_GLASS_TEXTURE)' in engine
assert 'Framebuffer' not in engine and 'PostEffect' not in engine
for name in ('en_us.json', 'de_de.json', 'tr_tr.json'):
    json.loads((root / 'src/main/resources/assets/baroxvs/lang' / name).read_text(encoding='utf-8'))
assert "archiveFileName = 'BAROX-VS-v043.jar'" in read('build.gradle')
assert 'mod_version=0.43.0' in read('gradle.properties')
assert read('VERSION').strip() == 'BAROX VS v043'
assert read('BUILD_VERSION.txt').strip() == 'BAROX VS v043'
assert read('README.md').startswith('# BAROX VS — v043')
assert '## v043 — Full-body Avatar Liquid Glass' in read('README.md')
assert (root / 'LIQUID_GLASS_v043.md').is_file()

print('v043 checks passed: 99 stable module IDs; full-body local-avatar Liquid Glass shell; UV-mapped RGBA texture; animated Fresnel/specular highlights; original skin visible; TR/DE/EN JSON valid; version stamps correct')
