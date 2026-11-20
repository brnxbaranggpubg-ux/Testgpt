from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1])
resources = root / "src/main/resources"
java = root / "src/main/java/com/baroxvs/client"

metadata = json.loads((resources / "fabric.mod.json").read_text(encoding="utf-8"))
assert metadata["depends"]["minecraft"] == "1.21.4"
assert metadata["depends"]["java"] == ">=21"

mixins = json.loads((resources / "baroxvs.mixins.json").read_text(encoding="utf-8"))
client_mixins = set(mixins["client"])
required_mixins = {
    "SkyRenderingMixin", "BackgroundRendererMixin", "InGameHudMixin",
    "HeldItemFirstPersonGlassMixin", "PlayerHeldItemGlassMixin",
    "ItemLayerGlassMixin", "PlayerGlassMixin",
}
assert required_mixins.issubset(client_mixins)
assert mixins["required"] is True and mixins["injectors"]["defaultRequire"] == 1

cosmetic = (java / "cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
cloth = (java / "cosmetic/CapeClothSimulation.java").read_text(encoding="utf-8")
held = (java / "render/HeldItemGlassRenderer.java").read_text(encoding="utf-8")
sky = (java / "render/SkyboxEngine.java").read_text(encoding="utf-8")
sky_mixin = (java / "mixin/SkyRenderingMixin.java").read_text(encoding="utf-8")
fog_mixin = (java / "mixin/BackgroundRendererMixin.java").read_text(encoding="utf-8")
hud_mixin = (java / "mixin/InGameHudMixin.java").read_text(encoding="utf-8")
hud = (java / "hud/HudRenderer.java").read_text(encoding="utf-8")

# Cape physics and render-buffer lifecycle.
assert "-0.0105 - vertical * 0.0014 + lagVertical * 0.013" in cloth
assert "private void renderCape(VertexConsumer out, VertexConsumerProvider consumers" in cosmetic
assert "consumers instanceof VertexConsumerProvider.Immediate immediate" in cosmetic
assert "immediate.draw(bodyLayer);" in cosmetic and "immediate.draw(logoLayer);" in cosmetic
assert (resources / "assets/baroxvs/textures/misc/cape_body.png").is_file()
assert (resources / "assets/baroxvs/textures/misc/cape_logo.png").is_file()

# Baked item atlas/UV/alpha and glint, no leaked RenderSystem state.
assert "quad.getSprite()" in held and "sprite.getAtlasId()" in held
assert "multiplyRgb(tint, sourceColor)" in held
assert "sourceAlpha = ((sourceColor >>> 24) & 255) / 255.0f" in held
assert "consumers.getBuffer(RenderLayer.getEntityTranslucent(atlas))" in held
assert "setQuadNormal(data, stride, face, entry, normal)" in held
assert "frames.clear();" in held and "frames.push(new Frame(settings, glint));" in held
assert "RenderSystem." not in held

# Wet world budget and non-uniform, coverage-aware cached puddle meshes.
assert "WET_CHUNK_BUILDS_PER_FRAME = 1" in cosmetic
assert "WET_CHUNK_REFRESH_TICKS = 120L" in cosmetic
assert "buildWetSurfaceMesh(world, chunkX, chunkZ, coverage)" in cosmetic
assert "wetField(worldX + 0.5, worldZ + 0.5)" in cosmetic
assert "private static float wetField(double x, double z)" in cosmetic
assert "mesh.coverage - coverage" in cosmetic

# Wings attach mesh and glints to the same shoulder root; 1P overlay stays peripheral.
wing_point = cosmetic.split("private Vec3d wingPoint(", 1)[1].split("private static void drawHandRibbon", 1)[0]
assert "return wingPose(root," in wing_point and "playerPos.add(0, 1.13, 0)" not in wing_point
assert "shoulderHeight = p.isInSneakingPose() ? 1.24 : 1.36" in cosmetic
assert "renderFirstPersonWingPanels(out, camera, cameraRotation)" in cosmetic
assert "private void renderFirstPersonWingPanels" in cosmetic
assert "wingPoint(wingRoot" in cosmetic

# Silk veil, trail density, nametag readability and existing head accessory anchor.
assert "double vertical = 1.52 - 1.30 * t + lift" in cosmetic
assert "PRISM_TRAIL_SAMPLE_DISTANCE_SQ = 0.0025" in cosmetic
assert "double pixel = 0.0170 * scale" in cosmetic
assert "gridStep = pixel * 1.04" in cosmetic
assert "textFace = face.add(view.multiply(0.010 * scale))" in cosmetic
assert "headAccessoryAnchorY" in cosmetic and "renderHanfuOrnament" in cosmetic

# Sky retries transient errors; injectors are constrained to one exact match.
assert "retryAfterMillis = System.currentTimeMillis() + 1500L" in sky
assert "renderFaulted" not in sky
for path, source in [
    ("SkyRenderingMixin", sky_mixin),
    ("BackgroundRendererMixin", fog_mixin),
    ("InGameHudMixin", hud_mixin),
]:
    assert "require = 1, expect = 1, allow = 1" in source, path
assert 'if (cfg.isOn("crosshair_studio"))' in hud and 'else if (cfg.isOn("crosshair_ring"))' in hud

# Jump Ring keeps five model styles and independent pulse histories from v101.
assert "JUMP_PULSE_CAPACITY = 24" in cosmetic
assert "List<JumpPulse> jumpPulses" in cosmetic
assert "renderJumpPulseInstance" in cosmetic
jump_section = cosmetic.split("private void renderJumpPulseInstance", 1)[1].split("private ", 1)[0]
for case in ["case 0", "case 1", "case 2", "case 3", "default"]:
    assert case in jump_section

# Module IDs remain unique and complete.
module_catalog = (java / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
module_ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', module_catalog)
assert len(module_ids) == 99, f"expected 99 module ids, found {len(module_ids)}"
assert len(module_ids) == len(set(module_ids)), "duplicate module id"

assert "BAROX-VS-v103.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=1.03.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v103"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v103"

print("v103 checks passed: cape physics/layer flush, item-atlas glass and glint, cached Wet World puddles, shoulder-root/first-person wings, Sky retry, HUD text/crosshair and 99 unique module IDs")
