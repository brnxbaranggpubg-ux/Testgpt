from pathlib import Path
import sys

root = Path(sys.argv[1])
gui = root / "src/main/java/com/baroxvs/client/gui"
if not gui.is_dir():
    raise SystemExit(f"Missing GUI source directory: {gui}")

def replace_once(source, old, new, label):
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)

# One shared UI material adapter keeps module selection surfaces consistent.
helper = r'''package com.baroxvs.client.gui;

import net.minecraft.client.gui.DrawContext;

import java.util.Locale;
import java.util.Set;

/**
 * Shared Liquid Glass treatment for modules that render a glass material or
 * expose a glass-like style in their selection list.
 *
 * The helper deliberately uses DrawContext-only primitives. It does not
 * sample the framebuffer, allocate meshes, or depend on shader-pack state.
 */
public final class LiquidGlassModuleUi {
    private static final Set<String> GLASS_MODULES = Set.of(
            "player_glass", "hand_glow", "arm_glow", "held_item_glow", "self_glass",
            "liquid_rain", "glint", "music_aura_sync", "orbit_stars", "halo",
            "pet_glow", "jump_circle", "wing_glints", "wing_outline",
            "sky_mood", "sky_aurora", "sky_nebula", "sky_meteors", "sky_constellations",
            "keystrokes_hud", "biome_toast", "watermark", "dynamic_island", "crosshair_ring"
    );

    private LiquidGlassModuleUi() {}

    private static String key(String value) {
        return value == null ? "" : value.trim().toLowerCase(Locale.ROOT);
    }

    public static boolean isGlassVariant(String moduleId, String option) {
        if (GLASS_MODULES.contains(key(moduleId))) return true;
        String value = key(option);
        return value.contains("glass")
                || value.contains("pearl")
                || value.contains("prism")
                || value.contains("crystal")
                || value.contains("ice")
                || value.contains("frost")
                || value.contains("aurora");
    }

    public static boolean supports(String moduleId, String[] options) {
        if (GLASS_MODULES.contains(key(moduleId))) return true;
        if (options == null) return false;
        for (String option : options) {
            if (isGlassVariant(moduleId, option)) return true;
        }
        return false;
    }

    /**
     * Draws the shared glass material with a gentle hover response and a
     * stronger Fresnel rim for the selected module/choice.
     */
    public static void drawSurface(DrawContext context, int x, int y, int width, int height,
                                   int radius, int primary, int secondary, String moduleId,
                                   boolean selected, float hover, float phase) {
        if (context == null || width < 5 || height < 5) return;

        boolean glassModule = GLASS_MODULES.contains(key(moduleId));
        float p = Float.isFinite(phase) ? phase - (float) Math.floor(phase) : 0.18f;
        float h = Math.max(0f, Math.min(1f, hover));
        int baseAlpha = glassModule ? 0xB5 : 0x9C;
        int base = (baseAlpha << 24) | 0x081827;
        int accentColor = Ui.lerp(primary, secondary, glassModule ? 0.16f : 0.32f);
        int accent = Ui.alpha(accentColor, glassModule ? 0xB8 : 0x90);

        Ui.hudGlassPanel(context, x, y, x + width, y + height,
                radius, base, accent, p);
        Ui.glassFrame(context, x, y, x + width, y + height,
                radius, accentColor, p);

        if (selected) {
            context.drawBorder(x, y, width, height, Ui.alpha(primary, 0xE8));
            context.fill(x + 2, y + 1, x + Math.max(3, width - 2), y + 2,
                    Ui.alpha(0xFFFFFFFF, 0x3E));
            int stripeTop = y + Math.min(height / 3, Math.max(3, radius));
            int stripeBottom = y + height - Math.min(height / 3, Math.max(3, radius));
            if (stripeBottom > stripeTop) {
                context.fill(x + 1, stripeTop, x + 2, stripeBottom, Ui.alpha(primary, 0xC8));
            }
        } else if (h > 0.015f) {
            int alpha = Math.round(0x24 + h * 0x72);
            context.drawBorder(x, y, width, height, Ui.alpha(primary, alpha));
            context.fill(x + 3, y + 1, x + Math.max(4, width - 3), y + 2,
                    Ui.alpha(secondary, Math.round(0x10 + h * 0x28)));
        }
    }
}
'''
helper_path = gui / "LiquidGlassModuleUi.java"
helper_path.write_text(helper, encoding="utf-8")

# ClickGUI module rows: glass modules and modules with glass-themed choices use
# the same material and selected/hover state treatment.
click_path = gui / "ModuleClickGuiScreen.java"
click = click_path.read_text(encoding="utf-8")
old = '''        int fill = selected ? 0xFF29323E : over ? 0xFF222831 : 0xFF1A1F27;
        c.fill(x, y, x + w, y + h, fill);
        c.drawBorder(x, y, w, h, selected ? Ui.alpha(theme.primary(), 0xD0)
                : over ? 0xFF444D59 : 0xFF2B323C);
        if (selected) c.fill(x, y + s(5), x + s(3), y + h - s(5), theme.primary());
'''
new = '''        if (LiquidGlassModuleUi.supports(module.id(), module.options())) {
            LiquidGlassModuleUi.drawSurface(c, x, y, w, h, s(8), theme.primary(), theme.secondary(),
                    module.id(), selected, amount, animationTime * 0.12f);
        } else {
            int fill = selected ? 0xFF29323E : over ? 0xFF222831 : 0xFF1A1F27;
            c.fill(x, y, x + w, y + h, fill);
            c.drawBorder(x, y, w, h, selected ? Ui.alpha(theme.primary(), 0xD0)
                    : over ? 0xFF444D59 : 0xFF2B323C);
            if (selected) c.fill(x, y + s(5), x + s(3), y + h - s(5), theme.primary());
        }
'''
click = replace_once(click, old, new, "ClickGUI module row")

