#!/usr/bin/env python3
"""BAROX VS v049: audited second tranche (last 13 of 25 Java classes)."""
from pathlib import Path
import json
import sys

ROOT = Path(sys.argv[1]).resolve()

def edit(rel, changes):
    path = ROOT / rel
    if not path.is_file():
        raise SystemExit(f"v049 missing source: {rel}")
    source = path.read_text(encoding="utf-8")
    for old, new, label in changes:
        count = source.count(old)
        if count != 1:
            raise SystemExit(f"v049 {label}: expected exactly one match, found {count}")
        source = source.replace(old, new, 1)
    path.write_text(source, encoding="utf-8")

# Translation lookup: use the active Minecraft locale but retain catalogue fallbacks.
edit("src/main/java/com/baroxvs/client/gui/L10n.java", [
    ("    public static String module(ModuleCatalog.Module module) {\n        return Text.translatable(\"baroxvs.module.\" + module.id()).getString();\n    }",
     "    public static String module(ModuleCatalog.Module module) {\n        String key = \"baroxvs.module.\" + module.id();\n        String translated = Text.translatable(key).getString();\n        return translated.equals(key) ? module.name() : translated;\n    }\n\n    public static String moduleDescription(ModuleCatalog.Module module) {\n        String key = \"baroxvs.module.\" + module.id() + \".description\";\n        String translated = Text.translatable(key).getString();\n        return translated.equals(key) ? module.description() : translated;\n    }\n\n    public static String category(String category) {\n        String suffix = switch (category) {\n            case \"Effects\" -> \"effects\";\n            case \"Trails\" -> \"trails\";\n            case \"Cosmetics\" -> \"cosmetics\";\n            case \"HUD\" -> \"hud\";\n            case \"Misc\" -> \"misc\";\n            case \"Themes\" -> \"themes\";\n            default -> \"\";\n        };\n        if (suffix.isEmpty()) return category;\n        String key = \"baroxvs.modules.\" + suffix;\n        String translated = Text.translatable(key).getString();\n        return translated.equals(key) ? category : translated;\n    }", "localized module/category fallbacks")
])

# Compact ClickGUI: translated names/descriptions/category captions and real mod version.
edit("src/main/java/com/baroxvs/client/gui/ModuleClickGuiScreen.java", [
    ("import com.baroxvs.client.theme.Theme;\n", "import com.baroxvs.client.theme.Theme;\nimport net.fabricmc.loader.api.FabricLoader;\n", "FabricLoader import"),
    ("    private final BaroxConfig cfg;\n", "    private static final String VERSION_LABEL = FabricLoader.getInstance().getModContainer(\"baroxvs\")\n            .map(container -> \"v\" + container.getMetadata().getVersion().getFriendlyString())\n            .orElse(\"Visual Client\");\n\n    private final BaroxConfig cfg;\n", "version metadata"),
    ("String label = category.equals(\"All\") ? \"ALL MODULES\" : category.toUpperCase(Locale.ROOT);",
     "String label = category.equals(\"All\") ? L10n.tr(\"modules.all\").toUpperCase(Locale.ROOT)\n                    : L10n.category(category).toUpperCase(Locale.ROOT);", "localized category label"),
    ("Ui.text(c, textRenderer, \"v039  ·  \" + enabledCount + \"/\" + allCount + \" ACTIVE\",",
     "Ui.text(c, textRenderer, VERSION_LABEL + \"  ·  \" + enabledCount + \"/\" + allCount + \" \" + L10n.tr(\"modules.active\"),", "stale version badge"),
    ("String shown = search.isEmpty() ? (searchFocused ? \"\" : \"SEARCH MODULES\") : search;",
     "String shown = search.isEmpty() ? (searchFocused ? \"\" : L10n.tr(\"modules.search\").toUpperCase(Locale.ROOT)) : search;", "localized search prompt"),
    ("        String name = Ui.fit(textRenderer, module.name(), availableText, 0.55f * uiScale);\n        String detail = module.kind() == ModuleCatalog.Kind.CYCLE\n                ? \"STYLE \" + (cfg.style(module.id()) + 1)\n                : module.description();",
     "        String name = Ui.fit(textRenderer, L10n.module(module), availableText, 0.55f * uiScale);\n        String detail = module.kind() == ModuleCatalog.Kind.CYCLE\n                ? \"STYLE \" + (cfg.style(module.id()) + 1)\n                : L10n.moduleDescription(module);", "localized module card"),
    ("        if (module.name().toLowerCase(Locale.ROOT).contains(needle)\n                || module.description().toLowerCase(Locale.ROOT).contains(needle)\n                || module.id().toLowerCase(Locale.ROOT).contains(needle)) return true;",
     "        if (L10n.module(module).toLowerCase(Locale.ROOT).contains(needle)\n                || L10n.moduleDescription(module).toLowerCase(Locale.ROOT).contains(needle)\n                || module.name().toLowerCase(Locale.ROOT).contains(needle)\n                || module.description().toLowerCase(Locale.ROOT).contains(needle)\n                || module.id().toLowerCase(Locale.ROOT).contains(needle)) return true;", "localized module search"),
    ("            if (L10n.module(child).toLowerCase(Locale.ROOT).contains(needle)\n                    || child.name().toLowerCase(Locale.ROOT).contains(needle)\n                    || child.description().toLowerCase(Locale.ROOT).contains(needle)\n                    || child.id().toLowerCase(Locale.ROOT).contains(needle)) return true;",
     "            if (L10n.module(child).toLowerCase(Locale.ROOT).contains(needle)\n                    || L10n.moduleDescription(child).toLowerCase(Locale.ROOT).contains(needle)\n                    || child.name().toLowerCase(Locale.ROOT).contains(needle)\n                    || child.description().toLowerCase(Locale.ROOT).contains(needle)\n                    || child.id().toLowerCase(Locale.ROOT).contains(needle)) return true;", "localized child search")
])

