import json
import re
import struct
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
base = root / "src/main/java/com/baroxvs/client"

catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(ids) == len(set(ids)) == 99, f"module count or duplicate IDs changed: {len(ids)}"
assert ids.count("held_item_glow") == 1, "existing Held Item Glow module is missing or duplicated"
assert '"held_item_glow", "Held Item Glow"' in catalog
assert '"held_item_glow"' in catalog[catalog.index('group("player_glass"'):catalog.index('group("aura"')]

engine = (base / "cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
assert 'config.isOn("held_item_glow")' not in engine, "old hand-orb effect is still present"
assert '(config.isOn("player_glass") && (config.isOn("arm_glow")' in engine
assert '|| config.isOn("hand_glow") || config.isOn("held_item_glow")' not in engine

renderer = (base / "render/HeldItemGlassRenderer.java").read_text(encoding="utf-8")
for token in [
    "beginFirstPerson", "DataComponentTypes.FOOD", "Items.BOOK", "Items.WRITTEN_BOOK",
    "Items.SPYGLASS", "RenderLayer.getEntityTranslucent(MATERIAL)",
    "model.getQuads(null, direction", "model.getQuads(null, null",
    "entry.transformNormal(normal, normal)", "float fresnel =",
    "sweepFrequency", "sweepSharpness", "ThreadLocal<Scratch>",
    "client.getRenderTickCounter().getTickDelta(false)",
    "higher transmission means less opaque body"
]:
    assert token.lower() in renderer.lower(), f"held-item glass renderer is missing: {token}"
for forbidden in ["Framebuffer", "PostEffectProcessor", "KawaseBlur", "RenderSystem.setShader"]:
    assert forbidden not in renderer, f"unexpected costly screen-space pipeline: {forbidden}"
assert '"minecraft".equals(Registries.ITEM.getId(stack.getItem()).getNamespace())' in renderer
assert "stack.isOf(Items.MAP)" not in renderer and "stack.isOf(Items.FILLED_MAP)" not in renderer

first_person = (base / "mixin/HeldItemFirstPersonGlassMixin.java").read_text(encoding="utf-8")
assert "renderFirstPersonItem(" in first_person
assert 'at = @At("HEAD")' in first_person and 'at = @At("RETURN")' in first_person
layer = (base / "mixin/ItemLayerGlassMixin.java").read_text(encoding="utf-8")
assert "ItemRenderState.LayerRenderState.class" in layer
assert '@Inject(method = "render", at = @At("TAIL"))' in layer
assert "this.model != null" in layer
mixins = json.loads((root / "src/main/resources/baroxvs.mixins.json").read_text(encoding="utf-8"))
assert "HeldItemFirstPersonGlassMixin" in mixins["client"]
assert "ItemLayerGlassMixin" in mixins["client"]
assert "ItemRendererGlassMixin" not in mixins["client"]
assert not (base / "mixin/ItemRendererGlassMixin.java").exists()

settings = (base / "gui/ModuleSettingsScreen.java").read_text(encoding="utf-8")
for token in [
    'addSlider("heldGlowScale", "Reflection sweep size"',
    'addSlider("heldGlassTransmission", "Pearl transmission"',
    'addSlider("heldGlassEdge", "Fresnel edge"',
    'addSlider("heldGlassGloss", "Moving surface gloss"',
    'case "heldGlassTransmission" -> config.moduleValue("held_item_glow", "transmission"',
    'case "heldGlassEdge" -> config.moduleValue("held_item_glow", "edge"',
    'case "heldGlassGloss" -> config.moduleValue("held_item_glow", "gloss"',
]:
    assert token in settings, f"missing glass setting: {token}"

languages = root / "src/main/resources/assets/baroxvs/lang"
files = ["en_us.json", "de_de.json", "tr_tr.json"]
data = {name: json.loads((languages / name).read_text(encoding="utf-8")) for name in files}
keys = set(data["en_us.json"])
assert all(set(values) == keys for values in data.values()), "localisation keys differ"
for name in files:
    assert "baroxvs.module.held_item_glow.description" in data[name]

png = (root / "src/main/resources/assets/baroxvs/textures/misc/held_item_glass.png").read_bytes()
assert png[:8] == b"\x89PNG\r\n\x1a\n"
assert struct.unpack(">II", png[16:24]) == (128, 128), "glass texture should be 128x128"

assert (root / "HELD_ITEM_LIQUID_GLASS_v064.md").is_file()
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v064"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v064"
assert "BAROX-VS-v064.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=0.64.0" in (root / "gradle.properties").read_text(encoding="utf-8")

print("v064 checks passed: existing Held Item Glow converted to Liquid Glass, 99 modules preserved, first-person only hook, material settings/locales and 128x128 texture")
