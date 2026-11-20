#!/usr/bin/env python3
import re, sys
from pathlib import Path
root=Path(sys.argv[1])
base=root/"src/main/java/com/baroxvs/client"
engine=(base/"cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
catalog=(base/"cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
hud=(base/"hud/HudRenderer.java").read_text(encoding="utf-8")
mixin=(base/"mixin/InGameHudMixin.java").read_text(encoding="utf-8")
mixins=(root/"src/main/resources/baroxvs.mixins.json").read_text(encoding="utf-8")
ids=re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"',catalog)
assert len(ids)==len(set(ids))==99, f"module IDs: {len(ids)} / {len(set(ids))}"
for mid in ("crosshair_ring","crosshair_studio","nameplate_designer","prism_trail"):
 assert ids.count(mid)==1, mid
assert 'if (cfg.isOn("crosshair_studio")) {' in hud
assert '} else if (cfg.isOn("crosshair_ring")) {' in hud
studio=hud[hud.index('private void drawCrosshairStudio('):hud.index('// ------------------------------------------------------------------ Kimiko-inspired local HUD additions')]
for token in ("case 0 ->","case 1 ->","case 2 ->","case 3 ->","default ->","Ui.roundRect","Ui.ring"):
 assert token in studio, token
assert "orbitRadius" not in studio and "satellite" not in studio
assert "renderCrosshair(Lnet/minecraft/client/gui/DrawContext;Lnet/minecraft/client/render/RenderTickCounter;)V" in mixin
assert 'config.isOn("crosshair_studio") || config.isOn("crosshair_ring")' in mixin
assert '"InGameHudMixin"' in mixins
assert '"A clean five-style reticle that replaces the vanilla crosshair while active"' in catalog
nameplate=engine[engine.index('private void drawPlayerNameplate('):engine.index('private static int qualityCount(')]
for token in ("double pixel = 0.0145 * scale","double height = 0.30 * scale",
              "textFace = face.add(view.multiply(0.006 * scale))","row < 7","col < 5",
              "private static long glyphBitmap","case 'A' -> 0x3A31FC631L","case 'Z' -> 0x7C222221FL"):
 assert token in nameplate, token
assert "safeName.length() > 16" in engine
assert "glyph5x7" not in engine
assert "row < 5" not in nameplate and "col < 3" not in nameplate
assert "PRISM_TRAIL_CAPACITY = 48" in engine
assert "PRISM_TRAIL_LIFETIME_TICKS = 42.0" in engine
assert "PRISM_TRAIL_SAMPLE_DISTANCE_SQ = 0.0004" in engine
assert "renderPrismTrail(output, camera, tick + partial" in engine
assert engine.count("renderPrismTrail(")==2
assert "horizontalDistanceSq >= PRISM_TRAIL_SAMPLE_DISTANCE_SQ" in engine
assert "subdivisions = Math.max(1, Math.min(6" in engine
assert "horizontalDistanceSq > 16.0" in engine
block=engine[engine.index('if (!config.isOn("prism_trail")) {',engine.index('private void updateVisualHistories')):engine.index('private void appendPrismTrailSample')]
assert "speed < 0.012" not in block
trail=engine[engine.index('private void renderPrismTrail('):engine.index('private void drawPlayerNameplate(')]
for token in ("PRISM_TRAIL_LIFETIME_TICKS","halfWidth = 0.072","coreCentre","facetCentre"):
 assert token in trail, token
assert "BAROX-VS-v098.jar" in (root/"build.gradle").read_text()
assert "mod_version=0.98.0" in (root/"gradle.properties").read_text()
assert (root/"VERSION").read_text().strip()=="BAROX VS v098"
assert (root/"BUILD_VERSION.txt").read_text().strip()=="BAROX VS v098"
assert (root/"RENDER_REPAIR_v098.md").is_file()
print("v098 checks passed: vanilla crosshair replacement, z-fight-free 5x7 nametag, displacement-driven Prism Trail and 99 unique module IDs")
