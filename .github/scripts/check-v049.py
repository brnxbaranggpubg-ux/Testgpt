#!/usr/bin/env python3
"""Regression and source-boundary checks for BAROX VS v049 second tranche."""
from pathlib import Path
import hashlib, json, sys

root = Path(sys.argv[1]).resolve()
src = root / "src/main/java"
java_files = sorted(src.rglob("*.java"))
assert len(java_files) == 25, f"expected 25 Java classes, got {len(java_files)}"

# v048 first tranche: all 12 Java classes must stay byte-identical.
first_half = {
"src/main/java/com/baroxvs/client/BaroxVsClient.java":"65d0bc273eb5c89375bf217a8c16be89c54fd62cae67ec89343685e4d83a8a03",
"src/main/java/com/baroxvs/client/HudChatCommands.java":"6f0060afa5164631e901b537a973b53c173209e145b18332e563febbef8bacaf",
"src/main/java/com/baroxvs/client/audio/DesktopPcmOutput.java":"fea66c93f1793d319866727ac4c3de682abe34d99b64b01eefef9074b7e32af7",
"src/main/java/com/baroxvs/client/audio/MusicEngine.java":"9c7f7df4968b58e215049919c961aece06454d0f5f42e770a60032a4f89aa722",
"src/main/java/com/baroxvs/client/config/BaroxConfig.java":"018cfb9a3953805f09dec623736c38c5666090b19b00660a739fd7a13cdd5df5",
"src/main/java/com/baroxvs/client/cosmetic/CapeClothSimulation.java":"26f5817c2f1f0fb1744378a60ce0e1f3268fe12735f9a6451e0175eccd020e2a",
"src/main/java/com/baroxvs/client/cosmetic/CosmeticCatalog.java":"4681d3d2cb34d361445391f547a03ffb9f7d25dadabc66009fae5848b68a576d",
"src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java":"589583d3eacd7f15fc0bd15f80be96a1538f7a4901b06b4fe6787654e11f5ab4",
"src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java":"be8e288c2d17cb16d8f75cf2ef627dc38f783ac2c4ee2ed94d7135749b306e5b",
"src/main/java/com/baroxvs/client/gui/BaroxClothConfigScreen.java":"a5f95218380e9def7973912e4aec7635abc11c935afe5c0d9c35b29edf048f4c",
"src/main/java/com/baroxvs/client/gui/BaroxMenuScreen.java":"c97b8e69dd5f351df54f431ab874e9be19e300ee0bbda53c826b192405deee54",
"src/main/java/com/baroxvs/client/gui/HudEditorScreen.java":"cef7b4a29fce165912016fd5626feefe88d112d5737532835ed8aa55abf2ca7e",
}
for rel, expected in first_half.items():
    actual = hashlib.sha256((root / rel).read_bytes()).hexdigest()
    assert actual == expected, f"v048 first tranche changed: {rel}"

# Five second-half classes are intentionally unmodified.
unchanged = {
"src/main/java/com/baroxvs/client/gui/Ui.java":"4198ac5040937be397794aec2a86ea4049293870620539252904913b229a3cb3",
"src/main/java/com/baroxvs/client/mixin/BackgroundRendererMixin.java":"f7fe6fda0c6ccc7b811f246b94a92bb5274f56020376817461173acd63378eb5",
"src/main/java/com/baroxvs/client/mixin/LocalSkinMixin.java":"135381519b2dbff3f2a126c55f2dd914b2a8253039a4e79fbb338513dd72496b",
"src/main/java/com/baroxvs/client/mixin/SkyRenderingMixin.java":"68d968184da869f3a80219f3ee64e3470aa6ceb564a35ef0e26315dac9737079",
"src/main/java/com/baroxvs/client/theme/Theme.java":"1f1901258e33f966583b931295ffa943ab1dc646756ce07607f53c8f2980bdff",
}
for rel, expected in unchanged.items():
    actual = hashlib.sha256((root / rel).read_bytes()).hexdigest()
    assert actual == expected, f"unexpected second-half file change: {rel}"

