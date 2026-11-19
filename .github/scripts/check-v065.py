import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
base = root / "src/main/java/com/baroxvs/client"

catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(ids) == len(set(ids)) == 99, f"module registrations changed: {len(ids)}"
for module_id in ["aura", "glint", "player_glass", "self_glass", "jump_circle", "rgb_outline",
                  "prism_trail", "footprint_fx", "wings", "pet", "wing_harness"]:
    assert ids.count(module_id) == 1, f"missing/duplicate module {module_id}"

engine = (base / "cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
assert "WorldRenderEvents.AFTER_ENTITIES.register(this::renderWorldEffects)" in engine
assert "WorldRenderEvents.BEFORE_ENTITIES.register(this::renderWorldEffects)" not in engine
assert 'config.isOn("rgb_outline")' not in engine, "old ellipsoid RGB shell still runs in world geometry"
assert 'config.isOn("self_glass")' not in engine, "old separate body-shell Player Glass pass is still active"
assert "drawPetOrb(out, camera, centre" in engine and "drawPetBloom(out, camera, centre" in engine
assert "case 0 -> 3; case 1 -> 4; default -> 6;" in engine
assert "case 0 -> 5; case 1 -> 6; default -> 8;" in engine
assert "case 0 -> 6; case 1 -> 8; default -> 10;" in engine
assert "int layers = activeRenderQuality == 0 ? 1 : activeRenderQuality == 1 ? 2 : 3;" in engine
assert "position.squaredDistanceTo(lastFootstepPlayerPos) >= 0.09" in engine
assert "position.squaredDistanceTo(lastPrismTrailPos) >= 0.0016" in engine
assert "prismTrailPositions[prismTrailCursor] = position.add(0, 0.055, 0);" in engine
assert "Vec3d centre = jumpPulseOrigin.add(0, 0.018, 0);" in engine

aura = engine[engine.index("private void renderAura("):engine.index("private void renderGlints(")]
assert "drawSoftDisc" in aura and "drawBillboard" not in aura and "drawDiamond" not in aura
first_person_glints = engine[engine.index("private void renderGlints("):engine.index("private void renderButterflyCompanion(")]
assert "if (client.options.getPerspective().isFirstPerson()) return;" in first_person_glints

renderer = (base / "render/SelfGlassRenderer.java").read_text(encoding="utf-8")
for token in [
    "model.render(matrices, new GlassConsumer", "RenderLayer.getEntityTranslucent(TEXTURE)",
    "public static void renderRgbOutline", "model.render(matrices, new RgbOutlineConsumer",
    "RenderLayer.getEntityTranslucent(WHITE_TEXTURE)", "float fresnel =",
    "delegate.vertex(x + nx * bias", "Themes.hsbToRgb"
]:
    assert token in renderer, f"missing model-material implementation: {token}"
assert "Framebuffer" not in renderer and "PostEffectProcessor" not in renderer

player_mixin = (base / "mixin/PlayerGlassMixin.java").read_text(encoding="utf-8")
assert "@Mixin(LivingEntityRenderer.class)" in player_mixin
assert "PlayerEntityRenderState" in player_mixin and "playerState.id != client.player.getId()" in player_mixin
assert "SelfGlassRenderer.render(this.model" in player_mixin
assert "SelfGlassRenderer.renderRgbOutline(this.model" in player_mixin
mixins = json.loads((root / "src/main/resources/baroxvs.mixins.json").read_text(encoding="utf-8"))
assert "PlayerGlassMixin" in mixins["client"]

held = (base / "render/HeldItemGlassRenderer.java").read_text(encoding="utf-8")
assert "GlintSettings" in held and "private static void renderGlint" in held
assert 'if (config.isOn("glint"))' in held
assert "frame.renderedModels.add(model)" in held
assert "frame.drawn" not in held
assert "RenderLayer.getEntityTranslucent(GLINT_TEXTURE)" in held
assert "emitGlintQuads(model.getQuads(null, direction" in held
assert "RenderLayer.getEntityTranslucent(MATERIAL)" in held

settings = (base / "gui/ModuleSettingsScreen.java").read_text(encoding="utf-8")
for token in ["selfGlassRefraction", "selfGlassEdge", "selfGlassGloss", "heldGlassTransmission"]:
    assert token in settings, f"existing visual control missing: {token}"

languages = root / "src/main/resources/assets/baroxvs/lang"
files = ["en_us.json", "de_de.json", "tr_tr.json"]
data = {name: json.loads((languages / name).read_text(encoding="utf-8")) for name in files}
keys = set(data["en_us.json"])
assert all(set(values) == keys for values in data.values()), "locale key parity changed"

assert (root / "RENDER_REPAIR_v065.md").is_file()
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v065"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v065"
assert "BAROX-VS-v065.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=0.65.0" in (root / "gradle.properties").read_text(encoding="utf-8")

print("v065 checks passed: model-conforming Player Glass/RGB, after-entity depth occlusion, Aura skin-safe, held multi-layer glint, trail/footprint history, compact pet LOD, 99 modules preserved")
