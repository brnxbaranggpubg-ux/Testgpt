#!/usr/bin/env python3
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
base = root / "src/main/java/com/baroxvs/client"
engine = (base / "cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
gui = (base / "gui/ModuleSettingsScreen.java").read_text(encoding="utf-8")
catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
config = (base / "config/BaroxConfig.java").read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(ids) == len(set(ids)) == 99, f"module declarations changed: {len(ids)} / {len(set(ids))} unique"
for module_id in ("liquid_rain", "silk_ribbons", "glint", "player_glass", "held_item_glow"):
    assert ids.count(module_id) == 1, f"missing or duplicated module ID: {module_id}"
assert '"liquid_rain"' in config and '"silk_ribbons"' in config

# Wet World: droplets and ground water must use distinct material passes.
assert 'RenderLayer.getEntityTranslucent(LIQUID_GLASS_TEXTURE)' in engine
assert 'RenderLayer.getEntityTranslucent(COSMETIC_TEXTURE)' in engine
assert 'renderLiquidGlassRain(rainOutput, camera, player, partial, client)' in engine
assert 'renderWetGround(wetGroundOutput, camera, player, partial, client)' in engine
rain = engine[engine.index('private void renderLiquidGlassRain('):engine.index('private void renderWetGround(')]
wet = engine[engine.index('private void renderWetGround('):engine.index('private static void drawPuddleRipple(')]
assert 'drawGlassRaindrop(out,' in rain
assert 'drawGlassEllipsoid(out, camera, puddle' not in rain and 'drawGlassEllipsoidRim(' not in rain, 'ground ellipsoids must not use the faint rain texture'
for token in ('drawWetPuddleFilm(', 'drawGlassEllipsoid(out, camera, puddle', 'drawGlassEllipsoidRim(out, camera, puddle',
              'drawPuddleRipple(out, camera, puddle', 'Math.min(22', '0.84f'):
    assert token in wet, f"Wet World ground pass missing: {token}"
assert 'private static void drawWetPuddleFilm(' in engine
assert 'config.moduleValue(module.id(), "opacity", 0.84f, 0.10f, 0.90f)' in gui
assert 'Visible reflective water films' in catalog

# Silk Veil: centreline/tangent frame, stable projected axes and reverse winding.
silk = engine[engine.index('private void renderSilkRibbons('):engine.index('private static final int[][] CAPE_PALETTES')]
for token in ('Vec3d[] centres = new Vec3d[segments + 1]', 'qualitySegments(24)',
              'after.subtract(before)', 'playerBack.subtract(tangent.multiply(playerBack.dotProduct(tangent)))',
              'tangent.crossProduct(projectedBack)', 'emitQuad(out, camera, left, rightEdge, previousRight, previousLeft',
              'emitQuad(out, camera, sheenLeft, sheenRight, previousSheenRight, previousSheenLeft'):
    assert token in silk, f"Silk Veil frame repair missing: {token}"
assert 'back.multiply(Math.cos(twist)).add(up.multiply(Math.sin(twist)))' not in silk
assert 'stable body-framed cloth motion' in catalog
assert '"silk_ribbons"' in config

assert "BAROX-VS-v095.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=0.95.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v095"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v095"
assert (root / "RENDER_REPAIR_v095.md").is_file()
print("v095 checks passed: separate bright Wet World ground pass, expanded puddle films/reflections/ripples, stable double-sided Silk Veil frame, 99 unique module IDs and version stamps")