# Settings sheet: avoid a second full-screen dim pass and defer disk writes until slider release.
edit("src/main/java/com/baroxvs/client/gui/ModuleSettingsScreen.java", [
    ("    private int activeSlider = -1;\n    private int activeSliderBarX, activeSliderBarW;\n",
     "    private int activeSlider = -1;\n    private boolean sliderDirty;\n", "slider dirty state"),
    ("        // Keep settings in a compact floating sheet instead of replacing the screen\n        // with a full-width opaque surface.\n        context.fillGradient(0, 0, width, height, 0x65040A13, 0x76070D17);\n        Theme theme = Themes.current(config);",
     "        // renderBackground() owns the single dim pass; do not darken the world twice.\n        Theme theme = Themes.current(config);", "duplicate settings backdrop"),
    ("        activeSliderBarX = x;\n        activeSliderBarW = w;\n", "", "unused slider geometry fields"),
    ("        write(option.key(), Math.max(option.min(), Math.min(option.max(), value)));\n        config.save();",
     "        write(option.key(), Math.max(option.min(), Math.min(option.max(), value)));\n        sliderDirty = true;", "per-frame settings disk write"),
    ("        if (button == 0 && activeSlider >= 0) {\n            activeSlider = -1;\n            config.save();\n            return true;\n        }",
     "        if (button == 0 && activeSlider >= 0) {\n            activeSlider = -1;\n            if (sliderDirty) config.save();\n            sliderDirty = false;\n            return true;\n        }", "save slider once on release")
])

