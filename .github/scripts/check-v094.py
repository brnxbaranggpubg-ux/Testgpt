#!/usr/bin/env python3
import json
import re
import struct
import sys
from pathlib import Path

root = Path(sys.argv[1])
base = root / "src/main/java/com/baroxvs/client"
renderer = (base / "render/HeldItemGlassRenderer.java").read_text(encoding="utf-8")
engine = (base / "cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(ids) == len(set(ids)) == 99, f"module IDs changed: {len(ids)} declarations / {len(set(ids))} unique"
for module_id in ("glint", "player_glass", "hand_glow", "held_item_glow", "self_glass"):
    assert ids.count(module_id) == 1, f"missing or duplicated module: {module_id}"

assert 'RenderLayer.getEntityTranslucent(WHITE_TEXTURE)' in renderer
assert 'RenderLayer.getEntityGlint()' not in renderer
assert 'GLINT_FACE_BIAS = 0.00110f' in renderer
assert 'position.add(normal.x * GLINT_FACE_BIAS' in renderer
assert 'private static void renderGlint' in renderer
assert 'if (config.isOn("glint"))' in renderer
assert 'settings.opacity()' in renderer and 'settings.color()' in renderer
assert 'isSupportedDisplayItem' not in renderer
assert 'DataComponentTypes.FOOD' not in renderer
assert 'Registries.ITEM' not in renderer
assert 'Items.' not in renderer
assert 'if (config.isOn("player_glass") && config.isOn("held_item_glow"))' in renderer
assert 'FIRST_PERSON_LEFT_HAND' in renderer and 'FIRST_PERSON_RIGHT_HAND' in renderer
assert 'THIRD_PERSON_LEFT_HAND' in renderer and 'THIRD_PERSON_RIGHT_HAND' in renderer
assert 'if (frame.settings != null) renderGlass' in renderer
assert 'private static void renderGlass' in renderer
assert 'RenderLayer.getEntityTranslucent(MATERIAL)' in renderer

first_person = (base / "mixin/HeldItemFirstPersonGlassMixin.java").read_text(encoding="utf-8")
third_person = (base / "mixin/PlayerHeldItemGlassMixin.java").read_text(encoding="utf-8")
layer = (base / "mixin/ItemLayerGlassMixin.java").read_text(encoding="utf-8")
assert 'method = "renderFirstPersonItem(' in first_person
assert 'at = @At("HEAD")' in first_person and 'at = @At("RETURN")' in first_person
assert 'method = "renderItem(' in third_person
assert 'HeldItemGlassRenderer.beginThirdPerson' in third_person
assert 'at = @At("HEAD")' in third_person and 'at = @At("RETURN")' in third_person
assert '@Mixin(ItemRenderState.LayerRenderState.class)' in layer
assert '@Inject(method = "render", at = @At("TAIL"))' in layer
assert 'HeldItemGlassRenderer.render(this.model' in layer
mixins = json.loads((root / "src/main/resources/baroxvs.mixins.json").read_text(encoding="utf-8"))
for mixin in ("ItemLayerGlassMixin", "HeldItemFirstPersonGlassMixin", "PlayerHeldItemGlassMixin"):
    assert mixin in mixins["client"], f"missing mixin: {mixin}"

start = engine.index('private void renderGlowCosmetics(')
end = engine.index('private void renderLiquidGlassAvatar(', start)
hand_region = engine[start:end]
assert 'drawHandRibbon(' in hand_region
assert 'drawGlassOrb(out, camera, wrist' not in hand_region
assert 'drawGlassOrb(out, camera, handPearl' not in hand_region
assert 'drawGlassOrb(out, camera, offWrist' not in hand_region
assert 'private static void drawHandRibbon(' in engine

lang = root / "src/main/resources/assets/baroxvs/lang"
files = ("en_us.json", "de_de.json", "tr_tr.json")
data = {name: json.loads((lang / name).read_text(encoding="utf-8")) for name in files}
keys = set(data["en_us.json"])
assert all(set(value) == keys for value in data.values()), "locale keys differ"
assert "all baked held-item models" in data["en_us.json"]["baroxvs.module.held_item_glow.description"]
assert "allen gebackenen gehaltenen Item-Modellen" in data["de_de.json"]["baroxvs.module.held_item_glow.description"]
assert "Tüm elde tutulan model eşyalara" in data["tr_tr.json"]["baroxvs.module.held_item_glow.description"]

white = (root / "src/main/resources/assets/baroxvs/textures/misc/white.png").read_bytes()
assert white[:8] == b"\x89PNG\r\n\x1a\n"
assert struct.unpack(">II", white[16:24]) == (1, 1)
assert "BAROX-VS-v094.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=0.94.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v094"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v094"
assert (root / "RENDER_REPAIR_v094.md").is_file()
print("v094 checks passed: Glint vertex alpha/tint, all baked held-item models, first-/third-person hooks, hand ribbons, 99 module IDs and locale parity")
