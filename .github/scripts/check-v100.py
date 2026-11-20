#!/usr/bin/env python3
import re, sys
from pathlib import Path
root=Path(sys.argv[1])
base=root/'src/main/java/com/baroxvs/client'
engine=(base/'cosmetic/CosmeticEngine.java').read_text(encoding='utf-8')
catalog=(base/'cosmetic/ModuleCatalog.java').read_text(encoding='utf-8')
client=(base/'BaroxVsClient.java').read_text(encoding='utf-8')
config=(base/'config/BaroxConfig.java').read_text(encoding='utf-8')
ids=re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"',catalog)
assert len(ids)==len(set(ids))==99, f'module IDs changed: {len(ids)}/{len(set(ids))}'
for mid in ('head_accessories','headwear','chinese_hat','hanfu_ornament','silk_ribbons'):
    assert ids.count(mid)==1, mid
assert 'ModuleCatalog.isGroupedChild(id)' in client and 'ModuleCatalog.parentOf(id)' in client
assert 'CONFIG.setOn(parent, true)' in client
assert '"head_accessories".equals(id)' in client and 'CONFIG.setOn("headwear", true)' in client
assert 'modules.put("head_accessories", true)' in config
assert 'private static double headAccessoryAnchorY(PlayerEntity player)' in engine
for method_start, method_end in [
    ('private void renderChineseHat(', 'private void renderHeadwear('),
    ('private void renderHeadwear(', 'private Vec3d wingPose('),
    ('private void renderHanfuOrnament(', 'private void renderSilkRibbons(')
]:
    body=engine[engine.index(method_start):engine.index(method_end,engine.index(method_start))]
    assert 'headAccessoryAnchorY(' in body, method_start
silk=engine[engine.index('private void renderSilkRibbons('):engine.index('private static final int[][] CAPE_PALETTES')]
for token in ('player.prevBodyYaw','player.bodyYaw','playerRight','projectedRight','projectedDepth',
              'emitSilkDoubleSidedQuad','emitQuadWithNormal','0.285 + 0.045 * t','0.205 + 0.135 * t'):
    assert token in silk, token
assert 'projectedBack' not in silk, 'Silk width axis still relies on projected back axis'
assert '0.48 + 0.12 * t' not in silk, 'old detached side anchors remain'
assert 'emitVertex(out, camera, position, color, WORLD_UP)' in engine
assert 'int color, Vec3d normal) {' in engine
assert 'BAROX-VS-v100.jar' in (root/'build.gradle').read_text()
assert 'mod_version=1.00.0' in (root/'gradle.properties').read_text()
assert (root/'VERSION').read_text().strip()=='BAROX VS v100'
assert (root/'BUILD_VERSION.txt').read_text().strip()=='BAROX VS v100'
assert (root/'RENDER_REPAIR_v100.md').is_file()
print('v100 checks passed: head accessory parent/child activation, pose-aware head anchors, rear-facing lateral silk panels, normal-aware double-sided mesh and 99 unique module IDs')