# HUD renderer: fix initial World Monitor cache, screen-bound layout, graph fill, and stale state.
p = ROOT / "src/main/java/com/baroxvs/client/hud/HudRenderer.java"
s = p.read_text(encoding="utf-8")
changes = [
    ("    private final float[] keyPressBlend = new float[6];\n", "    private final float[] keyPressBlend = new float[6];\n    private static final EquipmentSlot[] ARMOR_SLOTS = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};\n", "shared armor slots"),
    ("            biomeToastCooldowns.clear();\n            return;", "            biomeToastCooldowns.clear();\n            targetRef = null;\n            targetPrevHealth = 0f;\n            targetName = \"\";\n            targetHealth = 0f;\n            targetMax = 0f;\n            targetDist = 0f;\n            targetSeenMs = 0L;\n            popups.clear();\n            return;", "world unload HUD state reset"),
    ("        if (ticks - worldInfoRefreshTick >= 10) {", "        if (worldInfoRefreshTick == Integer.MIN_VALUE || ticks - worldInfoRefreshTick >= 10) {", "World Monitor initial cache sentinel"),
    ("        popups.add(new Popup(text, color, System.currentTimeMillis(), ThreadLocalRandom.current().nextInt(-16, 17)));",
     "        while (popups.size() >= 8) popups.remove(0);\n        popups.add(new Popup(text, color, System.currentTimeMillis(), ThreadLocalRandom.current().nextInt(-16, 17)));", "bounded damage popup queue"),
    ("        int maxWidth = Math.max(96, screenWidth - 12);\n        int width = Math.min(Math.max(154, tr.getWidth(biomeToastName) + 78), maxWidth);",
     "        int maxWidth = Math.max(1, screenWidth - 12);\n        int width = Math.min(Math.max(96, tr.getWidth(biomeToastName) + 78), maxWidth);", "biome toast narrow screen bounds"),
    ("int[] kb = cfg.isOn(\"keybinds\") ? keybindsSize(tr) : null;", "int[] kb = cfg.isOn(\"keybinds\") ? keybindsSize(tr, sw) : null;", "keybind sizing screen width"),
    ("            String biome = mc.world.getBiome(mc.player.getBlockPos()).getKey()\n                    .map(key -> key.getValue().getPath().replace('_', ' ')).orElse(\"unknown\");",
     "            String biome = biomeDisplayName(mc, mc.player);", "translated world card biome"),
    ("        EquipmentSlot[] slots = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};\n        int style = cfg.style(\"armor_hud\");",
     "        EquipmentSlot[] slots = ARMOR_SLOTS;\n        int style = cfg.style(\"armor_hud\");", "armor slot array allocation"),
    ("        int graphX = x + 7, graphY = y + 27, graphW = w - 14, graphH = 23;",
     "        int graphX = x + 7, graphY = y + 27, graphW = Math.max(1, w - 14), graphH = 23;", "fps graph minimum width"),
    ("        int step = Math.max(1, graphW / fpsSampleCount);\n        for (int i = 0; i < fpsSampleCount; i++) {\n            float sample = fpsSamples[(fpsSampleCursor - fpsSampleCount + i + fpsSamples.length) % fpsSamples.length];\n            int bh = Math.max(1, Math.round(Math.max(0f, sample) / ceiling * graphH));\n            int gx = graphX + i * step;\n            int color = cfg.style(\"fps_graph\") == 2\n                    ? Ui.lerp(th.secondary(), th.primary(), i / (float) Math.max(1, fpsSampleCount - 1))\n                    : th.primary();\n            int barWidth = Math.max(1, step - 2);\n            int top = graphY + graphH - bh;\n            Ui.roundRect(c, gx, top, Math.min(graphX + graphW, gx + barWidth), graphY + graphH,\n                    Math.max(1, Math.min(3, barWidth / 2)), widgetColor(color));\n        }",
     "        for (int i = 0; i < fpsSampleCount; i++) {\n            float sample = fpsSamples[(fpsSampleCursor - fpsSampleCount + i + fpsSamples.length) % fpsSamples.length];\n            int bh = Math.max(1, Math.round(Math.max(0f, sample) / ceiling * graphH));\n            int gx0 = graphX + i * graphW / fpsSampleCount;\n            int gx1 = graphX + (i + 1) * graphW / fpsSampleCount;\n            int barWidth = Math.max(1, gx1 - gx0 - 1);\n            int color = cfg.style(\"fps_graph\") == 2\n                    ? Ui.lerp(th.secondary(), th.primary(), i / (float) Math.max(1, fpsSampleCount - 1))\n                    : th.primary();\n            int top = graphY + graphH - bh;\n            Ui.roundRect(c, gx0, top, Math.min(graphX + graphW, gx0 + barWidth), graphY + graphH,\n                    Math.max(1, Math.min(3, barWidth / 2)), widgetColor(color));\n        }", "FPS graph samples span full width"),
]
for old, new, label in changes:
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"v049 {label}: expected one match, got {count}")
    s = s.replace(old, new, 1)

