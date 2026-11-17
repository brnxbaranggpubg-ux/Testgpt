#!/usr/bin/env python3
"""BAROX VS v048: first 12 of 25 Java classes only."""
from pathlib import Path
import json, sys

ROOT = Path(sys.argv[1]).resolve()

def edit(rel, changes):
    path = ROOT / rel
    if not path.is_file():
        raise SystemExit("v048 missing source: " + rel)
    s = path.read_text(encoding="utf-8")
    for old, new, label in changes:
        n = s.count(old)
        if n != 1:
            raise SystemExit("v048 " + label + ": expected one match, got " + str(n))
        s = s.replace(old, new, 1)
    path.write_text(s, encoding="utf-8")

def wrap_alpha(s, start_marker, end_marker, setup):
    a = s.index(start_marker)
    b = s.index(end_marker, a)
    part = s[a:b]
    if part.count(setup) != 1:
        raise SystemExit("v048 missing alpha setup: " + start_marker)
    part = part.replace(setup, setup + "        try {\n", 1)
    reset = "        GEOMETRY_ALPHA.set(previousAlpha);\n    }\n"
    if part.count(reset) != 1:
        raise SystemExit("v048 missing alpha restore: " + start_marker)
    lo = part.index("        try {\n") + len("        try {\n")
    hi = part.index(reset)
    body = part[lo:hi]
    body = "".join(("    " + line if line.strip() else line)
                   for line in body.splitlines(keepends=True))
    part = part[:lo] + body + part[hi:]
    part = part.replace(reset,
        "        } finally {\n            GEOMETRY_ALPHA.set(previousAlpha);\n        }\n    }\n", 1)
    return s[:a] + part + s[b:]

edit("src/main/java/com/baroxvs/client/BaroxVsClient.java", [
    ("import com.baroxvs.client.BaroxVsClient;\n", "", "self import")
])

p = ROOT / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java"
s = p.read_text(encoding="utf-8")
for old, new, label in [
    ("import net.minecraft.util.hit.BlockHitResult;\n", "", "obsolete hit import"),
    ("    private static final Identifier LIQUID_GLASS_TEXTURE = Identifier.of(\"baroxvs\", \"textures/misc/liquid_glass.png\");\n\n\n",
     "    private static final Identifier LIQUID_GLASS_TEXTURE = Identifier.of(\"baroxvs\", \"textures/misc/liquid_glass.png\");\n    private static final int[] SIDES = {-1, 1};\n\n", "shared side array"),
    ("        boolean targetingWater = client.crosshairTarget instanceof BlockHitResult hit\n                && client.world.getFluidState(hit.getBlockPos()).isIn(FluidTags.WATER);\n        if (targetingWater) return;\n\n", "", "water-target early return"),
    ("        int puddleCount = Math.max(0, Math.min(18,\n                Math.round((4f + puddleCoverage * 12f) * (0.45f + quality * 0.55f))));",
     "        int puddleCount = puddleCoverage <= 0.01f ? 0 : Math.max(0, Math.min(18,\n                Math.round((4f + puddleCoverage * 12f) * puddleCoverage * (0.45f + quality * 0.55f))));", "zero puddle coverage"),
    ("        if (radiusX <= 0.0 || radiusY <= 0.0 || radiusZ <= 0.0) return;",
     "        if (opacity <= 0.01f || radiusX <= 0.0 || radiusY <= 0.0 || radiusZ <= 0.0) return;", "zero-opacity rim"),
    ("        float edgeStrength = Math.max(0.18f, Math.min(0.76f, opacity * 1.72f));",
     "        float edgeStrength = Math.max(0.0f, Math.min(0.76f, opacity * 1.72f));\n        if (edgeStrength <= 0.01f) return;", "rim alpha floor"),
    ("        float edgePower = Math.max(0.58f, Math.min(0.98f, opacity * 2.65f));",
     "        float edgePower = Math.max(0.0f, Math.min(0.92f, opacity * 1.42f));\n        if (edgePower <= 0.01f) return;", "avatar rim alpha floor")
]:
    n = s.count(old)
    if n != 1:
        raise SystemExit("v048 " + label + ": expected one match, got " + str(n))
    s = s.replace(old, new, 1)
