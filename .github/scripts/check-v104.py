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
for name in ("PlayerGlassMixin", "HeldItemFirstPersonGlassMixin", "PlayerHeldItemGlassMixin",
             "ItemLayerGlassMixin", "SkyRenderingMixin", "BackgroundRendererMixin", "InGameHudMixin"):
    assert name in client_mixins, f"missing client mixin: {name}"
assert mixins["required"] is True and mixins["injectors"]["defaultRequire"] == 1

self_glass = (java / "render/SelfGlassRenderer.java").read_text(encoding="utf-8")
player_mixin = (java / "mixin/PlayerGlassMixin.java").read_text(encoding="utf-8")
held_glass = (java / "render/HeldItemGlassRenderer.java").read_text(encoding="utf-8")
cosmetic = (java / "cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
cloth = (java / "cosmetic/CapeClothSimulation.java").read_text(encoding="utf-8")
config = (java / "config/BaroxConfig.java").read_text(encoding="utf-8")
client = (java / "BaroxVsClient.java").read_text(encoding="utf-8")
settings = (java / "gui/ModuleSettingsScreen.java").read_text(encoding="utf-8")
sky = (java / "render/SkyboxEngine.java").read_text(encoding="utf-8")
hud_mixin = (java / "mixin/InGameHudMixin.java").read_text(encoding="utf-8")

# Self Glass is the real player model overlay, not a HUD-only/glow proxy.
assert "model.render(matrices, new GlassConsumer" in self_glass
assert "RenderLayer.getEntityTranslucent(TEXTURE)" in self_glass
assert "config.isOn(\"player_glass\") || !config.isOn(\"self_glass\")" in self_glass
assert 'moduleValue("self_glass", "scale", 1.0f' in self_glass
assert "reflectionScale" in self_glass and "sweepRate" in self_glass
assert "float transmissionScale = 0.86f - transmission * 0.26f" in self_glass
assert "0.20f + fresnel * 0.72f * edge" in self_glass
assert "multiplyRgb(blend(main, pearl, pearlMix), originalColor)" in self_glass
assert "matrices.push();" in self_glass and "finally" in self_glass and "matrices.pop();" in self_glass
assert "this.model" in player_mixin and "SelfGlassRenderer.render(this.model" in player_mixin
assert "playerState.id != client.player.getId()" in player_mixin
assert "playerState.spectator || playerState.invisible" in player_mixin
assert "require = 1, expect = 1, allow = 1" in player_mixin

# Player Glass group state is repaired, persistent, and toggle semantics are deterministic.
assert "JsonElement beforeSanitize = GSON.toJsonTree(loaded)" in config
assert "if (!beforeSanitize.equals(GSON.toJsonTree(loaded))) loaded.save()" in config
assert "normalizePlayerGlassGroup(modules)" in config
assert "normalizePlayerGlassGroup(profile.modules)" in config
assert '"player_glass".equals(id)' in client
assert 'CONFIG.setOn("self_glass", true)' in client
assert 'CONFIG.setOn(child.id(), false)' in client
assert '"player_glass".equals(ModuleCatalog.parentOf(id))' in client

# Each component's tuning now lives on its own nested page; child rows can be opened by right-click.
assert 'if (id.equals("player_glass"))' in settings
for component in ("self_glass", "hand_glow", "arm_glow", "held_item_glow"):
    assert f'id.equals("{component}")' in settings
assert 'MinecraftClient.getInstance().setScreen(new ModuleSettingsScreen(this, config, child))' in settings
assert 'if (button == 1)' in settings
assert '"selfGlassScale", "Reflection pattern scale"' in settings
assert 'case "selfGlassOpacity" -> config.moduleValue("self_glass", "opacity", 0.42f' in settings
assert 'case "selfGlassEdge" -> config.moduleValue("self_glass", "edge", 0.82f' in settings
assert 'case "selfGlassGloss" -> config.moduleValue("self_glass", "gloss", 0.78f' in settings

# Prior critical repairs remain present.
assert "WET_CHUNK_BUILDS_PER_FRAME = 1" in cosmetic
assert "WET_CHUNK_REFRESH_TICKS = 120L" in cosmetic
assert "JUMP_PULSE_CAPACITY = 24" in cosmetic
assert "List<JumpPulse> jumpPulses" in cosmetic
assert "renderFirstPersonWingPanels" in cosmetic
assert "private void renderCape(VertexConsumer out, net.minecraft.client.render.VertexConsumerProvider consumers" in cosmetic
assert "immediate.draw(bodyLayer);" in cosmetic and "immediate.draw(logoLayer);" in cosmetic
assert "retryAfterMillis = System.currentTimeMillis() + 1500L" in sky
assert "quad.getSprite()" in held_glass and "sprite.getAtlasId()" in held_glass
assert "sourceAlpha = ((sourceColor >>> 24) & 255) / 255.0f" in held_glass
assert "require = 1, expect = 1, allow = 1" in hud_mixin

# All public module IDs stay backwards-compatible and unique.
module_catalog = (java / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
module_ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', module_catalog)
assert len(module_ids) == 99, f"expected 99 module IDs, found {len(module_ids)}"
assert len(module_ids) == len(set(module_ids)), "duplicate module id"

assert "BAROX-VS-v104.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=1.04.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v104"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v104"

print("v104 checks passed: rewritten Self Glass material and controls, Player Glass group-state migration, per-component settings navigation, preserved renderer fixes, exact Minecraft 1.21.4 and 99 unique module IDs")