old = "        int w = tr.getWidth(\"BAROX VS\") + 16;\n        for (String line : lines) w = Math.max(w, tr.getWidth(line) + 16);\n        int h = 16 + lines.size() * 11;"
new = "        int naturalWidth = tr.getWidth(\"BAROX VS\") + 16;\n        for (String line : lines) naturalWidth = Math.max(naturalWidth, tr.getWidth(line) + 16);\n        int w = Math.min(Math.max(110, naturalWidth), Math.max(1, sw - 8));\n        int h = 16 + lines.size() * 11;"
if s.count(old) != 1: raise SystemExit("v049 Info Panel width: expected one match")
s = s.replace(old, new, 1)
old = "        for (String line : lines) {\n            c.drawText(tr, line, x + 8, ly, widgetColor(Ui.MUTED), false);\n            ly += 11;\n        }"
new = "        for (String line : lines) {\n            c.drawText(tr, Ui.fit(tr, line, w - 16, 1f), x + 8, ly, widgetColor(Ui.MUTED), false);\n            ly += 11;\n        }"
if s.count(old) != 1: raise SystemExit("v049 Info Panel line fit: expected one match")
s = s.replace(old, new, 1)

old = "    private int[] keybindsSize(TextRenderer tr) {\n        List<BaroxVsClient.KeyEntry> entries = BaroxVsClient.keyEntries();\n        if (entries.isEmpty()) return null;\n        int w = tr.getWidth(L10n.tr(\"hud.keybinds\")) + 24;\n        for (BaroxVsClient.KeyEntry e : entries) {\n            String key = e.key().getBoundKeyLocalizedText().getString();\n            w = Math.max(w, 10 + tr.getWidth(e.label()) + 12 + tr.getWidth(key) + 10);\n        }\n        return new int[]{w, 17 + entries.size() * 11 + 3};\n    }"
new = "    private int[] keybindsSize(TextRenderer tr, int screenWidth) {\n        List<BaroxVsClient.KeyEntry> entries = BaroxVsClient.keyEntries();\n        if (entries.isEmpty()) return null;\n        int naturalWidth = tr.getWidth(L10n.tr(\"hud.keybinds\")) + 24;\n        for (BaroxVsClient.KeyEntry e : entries) {\n            String key = e.key().getBoundKeyLocalizedText().getString();\n            naturalWidth = Math.max(naturalWidth, 10 + tr.getWidth(e.label()) + 12 + tr.getWidth(key) + 10);\n        }\n        int w = Math.min(Math.max(88, naturalWidth), Math.max(1, screenWidth - 8));\n        return new int[]{w, 17 + entries.size() * 11 + 3};\n    }"
if s.count(old) != 1: raise SystemExit("v049 keybind width helper: expected one match")
s = s.replace(old, new, 1)
old = "        for (BaroxVsClient.KeyEntry e : entries) {\n            String key = e.key().getBoundKeyLocalizedText().getString();\n            boolean active = e.moduleId() != null && cfg.isOn(e.moduleId());\n            c.drawText(tr, e.label(), x + 7, ly + 1, widgetColor(active ? th.primary() : 0xFFD4D7DD), false);\n            int kw = tr.getWidth(key) + 6;\n            int kx = x + w - kw - 4;\n            Ui.roundRect(c, kx, ly - 1, kx + kw, ly + 9, 3, Ui.alpha(th.primary(), 0x44));\n            c.drawText(tr, key, kx + 3, ly + 1, widgetColor(Ui.WHITE), false);\n            ly += 11;\n        }"
new = "        for (BaroxVsClient.KeyEntry e : entries) {\n            String key = e.key().getBoundKeyLocalizedText().getString();\n            int keyWidth = Math.min(Math.max(24, w / 3), tr.getWidth(key) + 6);\n            int keyX = x + w - keyWidth - 4;\n            String label = Ui.fit(tr, e.label(), Math.max(1, keyX - (x + 7) - 5), 1f);\n            boolean active = e.moduleId() != null && cfg.isOn(e.moduleId());\n            c.drawText(tr, label, x + 7, ly + 1, widgetColor(active ? th.primary() : 0xFFD4D7DD), false);\n            Ui.roundRect(c, keyX, ly - 1, keyX + keyWidth, ly + 9, 3, Ui.alpha(th.primary(), 0x44));\n            c.drawText(tr, Ui.fit(tr, key, Math.max(1, keyWidth - 6), 1f), keyX + 3, ly + 1, widgetColor(Ui.WHITE), false);\n            ly += 11;\n        }"
if s.count(old) != 1: raise SystemExit("v049 keybind row fit: expected one match")
s = s.replace(old, new, 1)

