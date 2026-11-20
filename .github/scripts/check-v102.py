from hashlib import sha256
from pathlib import Path
import json
import sys

root = Path(sys.argv[1])
metadata = json.loads((root / "src/main/resources/fabric.mod.json").read_text(encoding="utf-8"))
assert metadata["depends"]["minecraft"] == "1.21.4", "Minecraft target must be exactly 1.21.4"
assert metadata["depends"]["java"] == ">=21"

mixins = json.loads((root / "src/main/resources/baroxvs.mixins.json").read_text(encoding="utf-8"))
client_mixins = set(mixins["client"])
expected = {"SkyRenderingMixin", "BackgroundRendererMixin", "ItemLayerGlassMixin", "HeldItemFirstPersonGlassMixin", "PlayerHeldItemGlassMixin", "PlayerGlassMixin"}
assert expected.issubset(client_mixins), "required 1.21.4 renderer mixins missing"
assert mixins["required"] is True and mixins["injectors"]["defaultRequire"] == 1

base = root / "src/main/java/com/baroxvs/client"
sky = (base / "mixin/SkyRenderingMixin.java").read_text(encoding="utf-8")
fog = (base / "mixin/BackgroundRendererMixin.java").read_text(encoding="utf-8")
player = (base / "mixin/PlayerGlassMixin.java").read_text(encoding="utf-8")
held_mixin = (base / "mixin/HeldItemFirstPersonGlassMixin.java").read_text(encoding="utf-8")
third_mixin = (base / "mixin/PlayerHeldItemGlassMixin.java").read_text(encoding="utf-8")
item_mixin = (base / "mixin/ItemLayerGlassMixin.java").read_text(encoding="utf-8")
held = (base / "render/HeldItemGlassRenderer.java").read_text(encoding="utf-8")
self_glass = (base / "render/SelfGlassRenderer.java").read_text(encoding="utf-8")

assert "import net.minecraft.client.render.SkyRendering;" in sky and 'method = "renderSky(FFF)V"' in sky and 'method = "renderCelestialBodies"' in sky
assert "import net.minecraft.client.render.BackgroundRenderer;" in fog and 'method = "getFogColor"' in fog and "CameraSubmersionType.NONE" in fog
assert 'target = "Lnet/minecraft/client/util/math/MatrixStack;pop()V", ordinal = 0' in player
assert "require = 1, expect = 1, allow = 1" in player
assert "playerState.id != client.player.getId()" in player and "playerState.spectator || playerState.invisible" in player
assert "beginFirstPerson(player, stack, hand)" in held_mixin and "HeldItemGlassRenderer.end()" in held_mixin
assert "beginThirdPerson(client.player, arm)" in third_mixin and "HeldItemGlassRenderer.end()" in third_mixin
assert 'method = "render", at = @At("TAIL")' in item_mixin and "HeldItemGlassRenderer.isActive()" in item_mixin
assert "if (!frames.isEmpty()) frames.clear();" in held and "frames.push(new Frame(settings, glint));" in held
assert "if (stack.isEmpty()) ACTIVE.remove();" in held
assert self_glass.count("matrices.push();") == 2 and self_glass.count("finally {") == 2 and self_glass.count("matrices.pop();") == 2
assert "RenderSystem." not in held and "RenderSystem." not in self_glass
assert "RenderLayer.getEntityTranslucent" in held and "RenderLayer.getEntityTranslucent" in self_glass

unchanged = {
 "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java": "35e462d644eccc8caf15a0193bcbb9b06e7e070c9503a9acda19d6f1f0a51d3e",
 "src/main/java/com/baroxvs/client/config/BaroxConfig.java": "4d0fda9eac887b782efe425f10bcccb7299113a9494098152946b454fed8797b",
 "src/main/java/com/baroxvs/client/theme/Themes.java": "e8e3a823a38720195b07c139199d7da3aca23376e588c364bd568afe2ea0cf23",
 "src/main/java/com/baroxvs/client/gui/Ui.java": "2ea0e6b308bd241c75f5049c23caa2e63199c362ce3ff5b5edc52e6fe484b5d1",
}
for relative, expected_hash in unchanged.items():
    assert sha256((root / relative).read_bytes()).hexdigest() == expected_hash, f"unexpected change: {relative}"
assert "BAROX-VS-v102.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=1.02.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v102"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v102"
print("v102 checks passed: exact 1.21.4 target, sky/fog compatibility, isolated glass passes, abandoned-scope cleanup, 99 module IDs retained")