s = s.replace("new int[]{-1, 1}", "SIDES")
s = wrap_alpha(s, "private void renderWings(", "private void renderChineseHat(",
               "        GEOMETRY_ALPHA.set(previousAlpha * config.moduleValue(\"wings\", \"opacity\", 1f, 0.10f, 1f));")
s = wrap_alpha(s, "private void renderHeadwear(", "private Vec3d wingPose(",
               "        GEOMETRY_ALPHA.set(previousAlpha * config.moduleValue(\"headwear\", \"opacity\", 1f, 0.10f, 1f));")
s = wrap_alpha(s, "private void renderHanfuOrnament(", "private void renderSilkRibbons(",
               "        GEOMETRY_ALPHA.set(previousAlpha * config.moduleValue(\"hanfu_ornament\", \"opacity\", 1f, 0.10f, 1f));")
p.write_text(s, encoding="utf-8")

edit("src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java", [
    ("        Module previous = BY_ID.put(m.id(), m);\n        if (previous != null) ALL.remove(previous);\n        ALL.add(m);",
     "        if (BY_ID.containsKey(m.id())) {\n            throw new IllegalArgumentException(\"Duplicate BAROX module id: \" + m.id());\n        }\n        BY_ID.put(m.id(), m);\n        ALL.add(m);", "duplicate module ID")
])

edit("src/main/java/com/baroxvs/client/config/BaroxConfig.java", [
    ("        values.replaceAll((key, value) -> value == null || !Float.isFinite(value) ? 0f : value);",
     "        values.entrySet().removeIf(entry -> entry.getKey() == null || entry.getKey().isBlank());\n        values.replaceAll((key, value) -> value == null || !Float.isFinite(value) ? 0f : value);", "config value keys")
])

edit("src/main/java/com/baroxvs/client/gui/BaroxClothConfigScreen.java", [
    (".setDefaultValue(false).setSaveConsumer(v -> config.setOn(\"aura\", v)).build());",
     ".setDefaultValue(true).setSaveConsumer(v -> config.setOn(\"aura\", v)).build());", "Aura reset default"),
    ("        effects.addEntry(entries.startBooleanToggle(Text.translatable(\"baroxvs.cloth.defeat_dissolve\"), config.isOn(\"defeat_dissolve\"))\n                .setDefaultValue(false).setSaveConsumer(v -> config.setOn(\"defeat_dissolve\", v)).build());\n", "", "retired defeat_dissolve toggle"),
    ("Text.literal(\"Sky colours\")", "Text.translatable(\"baroxvs.cloth.category.sky\")", "localized sky category")
])

edit("src/main/java/com/baroxvs/client/audio/DesktopPcmOutput.java", [
    ("    private final SourceDataLine line;\n",
     "    private final SourceDataLine line;\n    private byte[] pcmBuffer = new byte[8192];\n", "PCM scratch buffer"),
    ("        byte[] bytes = new byte[length * 2];\n        float effective = Math.max(0f, Math.min(1f, gain));\n        for (int i = 0, o = 0; i < length; i++) {\n            short value = (short) Math.max(Short.MIN_VALUE, Math.min(Short.MAX_VALUE, Math.round(samples[i] * effective)));\n            bytes[o++] = (byte) (value & 0xFF);\n            bytes[o++] = (byte) ((value >>> 8) & 0xFF);\n        }\n        line.write(bytes, 0, bytes.length);",
     "        int byteLength = length * 2;\n        if (pcmBuffer.length < byteLength) {\n            int capacity = Math.max(byteLength, pcmBuffer.length * 2);\n            pcmBuffer = new byte[capacity];\n        }\n        float effective = Math.max(0f, Math.min(1f, gain));\n        for (int i = 0, o = 0; i < length; i++) {\n            short value = (short) Math.max(Short.MIN_VALUE, Math.min(Short.MAX_VALUE, Math.round(samples[i] * effective)));\n            pcmBuffer[o++] = (byte) (value & 0xFF);\n            pcmBuffer[o++] = (byte) ((value >>> 8) & 0xFF);\n        }\n        line.write(pcmBuffer, 0, byteLength);", "PCM packet allocation")
])