old = "        c.drawText(tr, Ui.fit(tr, cfg.musicTitle, maxW, 1f), tx, y + 6, widgetColor(Ui.WHITE), false);\n        Ui.text(c, tr, Ui.fit(tr, cfg.musicArtist, (int) (maxW / 0.8f), 0.8f), tx, y + 16,"
new = "        String musicTitle = cfg.musicTitle == null || cfg.musicTitle.isBlank() ? \"BAROX MUSIC\" : cfg.musicTitle;\n        String musicArtist = cfg.musicArtist == null ? \"\" : cfg.musicArtist;\n        c.drawText(tr, Ui.fit(tr, musicTitle, maxW, 1f), tx, y + 6, widgetColor(Ui.WHITE), false);\n        Ui.text(c, tr, Ui.fit(tr, musicArtist, (int) (maxW / 0.8f), 0.8f), tx, y + 16,"
if s.count(old) != 1: raise SystemExit("v049 null music metadata: expected one match")
s = s.replace(old, new, 1)

old = "    private List<String> collectWorldCardLines(MinecraftClient mc) {"
new = "    private String biomeDisplayName(MinecraftClient mc, PlayerEntity player) {\n        return mc.world.getBiome(player.getBlockPos()).getKey().map(key -> {\n            var id = key.getValue();\n            String translationKey = \"biome.\" + id.getNamespace() + \".\" + id.getPath();\n            String translated = Text.translatable(translationKey).getString();\n            return translated.equals(translationKey) ? id.getPath().replace('_', ' ') : translated;\n        }).orElse(\"unknown\");\n    }\n\n    private List<String> collectWorldCardLines(MinecraftClient mc) {"
if s.count(old) != 1: raise SystemExit("v049 biome helper insertion: expected one match")
s = s.replace(old, new, 1)
old = "            String biome = mc.world.getBiome(p.getBlockPos()).getKey()\n                    .map(key -> key.getValue().getPath()).orElse(\"unknown\");"
new = "            String biome = biomeDisplayName(mc, p);"
if s.count(old) != 1: raise SystemExit("v049 info biome label: expected one match")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")

# LRC parser: reject malformed seconds fields and protect timestamp arithmetic from overflow.
edit("src/main/java/com/baroxvs/client/hud/LyricFlowOverlay.java", [
    ("                    long seconds = Long.parseLong(matcher.group(2));\n                    String fraction = matcher.group(3);",
     "                    long seconds = Long.parseLong(matcher.group(2));\n                    if (seconds >= 60L) { lastEnd = matcher.end(); continue; }\n                    String fraction = matcher.group(3);", "LRC seconds validation"),
    ("                    stamps.add(minutes * 60_000L + seconds * 1_000L + millis + offsetMs);\n                    lastEnd = matcher.end();\n                } catch (NumberFormatException ignored) { }",
     "                    long baseMs = Math.addExact(Math.addExact(minutes * 60_000L, seconds * 1_000L), millis);\n                    stamps.add(Math.max(0L, Math.addExact(baseMs, offsetMs)));\n                    lastEnd = matcher.end();\n                } catch (NumberFormatException | ArithmeticException ignored) { }", "LRC timestamp overflow"),
    ("                parsed.add(new Cue(Math.max(0L, stamp), text));", "                parsed.add(new Cue(stamp, text));", "already clamped LRC stamps")
])

