#!/usr/bin/env python3
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
base = root / "src/main/java/com/baroxvs/client"
engine = (base / "cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
held = (base / "render/HeldItemGlassRenderer.java").read_text(encoding="utf-8")
catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
settings = (base / "gui/ModuleSettingsScreen.java").read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(ids) == len(set(ids)) == 99, f"module declarations changed: {len(ids)} / {len(set(ids))} unique"
assert ids.count("liquid_rain") == 1 and ids.count("held_item_glow") == 1 and ids.count("cape") == 1

# Held-item glass never samples its former low-alpha overlay texture and uses declared face normals.
assert "RenderLayer.getEntityTranslucent(WHITE_TEXTURE)" in held
assert "held_item_glass.png" not in held and "MATERIAL" not in held
assert "float nx = face.getOffsetX();" in held and "float ny = face.getOffsetY();" in held
assert "int packed = data[offset + 7]" not in held
assert "float bodyAlpha = 0.018f + (1.0f - settings.transmission()) * 0.012f;" in held
assert "Math.min(0.34f, alpha)" in held
assert held.count("LightmapTextureManager.MAX_LIGHT_COORDINATE") == 2

# Wet World is a continuous chunk mesh, not per-frame circular puddle tessellation.
wet = engine[engine.index("private void renderWetGround("):engine.index("/** Tapered drop shell", engine.index("private void renderWetGround("))]
for token in ("WET_CHUNK_RADIUS", "WET_CHUNK_BUILDS_PER_FRAME", "wetSurfaceMeshes.get(key)",
              "buildWetSurfaceMesh(world, chunkX, chunkZ)", "WET_CHUNK_REFRESH_TICKS", "MOTION_BLOCKING",
              "mesh.addQuad(", "mesh.vertexCount", "LightmapTextureManager.MAX_LIGHT_COORDINATE"):
    assert token in wet, f"cached surface coating missing {token}"
for forbidden in ("puddleCount", "drawWetPuddleFilm", "drawPuddleRipple", "drawGlassEllipsoid", "drawGlassTorus"):
    assert forbidden not in wet, f"old puddle tessellation still present: {forbidden}"
assert "WET_CHUNK_BUILDS_PER_FRAME = 2" in engine
assert "private static final int[] WET_CHUNK_ORDER = {0, -1, 1};" in engine
assert "0x88" in wet and "0x68" in wet
rain = engine[engine.index("private void renderLiquidGlassRain("):engine.index("private void renderWetGround(")]
assert "Math.min(24" in rain

# Supplied v098 cape crash: request the logo layer only after the white cape body is finished.
world = engine[engine.index("private void renderWorldEffects("):engine.index("private boolean hasRenderableWorldEffects(")]
assert world.index("renderAmbientGeometry(output") < world.index("renderCape(output, context.consumers()")
cape = engine[engine.index("private void renderCape("):engine.index("private static void renderCapeSponsorLogo(")]
assert cape.index("drawDiamond(out") < cape.index("consumers.getBuffer(RenderLayer.getEntityTranslucent(CAPE_LOGO_TEXTURE))")
assert "VertexConsumer logoOut" in cape

assert '"liquid_rain"' in settings
assert "Liquid surface coverage" in settings
assert "Surface sheen scale" in settings
assert "BAROX-VS-v099.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=0.99.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v099"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v099"
assert (root / "RENDER_REPAIR_v099.md").is_file()
assert (root / "WET_WORLD_v099.md").is_file()
print("v099 checks passed: GLES-safe held-item highlight pass, chunk-cached liquid film, cape buffer lifecycle repair and 99 unique module IDs")