#!/usr/bin/env python3
"""Strict validation for the BAROX VS v048 first-source-tranche build."""
from pathlib import Path
import hashlib, json, sys

root = Path(sys.argv[1]).resolve()
src = root / "src/main/java"
java_files = sorted(src.rglob("*.java"))
assert len(java_files) == 25, f"expected 25 Java classes, got {len(java_files)}"
first = [p.relative_to(root).as_posix() for p in java_files[:12]]
expected_first = [
 "src/main/java/com/baroxvs/client/BaroxVsClient.java",
 "src/main/java/com/baroxvs/client/HudChatCommands.java",
 "src/main/java/com/baroxvs/client/audio/DesktopPcmOutput.java",
 "src/main/java/com/baroxvs/client/audio/MusicEngine.java",
 "src/main/java/com/baroxvs/client/config/BaroxConfig.java",
 "src/main/java/com/baroxvs/client/cosmetic/CapeClothSimulation.java",
 "src/main/java/com/baroxvs/client/cosmetic/CosmeticCatalog.java",
 "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java",
 "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java",
 "src/main/java/com/baroxvs/client/gui/BaroxClothConfigScreen.java",
 "src/main/java/com/baroxvs/client/gui/BaroxMenuScreen.java",
 "src/main/java/com/baroxvs/client/gui/HudEditorScreen.java",
]
assert first == expected_first, "source tranche boundary changed"

# The remaining 13 files are byte-identical to the v047 baseline: no second-half work is included.
unchanged = {
"src/main/java/com/baroxvs/client/gui/L10n.java":"ff2ac3dff57b9e738b532ff9d3d044a3b94af3520e2bbe5f0b7387b83acbcd97",
"src/main/java/com/baroxvs/client/gui/ModuleClickGuiScreen.java":"f8d937d8446a019f0fa45cf00dc25a60e797af9b06397280008b594b802b1ca1",
"src/main/java/com/baroxvs/client/gui/ModuleSettingsScreen.java":"1210bb1f2ad3ae6d45806657f2057ee2cd8547fe7ac8c1f79adcc36f07b549fc",
"src/main/java/com/baroxvs/client/gui/Ui.java":"4198ac5040937be397794aec2a86ea4049293870620539252904913b229a3cb3",
"src/main/java/com/baroxvs/client/hud/HudRenderer.java":"3a113f1f8fa9630c3ed3624b46f1fda342c3a89d0c2bf2b4090deb5f3dc653d4",
"src/main/java/com/baroxvs/client/hud/LyricFlowOverlay.java":"f64c32bd7665930a93dd43b549d7413ede2245f9efb12f6a51de66e6454dbdae",
"src/main/java/com/baroxvs/client/mixin/BackgroundRendererMixin.java":"f7fe6fda0c6ccc7b811f246b94a92bb5274f56020376817461173acd63378eb5",
"src/main/java/com/baroxvs/client/mixin/LocalSkinMixin.java":"135381519b2dbff3f2a126c55f2dd914b2a8253039a4e79fbb338513dd72496b",
"src/main/java/com/baroxvs/client/mixin/SkyRenderingMixin.java":"68d968184da869f3a80219f3ee64e3470aa6ceb564a35ef0e26315dac9737079",
"src/main/java/com/baroxvs/client/render/SkinStudio.java":"fb9faa269c3cde6f5025086493ad0590bb3286d888749e3919599ea411c2a77f",
"src/main/java/com/baroxvs/client/render/SkyboxEngine.java":"3f8d70b03a423865e86e459d40baf43359a3b01d225e3904f1f285a7583bf2b9",
"src/main/java/com/baroxvs/client/theme/Theme.java":"1f1901258e33f966583b931295ffa943ab1dc646756ce07607f53c8f2980bdff",
"src/main/java/com/baroxvs/client/theme/Themes.java":"78030af5a0ce8c9a8810a5cbbd4fc728c8eb8b18c65b091058d816cab40519c4",
}
for rel, digest in unchanged.items():
    actual = hashlib.sha256((root / rel).read_bytes()).hexdigest()
    assert actual == digest, f"second-half Java file changed: {rel}"

engine = (root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text()
assert "targetingWater" not in engine and "BlockHitResult" not in engine
assert "private static final int[] SIDES = {-1, 1};" in engine
assert "new int[]{-1, 1}" not in engine
assert "puddleCoverage <= 0.01f ? 0" in engine
assert "opacity <= 0.01f || radiusX <= 0.0" in engine
assert "Math.max(0.0f, Math.min(0.76f, opacity * 1.72f))" in engine
for start, end in [
 ("private void renderWings(", "private void renderChineseHat("),
 ("private void renderHeadwear(", "private Vec3d wingPose("),
 ("private void renderHanfuOrnament(", "private void renderSilkRibbons("),
]:
    body = engine[engine.index(start):engine.index(end, engine.index(start))]
    assert "try {" in body and "} finally {" in body and "GEOMETRY_ALPHA.set(previousAlpha);" in body

catalog = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text()
assert 'throw new IllegalArgumentException("Duplicate BAROX module id: " + m.id())' in catalog
config = (root / "src/main/java/com/baroxvs/client/config/BaroxConfig.java").read_text()
assert 'values.entrySet().removeIf(entry -> entry.getKey() == null || entry.getKey().isBlank())' in config

cloth = (root / "src/main/java/com/baroxvs/client/gui/BaroxClothConfigScreen.java").read_text()
assert 'defeat_dissolve' not in cloth
assert 'setDefaultValue(true).setSaveConsumer(v -> config.setOn("aura", v))' in cloth
assert 'Text.translatable("baroxvs.cloth.category.sky")' in cloth

menu = (root / "src/main/java/com/baroxvs/client/gui/BaroxMenuScreen.java").read_text()
assert 'getModContainer("baroxvs")' in menu and "VERSION_LABEL" in menu
assert 'CosmeticCatalog.SKIES.length + " sky presets"' in menu
assert "v018" not in menu and "v020" not in menu

pcm = (root / "src/main/java/com/baroxvs/client/audio/DesktopPcmOutput.java").read_text()
assert "private byte[] pcmBuffer = new byte[8192];" in pcm
assert "line.write(pcmBuffer, 0, byteLength);" in pcm
assert "byte[] bytes = new byte[length * 2]" not in pcm

lang = root / "src/main/resources/assets/baroxvs/lang"
translations = {name: json.loads((lang / name).read_text(encoding="utf-8"))
                for name in ("en_us.json", "de_de.json", "tr_tr.json")}
keys = set(translations["en_us.json"])
assert all(set(values) == keys for values in translations.values()), "locale key parity failed"
assert translations["en_us.json"]["baroxvs.cloth.category.sky"] == "Sky colours"
assert translations["de_de.json"]["baroxvs.cloth.category.sky"] == "Himmelsfarben"
assert translations["tr_tr.json"]["baroxvs.cloth.category.sky"] == "Gökyüzü renkleri"

assert "mod_version=0.48.0" in (root / "gradle.properties").read_text()
assert "BAROX-VS-v048.jar" in (root / "build.gradle").read_text()
assert (root / "VERSION").read_text().strip() == "BAROX VS v048"
assert "BAROX VS v048" in (root / "BUILD_VERSION.txt").read_text()
assert (root / "FIRST_HALF_REVIEW_v048.md").is_file()
print("v048 first-tranche checks passed: 12/25 classes reviewed; all 13 second-half Java files unchanged.")
