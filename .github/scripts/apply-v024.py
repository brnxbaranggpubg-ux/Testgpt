#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")

def read(rel):
    path = root / rel
    if not path.is_file():
        raise SystemExit(f"Missing v024 source file: {rel}")
    return path.read_text(encoding="utf-8")

def write(rel, value):
    path = root / rel
    path.write_text(value, encoding="utf-8")

def once(src, old, new, label):
    count = src.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return src.replace(old, new, 1)

# Add an optional, style-selectable blend layer that reflects every enabled
# cosmetic/effect/trail module without changing gameplay, items or combat.
catalog_rel = "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java"
catalog = read(catalog_rel)
wing_entry = '''        styled("celestial_wings", "Celestial Wings", "A separate ornamental wing effect with celestial colour palettes", COSMETICS, false,
                new String[]{"Aurora", "Moonlight", "Sakura", "Starlight", "Solar Flare", "Prism"});'''
resonance_entry = wing_entry + '''
        styled("module_resonance", "Module Resonance", "A shared light signature that blends your active cosmetics, effects and trails", EFFECTS, false,
                new String[]{"Balanced", "Brilliant", "Soft", "Prismatic"});'''
catalog = once(catalog, wing_entry, resonance_entry, "Register Module Resonance")
write(catalog_rel, catalog)

engine_rel = "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java"
engine = read(engine_rel)
engine_marker = '''
    }

    private int v022Color(String moduleId) {'''
helper = r'''
        renderV024ModuleResonance(out, camera, pos, right, forward, up, time);
    }

    // Cache active module colours once per client tick to avoid per-frame list work.
    private long v024ModuleCacheTick = Long.MIN_VALUE;
    private int v024ModuleCacheCount;
    private int v024ModuleCacheRed = 185;
    private int v024ModuleCacheGreen = 225;
    private int v024ModuleCacheBlue = 255;

    /**
     * A restrained shared finish for all enabled visual modules.
     * Only cosmetic/effect/trail categories are sampled; HUD and utility modules
     * never create world geometry. This is visual-only and has no gameplay hooks.
     */
    private void renderV024ModuleResonance(VertexConsumer out, Vec3d camera, Vec3d pos,
                                           Vec3d right, Vec3d forward, Vec3d up, double time) {
        if (!config.isOn("module_resonance")) return;

        if (v024ModuleCacheTick != tick) {
            v024ModuleCacheTick = tick;
            int count = 0;
            int red = 0;
            int green = 0;
            int blue = 0;
            String[] categories = {"Cosmetics", "Effects", "Trails"};
            for (String category : categories) {
                for (ModuleCatalog.Module module : ModuleCatalog.inCategory(category)) {
                    if (module.kind() == ModuleCatalog.Kind.CYCLE || !config.isOn(module.id())) continue;
                    int hash = module.id().hashCode();
                    red += 104 + (hash & 0x8F);
                    green += 104 + ((hash >>> 8) & 0x8F);
                    blue += 104 + ((hash >>> 16) & 0x8F);
                    count++;
                }
            }
            v024ModuleCacheCount = count;
            if (count > 0) {
                v024ModuleCacheRed = red / count;
                v024ModuleCacheGreen = green / count;
                v024ModuleCacheBlue = blue / count;
            }
        }

        if (v024ModuleCacheCount == 0) return;

        int style = Math.max(0, Math.min(3, config.style("module_resonance")));
        int red = v024ModuleCacheRed;
        int green = v024ModuleCacheGreen;
        int blue = v024ModuleCacheBlue;
        if (style == 3) {
            int oldRed = red;
            red = blue;
            blue = green;
            green = oldRed;
        }
        int color = 0xFF000000 | (red << 16) | (green << 8) | blue;
        int ringAlpha = style == 1 ? 0xA0 : style == 2 ? 0x42 : 0x76;
        int detailAlpha = style == 1 ? 0xCE : style == 2 ? 0x65 : 0xA2;
        double intensity = style == 1 ? 1.16 : style == 2 ? 0.82 : 1.0;
        double pulse = 1.0 + Math.sin(time * 0.052) * 0.025;
        double radius = (0.69 + Math.min(6, v024ModuleCacheCount) * 0.018) * pulse * intensity;
        Vec3d centre = pos.add(0, 1.02, 0);

        drawRing(out, camera, centre, radius, withAlpha(color, ringAlpha),
                time * 0.009, right, forward);
        drawRing(out, camera, centre.add(0, 0.075, 0), radius * 0.84,
                withAlpha(color, Math.max(0x20, ringAlpha - 0x28)),
                -time * 0.007, right, up);

        int sparks = Math.min(8, Math.max(3, v024ModuleCacheCount + 2));
        for (int i = 0; i < sparks; i++) {
            double angle = time * 0.012 + i * (Math.PI * 2.0 / sparks);
            Vec3d at = centre.add(right.multiply(Math.cos(angle) * radius))
                    .add(forward.multiply(Math.sin(angle) * radius))
                    .add(0, Math.sin(time * 0.04 + i) * 0.045, 0);
            drawStar(out, camera, at, 0.025 + (i % 3) * 0.006,
                    withAlpha(color, detailAlpha), angle, right, up);
        }
    }

    private int v022Color(String moduleId) {'''
engine = once(engine, engine_marker, helper, "Connect shared visual resonance renderer")
write(engine_rel, engine)

# Make the module browser genuinely responsive on narrow phones and remove
# the old hard-coded module count/build label.
gui_rel = "src/main/java/com/baroxvs/client/gui/ModuleClickGuiScreen.java"
gui = read(gui_rel)
gui = once(gui, "panelW = Math.max(250, Math.min(960, width - 12));",
                "panelW = Math.max(220, Math.min(960, width - 12));",
                "Make ClickGUI width adaptive")
gui = once(gui, "sidebarW = panelW < 430 ? 82 : 148;",
                "sidebarW = panelW < 400 ? 72 : 148;",
                "Compact ClickGUI sidebar for mobile")
gui = once(gui, '"BUILD 021"', '"BUILD 024"', "Update ClickGUI build label")
gui = once(gui, '"78 MODULES"', 'allCount + " MODULES"', "Use live ClickGUI module count")
write(gui_rel, gui)

print("Applied v024: shared module resonance, style presets, cached visual-module sampling, and responsive live-count ClickGUI.")
