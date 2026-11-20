#!/usr/bin/env python3
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
cosmetic = (root / 'src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java').read_text(encoding='utf-8')
hud = (root / 'src/main/java/com/baroxvs/client/hud/HudRenderer.java').read_text(encoding='utf-8')
catalog = (root / 'src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java').read_text(encoding='utf-8')
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([^"]+)"', catalog)
assert len(ids) == 99, f'expected 99 registered module declarations, found {len(ids)}'
assert len(set(ids)) == 99, 'module IDs must remain unique'

checks = {
    'Meteor Glow layered wake ribbons': 'Two offset, phase-linked wake ribbons' in cosmetic,
    'Prism Trail braided edge facets': 'Paired raised edge facets' in cosmetic,
    'Halo Bloom moving crystal crown': 'Three moving crystal petals' in cosmetic,
    'Nameplate Designer travelling crest': 'double crestTravel = Math.sin(time * 0.052)' in cosmetic,
    'Biome Discovery orbiting badge pips': 'Three orbiting glass pips' in hud,
    'version archive': "archiveFileName = 'BAROX-VS-v086.jar'" in (root / 'build.gradle').read_text(encoding='utf-8'),
    'version property': 'mod_version=0.86.0' in (root / 'gradle.properties').read_text(encoding='utf-8'),
    'version markers': 'BAROX VS v086' in (root / 'VERSION').read_text(encoding='utf-8') and 'BAROX VS v086' in (root / 'BUILD_VERSION.txt').read_text(encoding='utf-8'),
}
for label, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + label)
assert all(checks.values()), 'one or more v086 invariants failed'
print(f'PASS: {len(ids)} unique module IDs retained')