# The selected-module inspector receives the material matching the selected
# module; unrelated modules retain their existing neutral panel.
old = '''        c.fill(detailX, detailY - s(6), detailX + detailW, detailBottom,
                0xFF12151B);
        c.fill(detailX, detailY - s(6), detailX + detailW, detailY - s(5), LINE);
        ModuleCatalog.Module module = ModuleCatalog.byId(selectedModuleId);
'''
new = '''        ModuleCatalog.Module module = ModuleCatalog.byId(selectedModuleId);
        if (module != null && LiquidGlassModuleUi.supports(module.id(), module.options())) {
            LiquidGlassModuleUi.drawSurface(c, detailX, detailY - s(6), detailW,
                    detailBottom - (detailY - s(6)), s(10), theme.primary(), theme.secondary(),
                    module.id(), true, 0f, animationTime * 0.12f);
        } else {
            c.fill(detailX, detailY - s(6), detailX + detailW, detailBottom, 0xFF12151B);
            c.fill(detailX, detailY - s(6), detailX + detailW, detailY - s(5), LINE);
        }
'''
click = replace_once(click, old, new, "ClickGUI selected module inspector")

# Glass-parent child toggles keep the selected component visually connected to
# the parent material instead of appearing as detached opaque rows.
old = '''                c.fill(x, childY, x + innerW, childY + childH, 0xFF1D222A);
                c.drawBorder(x, childY, innerW, childH, 0xFF303844);
'''
new = '''                if (LiquidGlassModuleUi.supports(child.id(), child.options())) {
                    LiquidGlassModuleUi.drawSurface(c, x, childY, innerW, childH, s(6),
                            theme.primary(), theme.secondary(), child.id(), childOn, 0f,
                            animationTime * 0.12f);
                } else {
                    c.fill(x, childY, x + innerW, childY + childH, 0xFF1D222A);
                    c.drawBorder(x, childY, innerW, childH, 0xFF303844);
                }
'''
click = replace_once(click, old, new, "ClickGUI child module rows")
click_path.write_text(click, encoding="utf-8")

# Mobile chooser cards use the same module-aware glass treatment. Existing
# rounded controls below the card remain compatible with the v109 roundRect.
menu_path = gui / "BaroxMenuScreen.java"
menu = menu_path.read_text(encoding="utf-8")
old = '''        boolean cycle = module.kind() == ModuleCatalog.Kind.CYCLE;
        boolean enabled = !cycle && cfg.isOn(module.id());
        Ui.roundRect(c, x, y, x + w, y + h, 8, 0xFF142230);
'''
new = '''        boolean cycle = module.kind() == ModuleCatalog.Kind.CYCLE;
        boolean enabled = !cycle && cfg.isOn(module.id());
        if (LiquidGlassModuleUi.supports(module.id(), module.options())) {
            LiquidGlassModuleUi.drawSurface(c, x, y, w, h, 8, theme.primary(), theme.secondary(),
                    module.id(), enabled, 0f, (System.currentTimeMillis() % 11000L) / 11000.0f);
        } else {
            Ui.roundRect(c, x, y, x + w, y + h, 8, 0xFF142230);
        }
'''
menu = replace_once(menu, old, new, "Mobile module chooser card")
menu_path.write_text(menu, encoding="utf-8")

# In module settings, the actual selected glass-like option gets a dedicated
# accent-lit Liquid Glass capsule; other styles keep the shared standard glass.
settings_path = gui / "ModuleSettingsScreen.java"
settings = settings_path.read_text(encoding="utf-8")
old = '''        Ui.flatPanel(context, x, top, x + w, top + (compact ? 18 : 22), 10,
                0x8A182A35, Ui.alpha(theme.primary(), 0x58));
'''
new = '''        if (LiquidGlassModuleUi.isGlassVariant(target.id(), value)) {
            LiquidGlassModuleUi.drawSurface(context, x, top, w, compact ? 18 : 22, 10,
                    theme.primary(), theme.secondary(), target.id(), true, 0f,
                    (System.currentTimeMillis() % 11000L) / 11000.0f);
        } else {
            Ui.flatPanel(context, x, top, x + w, top + (compact ? 18 : 22), 10,
                    0x8A182A35, Ui.alpha(theme.primary(), 0x58));
        }
'''
settings = replace_once(settings, old, new, "Module style selector material")
settings_path.write_text(settings, encoding="utf-8")

# Version metadata: the build emits only the v110 Fabric JAR.
build = root / "build.gradle"
props = root / "gradle.properties"
version_file = root / "VERSION"
build_version = root / "BUILD_VERSION.txt"
for path in (build, props, version_file, build_version):
    if not path.is_file():
        raise SystemExit(f"Missing version file: {path}")
build_text = build.read_text(encoding="utf-8")
if "BAROX-VS-v109.jar" not in build_text:
    raise SystemExit("Unexpected build.gradle baseline: v109 JAR marker not found")
build.write_text(build_text.replace("BAROX-VS-v109.jar", "BAROX-VS-v110.jar"), encoding="utf-8")
prop_text = props.read_text(encoding="utf-8")
if "mod_version=1.09.0" not in prop_text:
    raise SystemExit("Unexpected Gradle version baseline: 1.09.0 not found")
props.write_text(prop_text.replace("mod_version=1.09.0", "mod_version=1.10.0"), encoding="utf-8")
version_file.write_text("BAROX VS v110\n", encoding="utf-8")
build_version.write_text("BAROX VS v110\n", encoding="utf-8")
print("v110 Liquid Glass module integration applied")