l10n = (root / "src/main/java/com/baroxvs/client/gui/L10n.java").read_text()
assert "moduleDescription(ModuleCatalog.Module module)" in l10n and "category(String category)" in l10n
click = (root / "src/main/java/com/baroxvs/client/gui/ModuleClickGuiScreen.java").read_text()
assert 'getModContainer("baroxvs")' in click and "L10n.module(module)" in click
assert "L10n.moduleDescription(module)" in click and "v039" not in click
assert "L10n.category(category)" in click and 'L10n.tr("modules.all")' in click

settings = (root / "src/main/java/com/baroxvs/client/gui/ModuleSettingsScreen.java").read_text()
assert "private boolean sliderDirty;" in settings
assert "sliderDirty = true;" in settings
assert "if (sliderDirty) config.save();" in settings
render = settings[settings.index("public void render(DrawContext context"):settings.index("private int heightOf(")]
assert render.count("fillGradient(0, 0, width, height") == 0, "settings sheet has a duplicate dim layer"

hud = (root / "src/main/java/com/baroxvs/client/hud/HudRenderer.java").read_text()
assert "worldInfoRefreshTick == Integer.MIN_VALUE || ticks - worldInfoRefreshTick >= 10" in hud
assert "private int[] keybindsSize(TextRenderer tr, int screenWidth)" in hud
assert "int gx0 = graphX + i * graphW / fpsSampleCount;" in hud
assert "int gx1 = graphX + (i + 1) * graphW / fpsSampleCount;" in hud
assert "targetSeenMs = 0L;" in hud and "while (popups.size() >= 8)" in hud
assert "musicTitle = cfg.musicTitle == null" in hud
assert "biomeDisplayName(MinecraftClient mc, PlayerEntity player)" in hud

lrc = (root / "src/main/java/com/baroxvs/client/hud/LyricFlowOverlay.java").read_text()
assert "seconds >= 60L" in lrc
assert "Math.addExact(baseMs, offsetMs)" in lrc

skin = (root / "src/main/java/com/baroxvs/client/render/SkinStudio.java").read_text()
assert "MAX_SKIN_FILE_BYTES" in skin and "discardPhoto(client);" in skin
assert "Skin PNG must be between 1 byte and 1 MB" in skin

themes = (root / "src/main/java/com/baroxvs/client/theme/Themes.java").read_text()
assert "import java.awt" not in themes and "hsbToRgb" in themes
sky = (root / "src/main/java/com/baroxvs/client/render/SkyboxEngine.java").read_text()
assert "final int segments = 64;" in sky and "auroraColor(" not in sky

lang_dir = root / "src/main/resources/assets/baroxvs/lang"
locales = {name: json.loads((lang_dir / name).read_text(encoding="utf-8"))
           for name in ("en_us.json", "de_de.json", "tr_tr.json")}
keys = set(locales["en_us.json"])
assert all(set(data) == keys for data in locales.values()), "locale key parity failed"
assert locales["en_us.json"]["baroxvs.modules.all"] == "All modules"
assert locales["de_de.json"]["baroxvs.modules.all"] == "Alle Module"
assert locales["tr_tr.json"]["baroxvs.modules.all"] == "Tüm Modüller"

assert "mod_version=0.49.0" in (root / "gradle.properties").read_text()
assert "BAROX-VS-v049.jar" in (root / "build.gradle").read_text()
assert (root / "VERSION").read_text().strip() == "BAROX VS v049"
assert "BAROX VS v049" in (root / "BUILD_VERSION.txt").read_text()
assert (root / "SECOND_HALF_REVIEW_v049.md").is_file()
print("v049 second-tranche checks passed: 13/25 classes reviewed; first 12 v048 Java files and 5 untouched classes preserved.")