# Local skin profiles: cap input size and clear stale state after a failed reload.
edit("src/main/java/com/baroxvs/client/render/SkinStudio.java", [
    ("    private static final Path DIRECTORY = FabricLoader.getInstance().getConfigDir().resolve(\"baroxvs/skins\");",
     "    private static final Path DIRECTORY = FabricLoader.getInstance().getConfigDir().resolve(\"baroxvs/skins\");\n    private static final long MAX_SKIN_FILE_BYTES = 1L * 1024L * 1024L;\n\n    private static void clearPhoto(MinecraftClient client) {\n        if (textureId != null) {\n            client.getTextureManager().destroyTexture(textureId);\n            textureId = null;\n        }\n    }", "skin byte limit and texture cleanup helper"),
    ("            if (!Files.isRegularFile(file)) {\n                status = \"Missing: \" + file;\n                return false;\n            }\n            NativeImage image = NativeImage.read(Files.readAllBytes(file));",
     "            if (!Files.isRegularFile(file)) {\n                clearPhoto(client);\n                status = \"Missing: \" + file;\n                return false;\n            }\n            long size = Files.size(file);\n            if (size <= 0L || size > MAX_SKIN_FILE_BYTES) {\n                clearPhoto(client);\n                status = \"Skin PNG must be between 1 byte and 1 MB\";\n                return false;\n            }\n            NativeImage image = NativeImage.read(Files.readAllBytes(file));", "skin file size validation"),
    ("                image.close();\n                status = \"Invalid dimensions; expected 64x64 PNG\";\n                return false;",
     "                image.close();\n                clearPhoto(client);\n                status = \"Invalid dimensions; expected 64x64 PNG\";\n                return false;", "skin invalid dimension cleanup"),
    ("        } catch (IOException | RuntimeException exception) {\n            status = \"Load failed: \" + exception.getMessage();\n            return false;\n        }",
     "        } catch (IOException | RuntimeException exception) {\n            clearPhoto(client);\n            status = \"Load failed: \" + exception.getClass().getSimpleName();\n            return false;\n        }", "skin load failure cleanup")
])

# Android/mobile-friendly palette conversion: avoid java.awt.Color / java.desktop at runtime.
edit("src/main/java/com/baroxvs/client/theme/Themes.java", [
    ("import java.awt.Color;\n\n", "", "remove java.awt dependency"),
    ("            int primary = Color.HSBtoRGB(config.customHue, config.customSaturation, config.customBrightness) | 0xFF000000;\n            int secondary = Color.HSBtoRGB(config.customSecondaryHue,\n                    Math.max(0.35f, config.customSaturation * 0.88f),\n                    Math.max(0.25f, config.customBrightness * 0.63f)) | 0xFF000000;",
     "            int primary = hsbToRgb(config.customHue, config.customSaturation, config.customBrightness);\n            int secondary = hsbToRgb(config.customSecondaryHue,\n                    Math.max(0.35f, config.customSaturation * 0.88f),\n                    Math.max(0.25f, config.customBrightness * 0.63f));", "portable HSB conversion"),
    ("    public static Theme current(BaroxConfig config) {",
     "    /** java.awt.Color is not available in every Android-hosted Java runtime. */\n    private static int hsbToRgb(float hue, float saturation, float brightness) {\n        float h = Float.isFinite(hue) ? hue - (float)Math.floor(hue) : 0f;\n        float s = Float.isFinite(saturation) ? Math.max(0f, Math.min(1f, saturation)) : 0f;\n        float v = Float.isFinite(brightness) ? Math.max(0f, Math.min(1f, brightness)) : 0f;\n        float r, g, b;\n        if (s <= 0f) {\n            r = g = b = v;\n        } else {\n            float scaled = h * 6f;\n            int sector = (int)scaled;\n            float fraction = scaled - sector;\n            float p = v * (1f - s);\n            float q = v * (1f - s * fraction);\n            float t = v * (1f - s * (1f - fraction));\n            switch (Math.floorMod(sector, 6)) {\n                case 0 -> { r = v; g = t; b = p; }\n                case 1 -> { r = q; g = v; b = p; }\n                case 2 -> { r = p; g = v; b = t; }\n                case 3 -> { r = p; g = q; b = v; }\n                case 4 -> { r = t; g = p; b = v; }\n                default -> { r = v; g = p; b = q; }\n            }\n        }\n        return 0xFF000000 | (Math.round(r * 255f) << 16)\n                | (Math.round(g * 255f) << 8) | Math.round(b * 255f);\n    }\n\n    public static Theme current(BaroxConfig config) {", "portable HSB helper")
])