edit("src/main/java/com/baroxvs/client/gui/BaroxMenuScreen.java", [
    ("import net.minecraft.client.MinecraftClient;",
     "import net.fabricmc.loader.api.FabricLoader;\nimport net.minecraft.client.MinecraftClient;", "FabricLoader import"),
    ("    private static final String[] PAGES = {\"Overview\", \"Wardrobe\", \"Wings Lab\", \"Effects\", \"HUD\", \"Atmosphere\", \"Music\", \"Color Studio\", \"Settings\"};",
     "    private static final String[] PAGES = {\"Overview\", \"Wardrobe\", \"Wings Lab\", \"Effects\", \"HUD\", \"Atmosphere\", \"Music\", \"Color Studio\", \"Settings\"};\n    private static final String VERSION_LABEL = FabricLoader.getInstance().getModContainer(\"baroxvs\")\n            .map(container -> \"v\" + container.getMetadata().getVersion().getFriendlyString())\n            .orElse(\"Visual Studio\");", "version metadata"),
    ("\"COSMETIC STUDIO  /  v018\"", "\"COSMETIC STUDIO  /  \" + VERSION_LABEL", "mobile version"),
    ("\"BAROX VS  /  v018\"", "\"BAROX VS  /  \" + VERSION_LABEL", "sidebar version"),
    ("\"BAROX VS   /   v020\"", "\"BAROX VS   /   \" + VERSION_LABEL", "footer version"),
    ("\"32 sky presets\"", "CosmeticCatalog.SKIES.length + \" sky presets\"", "preset count")
])

edit("gradle.properties", [("mod_version=0.47.0", "mod_version=0.48.0", "Gradle version")])
edit("build.gradle", [("archiveFileName = 'BAROX-VS-v047.jar'", "archiveFileName = 'BAROX-VS-v048.jar'", "remapped jar name")])
edit("VERSION", [("BAROX VS v047", "BAROX VS v048", "VERSION stamp")])
edit("BUILD_VERSION.txt", [("BAROX VS v047", "BAROX VS v048", "BUILD_VERSION stamp")])

for locale, value in {
    "en_us.json": "Sky colours",
    "de_de.json": "Himmelsfarben",
    "tr_tr.json": "Gökyüzü renkleri",
}.items():
    path = ROOT / "src/main/resources/assets/baroxvs/lang" / locale
    data = json.loads(path.read_text(encoding="utf-8"))
    key = "baroxvs.cloth.category.sky"
    if key in data:
        raise SystemExit("v048 translation already exists: " + locale)
    data[key] = value
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

(ROOT / "FIRST_HALF_REVIEW_v048.md").write_text("""# BAROX VS v048 — First source tranche review

Scope: the first 12 of 25 Java classes in sorted source-tree order. The remaining 13 Java classes were intentionally left unchanged for a later, separate review/build.

## Audited classes
- BaroxVsClient, HudChatCommands
- DesktopPcmOutput, MusicEngine
- BaroxConfig
- CapeClothSimulation, CosmeticCatalog, CosmeticEngine, ModuleCatalog
- BaroxClothConfigScreen, BaroxMenuScreen, HudEditorScreen

## Findings fixed in this tranche
1. Removed a crosshair-target water early return that skipped wings, headwear, cape and other cosmetics while looking at water.
2. Put the three temporary geometry-alpha scopes in try/finally, preventing render errors from leaking alpha state into later modules.
3. Made Wet World puddle count and pearl rims respect zero puddle coverage/opacity; previously a minimum rim strength could leave visible rings with coverage set to zero.
4. Reused bilateral side constants rather than allocating repeated int arrays inside render methods.
5. Made duplicate module IDs fail explicitly rather than silently replacing the catalogue index entry.
6. Removed the retired defeat_dissolve Cloth Config control, aligned Aura's reset default with the module catalogue, and localized the Sky category.
7. Reused the desktop PCM byte buffer instead of allocating a new byte array for every audio packet.
8. Cleaned invalid keys from the persisted module-value map and replaced stale menu version/sky-count labels with metadata-derived values.

No source files outside the first 12 Java classes were modified. Runtime testing in Minecraft has not yet been performed.
""", encoding="utf-8")

print("Applied BAROX VS v048 first tranche only (12/25 Java classes reviewed; remaining 13 untouched).")
