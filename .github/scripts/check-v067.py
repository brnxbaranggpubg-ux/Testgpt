from hashlib import sha256
from pathlib import Path
import sys
root = Path(sys.argv[1])
engine = (root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
glass = (root / "src/main/java/com/baroxvs/client/render/SelfGlassRenderer.java").read_text(encoding="utf-8")
held = (root / "src/main/java/com/baroxvs/client/render/HeldItemGlassRenderer.java").read_text(encoding="utf-8")
mixin = (root / "src/main/java/com/baroxvs/client/mixin/PlayerHeldItemGlassMixin.java").read_text(encoding="utf-8")
mixins = (root / "src/main/resources/baroxvs.mixins.json").read_text(encoding="utf-8")
assert "drawAuraRing(out, camera, pos, radius" in engine
assert "private static void drawAuraRing(" in engine
assert "activeRenderQuality == 0 ? 18 : activeRenderQuality == 1 ? 24 : 32" in engine
jump = engine[engine.index("private void renderJumpPulse("):engine.index("private void renderMusicVisualizerGeometry(")]
assert "drawAuraRing(" in jump and "drawAuraDisc(" not in jump
assert "Math.max(0.43, (0.24 + eased * 0.82) * scale)" in engine
assert "PRISM_TRAIL_CAPACITY = 28" in engine
assert "position.add(0, 0.018, 0)" in engine
assert "age / 28.0" in engine
assert "double width = 0.046 * scale * length * fade" in engine
assert "add(0, 0.014, 0)" in engine
assert "back.multiply(0.52)" in engine and "back.multiply(0.48)" in engine
assert "(0.62 + 0.035 * Math.sin(p0 * 0.62)) * scale" in engine
assert "back.multiply(0.72)" in engine
assert "orbitX = Math.cos(angle) * 0.68" in engine
assert "orbitZ = Math.sin(angle) * 0.38" in engine
assert "Vec3d ringCentre = pos.add(0, 0.12, 0);" in engine
assert "drawAuraRing(out, camera, centre, radius, 0.12," in engine
assert "drawAuraRing(out, camera, pos.add(0, y, 0)" in engine
assert "drawAuraRing(out, camera, pos.add(0, 1.02, 0)" in engine
assert "right.multiply(-0.48)).add(back.multiply(0.20))" in engine
assert "int layers = 1;" in engine and "layers == 1 ? 0.72f" in engine
assert "case 0 -> 3; case 1 -> 3; default -> 4;" in engine
assert "case 0 -> 4; case 1 -> 5; default -> 6;" in engine
assert "fresnel * 0.62f + fresnel * sweep * 0.12f" in glass
assert "Math.max(0.0f, Math.min(0.62f, alpha))" in glass
player_mixin = (root / "src/main/java/com/baroxvs/client/mixin/PlayerGlassMixin.java").read_text()
assert "playerState.id != client.player.getId()" in player_mixin
assert "playerState.spectator || playerState.invisible" in player_mixin
assert "RenderLayer.getEntityGlint()" in held
assert "GLINT_TEXTURE" not in held
assert "beginThirdPerson(client.player, arm)" in mixin
assert '@At("HEAD")' in mixin and '@At("RETURN")' in mixin
assert '"PlayerHeldItemGlassMixin"' in mixins
unchanged = {
"src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java":"ab8d6eaba93e6f791c5ec1cc454e973999e145e728f63ebf50296936e8e2e369",
"src/main/java/com/baroxvs/client/config/BaroxConfig.java":"6e0b98d331b507f347dda986c80fb786140f5821cfb1a5660bc163671bc7815d",
"src/main/java/com/baroxvs/client/theme/Themes.java":"e8e3a823a38720195b07c139199d7da3aca23376e588c364bd568afe2ea0cf23",
"src/main/java/com/baroxvs/client/gui/Ui.java":"2ea0e6b308bd241c75f5049c23caa2e63199c362ce3ff5b5edc52e6fe484b5d1"}
for relative, expected in unchanged.items():
 assert sha256((root/relative).read_bytes()).hexdigest()==expected, f"unexpected edit: {relative}"
assert "BAROX-VS-v067.jar" in (root/"build.gradle").read_text()
assert "mod_version=0.67.0" in (root/"gradle.properties").read_text()
assert (root/"VERSION").read_text().strip()=="BAROX VS v067"
assert (root/"BUILD_VERSION.txt").read_text().strip()=="BAROX VS v067"
print("v067 player visibility/glint/trail/companion checks passed")
