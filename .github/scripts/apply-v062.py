from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")

def transform(rel, fn):
    path = root / rel
    old = path.read_text(encoding="utf-8")
    new = fn(old)
    if new == old:
        raise SystemExit(f"No change made to {rel}; expected source anchor was not found")
    path.write_text(new, encoding="utf-8")

ui_path = "src/main/java/com/baroxvs/client/gui/Ui.java"
def update_ui(source):
    glass_anchor = "    /**\n     * iOS-inspired Liquid Glass surface: transparent colour depth, adaptive tint,\n"
    if source.count(glass_anchor) != 1:
        raise SystemExit("Ui.java: expected exactly one original glass helper anchor")

    matte_helper = """    /**
     * Matte, opaque panel for interface chrome. No transparency layers, lensing,
     * specular highlights or animated reflections are applied.
     */
    public static void flatPanel(DrawContext c, int x1, int y1, int x2, int y2,
                                 int radius, int base, int accent) {
        if (x2 <= x1 || y2 <= y1) return;
        int width = x2 - x1;
        int height = y2 - y1;
        int maxRadius = Math.min(width / 2, height / 2);
        int r = Math.max(0, Math.min(maxRadius, radius));

        // Convert the old tint/opacity inputs to a stable, fully opaque matte surface.
        int baseAlpha = (base >>> 24) & 255;
        int solid = lerp(0xFF10151D, 0xFF000000 | (base & 0x00FFFFFF), baseAlpha / 255f);
        roundRectShape(c, x1, y1, x2, y2, r, solid);

        // A static, restrained theme marker replaces the old moving glass reflection.
        int accentAlpha = Math.min(72, ((accent >>> 24) & 255) / 3);
        if (width >= 36 && height >= 18 && accentAlpha >= 8) {
            int inset = Math.max(5, Math.min(r, width / 4));
            roundRectShape(c, x1 + inset, y1 + 1, x2 - inset, y1 + 2, 1,
                    alpha(accent, accentAlpha));
        }
    }

"""
    source = source.replace(glass_anchor, matte_helper + "    /**\n     * HUD-only Liquid Glass surface: transparent colour depth, adaptive tint,\n")

    # Keep the exact optical renderer available only to the in-game HUD renderer.
    source = source.replace("glassPanel(", "hudGlassPanel(")

    # The GUI glass-button primitive is no longer needed after switching controls to flatPanel.
    start = source.find("    /** Small interactive glass control, using the same optical material as large panels. */")
    if start < 0:
        raise SystemExit("Ui.java: glassButton method declaration was not found")
    end = source.find("\n    public static void circle(", start)
    if end < 0:
        raise SystemExit("Ui.java: glassButton method boundary was not found")
    source = source[:start] + source[end + 1:]
    return source

transform(ui_path, update_ui)

settings_path = "src/main/java/com/baroxvs/client/gui/ModuleSettingsScreen.java"
def update_settings(source):
    source = source.replace("Ui.glassPanel(", "Ui.flatPanel(")
    source = source.replace("Ui.glassButton(", "Ui.flatPanel(")
    source = re.sub(r",\s*visualTime\s*\*\s*[0-9.]+f(?:\s*\+\s*[0-9.]+f)?\)", ")", source)
    source = source.replace("    private float visualTime;\n", "")
    source = source.replace("        visualTime += Math.max(0.01f, Math.min(1f, delta));\n", "")
    if "visualTime" in source:
        raise SystemExit("ModuleSettingsScreen.java: stale animation-clock reference remains")
    return source

transform(settings_path, update_settings)

menu_path = "src/main/java/com/baroxvs/client/gui/BaroxMenuScreen.java"
transform(menu_path, lambda source: source.replace("Ui.glassPanel(", "Ui.flatPanel("))

# The optical method body is unchanged; only its name makes its HUD-only scope explicit.
hud_path = "src/main/java/com/baroxvs/client/hud/HudRenderer.java"
transform(hud_path, lambda source: source.replace("Ui.glassPanel(", "Ui.hudGlassPanel("))

# Stamp the new source bundle version.
transform("build.gradle", lambda s: s.replace("BAROX-VS-v061.jar", "BAROX-VS-v062.jar"))
transform("gradle.properties", lambda s: s.replace("mod_version=0.61.0", "mod_version=0.62.0"))
(root / "VERSION").write_text("BAROX VS v062\n", encoding="utf-8")
(root / "BUILD_VERSION.txt").write_text("BAROX VS v062\n", encoding="utf-8")
(root / "GUI_MATTE_REDESIGN_v062.md").write_text("""# BAROX VS v062 — Matte GUI surfaces

The previous Liquid Glass material is removed from the GUI chrome. Module settings, the legacy visual gallery cards and the music page now use fully opaque matte panels with restrained static theme accents. The main ClickGUI remains on its existing dark, flat layout.

The optical HUD renderer is retained unchanged apart from the helper rename Ui.glassPanel to Ui.hudGlassPanel; HUD widget appearance is intentionally unchanged. The Self Glass player cosmetic and its v061 material pilot are also unchanged. No module IDs, saved settings, cosmetic geometry, sky rendering or gameplay state are changed.

Validation is performed by the v062 source checker and Java 21 / Gradle 8.12 CI build. Live Minecraft/ZalithLauncher2 visual QA is not claimed.
""", encoding="utf-8")