# Slightly lower sky ribbon tessellation to save per-frame vertex work on mobile GPUs.
edit("src/main/java/com/baroxvs/client/render/SkyboxEngine.java", [
    ("        final int segments = 88;", "        final int segments = 64;", "mobile aurora ribbon tessellation"),
    ("\n\n    private static void auroraColor(float[] palette, int band, int[] out) {\n        float t = (band % 3) / 2f;\n        float[] end = {0.42f, 0.82f, 0.70f};\n        out[0] = Math.round((palette[0] * (1f - t) + end[0] * t) * 255f);\n        out[1] = Math.round((palette[1] * (1f - t) + end[1] * t) * 255f);\n        out[2] = Math.round((palette[2] * (1f - t) + end[2] * t) * 255f);\n    }\n",
     "\n", "remove unused aurora helper")
])

translations = {
    "en_us.json": {"baroxvs.modules.all": "All modules", "baroxvs.modules.search": "Search"},
    "de_de.json": {"baroxvs.modules.all": "Alle Module", "baroxvs.modules.search": "Suchen"},
    "tr_tr.json": {"baroxvs.modules.all": "Tüm Modüller", "baroxvs.modules.search": "Ara"},
}
for locale, additions in translations.items():
    path = ROOT / "src/main/resources/assets/baroxvs/lang" / locale
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(additions)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

(ROOT / "SECOND_HALF_REVIEW_v049.md").write_text("""# BAROX VS v049 — Second source tranche review

Scope: the remaining 13 of 25 Java classes in sorted source-tree order. The first 12 classes reviewed in v048 are protected by SHA-256 checks and remain byte-identical in this release.

## Audited classes
- L10n, ModuleClickGuiScreen, ModuleSettingsScreen, Ui
- HudRenderer, LyricFlowOverlay
- BackgroundRendererMixin, LocalSkinMixin, SkyRenderingMixin
- SkinStudio, SkyboxEngine, Theme, Themes

## Findings fixed in this tranche
1. Corrected the World Monitor cache sentinel: subtracting Integer.MIN_VALUE from the tick counter overflowed, so its first snapshot could remain empty indefinitely.
2. Reworked the FPS graph bar coordinates so its complete fixed-size sample history spans the graph width.
3. Bounded the Info Panel, biome toast and Keybinds panel to the scaled viewport; long localized strings are fitted.
4. Reset target and popup state when the client world unloads, and cap the transient hit-popup queue.
5. Added null-safe Now Playing title/artist fallbacks and translated biome names in World Monitor and Info Panel.
6. Made compact ClickGUI module names, descriptions, category labels and search prompt follow Minecraft's active language; replaced the stale v039 badge with mod metadata.
7. Removed the second dim overlay in Module Settings and deferred settings-file writes during slider dragging until mouse release.
8. Hardened LRC timestamps against invalid seconds and signed overflow.
9. Added a 1 MB limit for local skin PNGs and clear stale texture state when a selected profile is missing or invalid.
10. Removed the java.awt.Color dependency from custom theme conversion for compatibility with Android-hosted Java runtimes that omit java.desktop.
11. Reduced aurora ribbon segments from 88 to 64 to lower per-frame vertex submissions while preserving curved ribbons.

The build validates that the first 12 Java classes from v048 remain unchanged. CI compiles with Java 21 / Gradle 8.12 and verifies the remapped Fabric JAR. Live Minecraft/ZalithLauncher2 runtime testing has not been performed.
""", encoding="utf-8")

edit("gradle.properties", [("mod_version=0.48.0", "mod_version=0.49.0", "Gradle version")])
edit("build.gradle", [("archiveFileName = 'BAROX-VS-v048.jar'", "archiveFileName = 'BAROX-VS-v049.jar'", "remapped jar name")])
edit("VERSION", [("BAROX VS v048", "BAROX VS v049", "VERSION stamp")])
edit("BUILD_VERSION.txt", [("BAROX VS v048", "BAROX VS v049", "BUILD_VERSION stamp")])

print("Applied BAROX VS v049 second tranche only (13/25 Java classes reviewed; first 12 preserved).")
