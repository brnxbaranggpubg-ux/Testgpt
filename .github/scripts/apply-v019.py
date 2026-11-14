#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")
catalog_path = root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java"
engine_path = root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java"

catalog = catalog_path.read_text(encoding="utf-8")
old_hand = '        toggle("hand_glow", "Hand Glow", "Soft colour-matched glow near your hand", EFFECTS, true);'
new_hand = '''        styled("hand_glow", "Hand Glow", "Paired glass highlights around both hands", EFFECTS, true,
                new String[]{"Pearl Glass", "Aurora Glass", "Rose Glass", "Jade Glass", "Ice Glass", "Sunset Glass"});
        styled("arm_glow", "Arm Glow", "Translucent light bands following both forearms", EFFECTS, false,
                new String[]{"Pearl Glass", "Aurora Glass", "Rose Glass", "Jade Glass", "Ice Glass", "Sunset Glass"});
        styled("held_item_glow", "Held Item Glow", "A soft crystal halo around items in either hand", EFFECTS, false,
                new String[]{"Pearl Glass", "Aurora Glass", "Rose Glass", "Jade Glass", "Ice Glass", "Sunset Glass"});
        styled("self_glass", "Self Glass", "A subtle translucent crystal shell around your character", EFFECTS, false,
                new String[]{"Pearl Glass", "Aurora Glass", "Rose Glass", "Jade Glass", "Ice Glass", "Sunset Glass"});'''
if old_hand not in catalog:
    raise SystemExit("Could not find existing Hand Glow module declaration.")
catalog = catalog.replace(old_hand, new_hand, 1)

old_hats = '{"Bamboo Kasa", "Imperial Kasa", "Moon Lantern Kasa", "Jade Festival Kasa", "Sakura Festival Kasa", "Crane Cloud Kasa", "Lotus Pearl Kasa"}'
new_hats = '{"Bamboo Kasa", "Imperial Kasa", "Moon Lantern Kasa", "Jade Festival Kasa", "Sakura Festival Kasa", "Crane Cloud Kasa", "Lotus Pearl Kasa", "Frost Jade Kasa", "Rose Quartz Kasa", "Moonlit Crane Kasa", "Golden Lotus Kasa"}'
if old_hats not in catalog:
    raise SystemExit("Could not find the v018 Chinese Kasa option list.")
catalog = catalog.replace(old_hats, new_hats, 1)
catalog_path.write_text(catalog, encoding="utf-8")

engine = engine_path.read_text(encoding="utf-8")

old_brim = '''        double brimRadius = (style == 1 || style == 3 ? 0.55 : 0.48) * scale
                * config.moduleValue("chinese_hat", "brim", 1f, 0.75f, 1.35f);'''
new_brim = '''        double brimRadius = (style == 1 || style == 3 || style == 7 || style == 9 ? 0.55 : 0.48) * scale
                * config.moduleValue("chinese_hat", "brim", 1f, 0.75f, 1.35f);'''
if old_brim not in engine:
    raise SystemExit("Could not find kasa brim size expression.")
engine = engine.replace(old_brim, new_brim, 1)

old_lift = '        double brimLift = style == 2 ? 0.075 : 0.035;'
new_lift = '        double brimLift = (style == 2 || style == 9) ? 0.075 : 0.035;'
if old_lift not in engine:
    raise SystemExit("Could not find kasa brim lift expression.")
engine = engine.replace(old_lift, new_lift, 1)

old_crown = '''        double crownHeight = (style == 1 ? 0.43 : style == 2 ? 0.32 : style == 3 ? 0.39 : 0.36) * scale;'''
new_crown = '''        double crownHeight = switch (style) {
            case 1 -> 0.43;
            case 2 -> 0.32;
            case 3 -> 0.39;
            case 7 -> 0.40;
            case 8 -> 0.37;
            case 9 -> 0.43;
            case 10 -> 0.39;
            default -> 0.36;
        } * scale;'''
if old_crown not in engine:
    raise SystemExit("Could not find kasa crown height expression.")
engine = engine.replace(old_crown, new_crown, 1)

hat_anchor = '        double tasselLength = config.moduleValue("chinese_hat", "tassel", 1f, 0.45f, 1.65f);'
hat_variants = '''        if (style == 7) {
            // Frost Jade Kasa: icy jade crest with a ring of small crystal drops.
            Vec3d crest = centre.add(forward.multiply(-innerRadius * 0.78)).add(0, crownHeight * 0.76, 0);
            int frost = scaleAlpha(withAlpha(0xFFB8F5ED, 0xF2), hatOpacity);
            int ice = scaleAlpha(withAlpha(0xFFE4FCFF, 0xF0), hatOpacity);
            drawRing(out, camera, centre.add(0, crownHeight * 0.64, 0), 0.17 * scale, frost, tick * 0.01, right, forward);
            for (int i = 0; i < 10; i++) {
                double a = i * Math.PI * 2.0 / 10.0;
                Vec3d at = crest.add(right.multiply(Math.cos(a) * 0.17 * scale))
                        .add(forward.multiply(Math.sin(a) * 0.17 * scale));
                drawDiamond(out, camera, at, 0.052 * scale, (i & 1) == 0 ? frost : ice, a);
            }
            drawDiamond(out, camera, crest, 0.090 * scale, ice, tick * 0.02);
        } else if (style == 8) {
            // Rose Quartz Kasa: a raised pink blossom, pearl centre and fine gold petals.
            Vec3d flower = centre.add(forward.multiply(-innerRadius * 0.85)).add(0, crownHeight * 0.70, 0);
            for (int petal = 0; petal < 7; petal++) {
                double a = petal * Math.PI * 2.0 / 7.0;
                Vec3d at = flower.add(right.multiply(Math.cos(a) * 0.105 * scale))
                        .add(0, Math.sin(a) * 0.065 * scale, 0);
                drawDiamond(out, camera, at, 0.061 * scale,
                        scaleAlpha(withAlpha((petal & 1) == 0 ? 0xFFFFB7D4 : 0xFFFFE3EF, 0xF0), hatOpacity), a);
            }
            drawRing(out, camera, flower, 0.045 * scale,
                    scaleAlpha(withAlpha(0xFFFFD98C, 0xF0), hatOpacity), tick * 0.02, right, forward);
            drawDiamond(out, camera, flower, 0.036 * scale, scaleAlpha(withAlpha(0xFFFFFFFF, 0xF8), hatOpacity), 0);
        } else if (style == 9) {
            // Moonlit Crane Kasa: pale crest with two swept feather-like ribbons.
            Vec3d crest = centre.add(forward.multiply(-innerRadius * 0.72)).add(0, crownHeight * 0.74, 0);
            int moon = scaleAlpha(withAlpha(0xFFE8F4FF, 0xF0), hatOpacity);
            int silver = scaleAlpha(withAlpha(0xFFB9D6E8, 0xE8), hatOpacity);
            drawRing(out, camera, crest.add(0, 0.045 * scale, 0), 0.115 * scale, moon, tick * 0.008, right, forward);
            for (int side : new int[]{-1, 1}) {
                Vec3d start = crest.add(right.multiply(side * 0.045 * scale));
                Vec3d mid = crest.add(right.multiply(side * 0.22 * scale)).add(0, 0.12 * scale, 0);
                Vec3d end = crest.add(right.multiply(side * 0.34 * scale)).add(0, -0.015 * scale, 0);
                ribbon(out, camera, start, mid, right, 0.036 * scale, moon);
                ribbon(out, camera, mid, end, right, 0.022 * scale, silver);
                drawDiamond(out, camera, end, 0.044 * scale, moon, side * 0.2);
            }
            drawStar(out, camera, crest.add(0, 0.11 * scale, 0), 0.075 * scale, moon, tick * 0.02);
        } else if (style == 10) {
            // Golden Lotus Kasa: layered golden petals around a small jade pearl.
            Vec3d lotus = centre.add(0, crownHeight * 0.84, 0);
            int gold = scaleAlpha(withAlpha(0xFFFFD77B, 0xF2), hatOpacity);
            int paleGold = scaleAlpha(withAlpha(0xFFFFF0C4, 0xEE), hatOpacity);
            for (int petal = 0; petal < 10; petal++) {
                double a = petal * Math.PI * 2.0 / 10.0;
                Vec3d at = lotus.add(right.multiply(Math.cos(a) * 0.13 * scale))
                        .add(forward.multiply(Math.sin(a) * 0.13 * scale));
                drawDiamond(out, camera, at, 0.066 * scale, (petal & 1) == 0 ? gold : paleGold, a);
            }
            drawRing(out, camera, lotus, 0.075 * scale, paleGold, tick * 0.012, right, forward);
            drawGlassOrb(out, camera, lotus.add(0, 0.025 * scale, 0), 0.045 * scale,
                    scaleAlpha(withAlpha(0xFFD7FFE9, 0xEF), hatOpacity), right, forward);
        }
'''
if hat_anchor not in engine:
    raise SystemExit("Could not find Chinese Kasa tassel anchor.")
engine = engine.replace(hat_anchor, hat_variants + hat_anchor, 1)

render_anchor = '''        if (targetingWater) return;
        if (config.isOn("wings")) renderWings(output, camera, player, partial);'''
render_replacement = '''        if (targetingWater) return;
        if (config.isOn("self_glass") || config.isOn("arm_glow")
                || config.isOn("hand_glow") || config.isOn("held_item_glow")) {
            renderGlowCosmetics(output, camera, player, partial, context.camera().getRotation());
        }
        if (config.isOn("wings")) renderWings(output, camera, player, partial);'''
if render_anchor not in engine:
    raise SystemExit("Could not find world cosmetic render insertion point.")
engine = engine.replace(render_anchor, render_replacement, 1)

method_anchor = '    private void renderChunkRain(VertexConsumer out, Vec3d camera, PlayerEntity player,'
glow_method = '''    /**
     * Draws glass and emissive-style cosmetic highlights as world-space meshes.
     * This pass does not allocate Spark objects or use Minecraft's particle system.
     */
    private void renderGlowCosmetics(VertexConsumer out, Vec3d camera, PlayerEntity player,
                                     float partial, Quaternionf cameraRotation) {
        Vec3d pos = player.getLerpedPos(partial);
        float yaw = MathHelper.lerpAngleDegrees(partial, player.prevYaw, player.getYaw());
        double angle = Math.toRadians(yaw);
        Vec3d right = new Vec3d(Math.cos(angle), 0, Math.sin(angle));
        Vec3d forward = new Vec3d(-Math.sin(angle), 0, Math.cos(angle));
        Vec3d up = new Vec3d(0, 1, 0);
        double pulse = 0.94 + 0.06 * Math.sin((tick + partial) * 0.075);

        if (config.isOn("self_glass")) {
            int body = withAlpha(glassColor("self_glass", false), 0x58);
            int accent = withAlpha(glassColor("self_glass", true), 0xA0);
            float opacity = config.fxOpacity * config.moduleValue("self_glass", "opacity", 0.78f, 0.10f, 1.0f);
            double scale = config.moduleValue("self_glass", "scale", 1f, 0.50f, 2.50f);
            Vec3d torso = pos.add(0, 1.02, 0);
            drawGlassOrb(out, camera, torso, 0.37 * scale * pulse, scaleAlpha(body, opacity), right, up);
            drawRing(out, camera, torso.add(0, 0.05, 0), 0.45 * scale,
                    scaleAlpha(accent, opacity), tick * 0.012, right, forward);
            drawRing(out, camera, pos.add(0, 1.62, 0), 0.22 * scale,
                    scaleAlpha(withAlpha(accent, 0x90), opacity), -tick * 0.016, right, up);
            drawRing(out, camera, pos.add(0, 0.22, 0), 0.36 * scale,
                    scaleAlpha(withAlpha(body, 0xA0), opacity), tick * 0.009, right, forward);
        }

        MinecraftClient client = MinecraftClient.getInstance();
        boolean firstPerson = client.options.getPerspective().isFirstPerson();
        boolean mainHeld = !player.getMainHandStack().isEmpty();
        boolean offHeld = !player.getOffHandStack().isEmpty();

        if (firstPerson) {
            Vector3f rightVector = new Vector3f(1, 0, 0).rotate(cameraRotation);
            Vector3f upVector = new Vector3f(0, 1, 0).rotate(cameraRotation);
            Vector3f forwardVector = new Vector3f(0, 0, 1).rotate(cameraRotation);
            Vec3d viewRight = new Vec3d(rightVector.x, rightVector.y, rightVector.z).normalize();
            Vec3d viewUp = new Vec3d(upVector.x, upVector.y, upVector.z).normalize();
            Vec3d viewForward = new Vec3d(forwardVector.x, forwardVector.y, forwardVector.z).normalize();

            Vec3d wrist = camera.add(viewRight.multiply(0.34)).add(viewUp.multiply(-0.29)).add(viewForward.multiply(0.62));
            Vec3d forearm = camera.add(viewRight.multiply(0.17)).add(viewUp.multiply(-0.17)).add(viewForward.multiply(0.48));
            if (config.isOn("arm_glow")) {
                int arm = withAlpha(glassColor("arm_glow", false), 0xB0);
                float opacity = config.fxOpacity * config.moduleValue("arm_glow", "opacity", 0.88f, 0.10f, 1.0f);
                double scale = config.moduleValue("arm_glow", "scale", 1f, 0.50f, 2.50f);
                ribbon(out, camera, forearm, wrist, viewUp, 0.090 * scale, scaleAlpha(arm, opacity));
                drawRing(out, camera, wrist, 0.105 * scale, scaleAlpha(withAlpha(glassColor("arm_glow", true), 0xD0), opacity), tick * 0.03, viewRight, viewForward);
            }
            if (config.isOn("hand_glow")) {
                float opacity = config.fxOpacity * config.moduleValue("hand_glow", "opacity", 0.95f, 0.10f, 1.0f);
                double scale = config.moduleValue("hand_glow", "scale", 1f, 0.50f, 2.50f);
                drawGlassOrb(out, camera, wrist, 0.105 * scale * pulse,
                        scaleAlpha(withAlpha(glassColor("hand_glow", false), 0xC0), opacity), viewRight, viewUp);
                drawStar(out, camera, wrist.add(viewUp.multiply(0.09)), 0.035 * scale,
                        scaleAlpha(withAlpha(glassColor("hand_glow", true), 0xE0), opacity), tick * 0.035, viewRight, viewUp);
            }
            if (config.isOn("held_item_glow") && mainHeld) {
                Vec3d item = wrist.add(viewForward.multiply(0.13)).add(viewUp.multiply(0.035));
                float opacity = config.fxOpacity * config.moduleValue("held_item_glow", "opacity", 0.96f, 0.10f, 1.0f);
                double scale = config.moduleValue("held_item_glow", "scale", 1f, 0.50f, 2.50f);
                int itemColor = scaleAlpha(withAlpha(glassColor("held_item_glow", false), 0xA8), opacity);
                drawGlassOrb(out, camera, item, 0.16 * scale * pulse, itemColor, viewRight, viewUp);
                drawRing(out, camera, item, 0.19 * scale,
                        scaleAlpha(withAlpha(glassColor("held_item_glow", true), 0xC0), opacity),
                        tick * 0.025, viewRight, viewUp);
            }
            if (config.isOn("held_item_glow") && offHeld) {
                Vec3d item = camera.add(viewRight.multiply(-0.31)).add(viewUp.multiply(-0.30)).add(viewForward.multiply(0.60));
                float opacity = config.fxOpacity * config.moduleValue("held_item_glow", "opacity", 0.96f, 0.10f, 1.0f);
                double scale = config.moduleValue("held_item_glow", "scale", 1f, 0.50f, 2.50f);
                drawGlassOrb(out, camera, item, 0.14 * scale, scaleAlpha(withAlpha(glassColor("held_item_glow", false), 0xA8), opacity), viewRight, viewUp);
                drawRing(out, camera, item, 0.17 * scale,
                        scaleAlpha(withAlpha(glassColor("held_item_glow", true), 0xC0), opacity), -tick * 0.02, viewRight, viewUp);
            }
            return;
        }

        for (int side : new int[]{-1, 1}) {
            Vec3d shoulder = pos.add(right.multiply(side * 0.25)).add(0, 1.32, 0);
            Vec3d elbow = pos.add(right.multiply(side * 0.31)).add(forward.multiply(0.015)).add(0, 1.08, 0);
            Vec3d wrist = pos.add(right.multiply(side * 0.36)).add(forward.multiply(0.055)).add(0, 0.83, 0);
            if (config.isOn("arm_glow")) {
                int arm = withAlpha(glassColor("arm_glow", false), 0xB0);
                int trim = withAlpha(glassColor("arm_glow", true), 0xD0);
                float opacity = config.fxOpacity * config.moduleValue("arm_glow", "opacity", 0.88f, 0.10f, 1.0f);
                double scale = config.moduleValue("arm_glow", "scale", 1f, 0.50f, 2.50f);
                ribbon(out, camera, shoulder, elbow, right, 0.070 * scale, scaleAlpha(arm, opacity));
                ribbon(out, camera, elbow, wrist, right, 0.058 * scale, scaleAlpha(trim, opacity));
                drawRing(out, camera, wrist, 0.105 * scale, scaleAlpha(trim, opacity), tick * 0.025, right, up);
            }
            if (config.isOn("hand_glow")) {
                float opacity = config.fxOpacity * config.moduleValue("hand_glow", "opacity", 0.95f, 0.10f, 1.0f);
                double scale = config.moduleValue("hand_glow", "scale", 1f, 0.50f, 2.50f);
                drawGlassOrb(out, camera, wrist, 0.095 * scale * pulse,
                        scaleAlpha(withAlpha(glassColor("hand_glow", false), 0xC0), opacity), right, up);
                drawRing(out, camera, wrist, 0.12 * scale,
                        scaleAlpha(withAlpha(glassColor("hand_glow", true), 0xD0), opacity), tick * 0.03, right, up);
            }
            boolean held = side == 1 ? mainHeld : offHeld;
            if (config.isOn("held_item_glow") && held) {
                Vec3d item = wrist.add(forward.multiply(0.18)).add(0, 0.07, 0);
                float opacity = config.fxOpacity * config.moduleValue("held_item_glow", "opacity", 0.96f, 0.10f, 1.0f);
                double scale = config.moduleValue("held_item_glow", "scale", 1f, 0.50f, 2.50f);
                drawGlassOrb(out, camera, item, 0.145 * scale * pulse,
                        scaleAlpha(withAlpha(glassColor("held_item_glow", false), 0xB0), opacity), right, up);
                drawRing(out, camera, item, 0.18 * scale,
                        scaleAlpha(withAlpha(glassColor("held_item_glow", true), 0xD0), opacity), -tick * 0.02, right, up);
            }
        }
    }

    private int glassColor(String moduleId, boolean secondary) {
        int style = Math.max(0, Math.min(5, config.style(moduleId)));
        int[] main = {0xFFBFEFFF, 0xFF83E8DD, 0xFFFFA9CE, 0xFF8FE4C4, 0xFF9BCBFF, 0xFFFFC879};
        int[] accent = {0xFFFFFFFF, 0xFFB7FFF4, 0xFFFFE5F0, 0xFFD7FFE9, 0xFFE6F6FF, 0xFFFFF0C8};
        return secondary ? accent[style] : main[style];
    }

'''
if method_anchor not in engine:
    raise SystemExit("Could not find renderChunkRain method anchor.")
engine = engine.replace(method_anchor, glow_method + method_anchor, 1)
engine_path.write_text(engine, encoding="utf-8")

# Keep fabric.mod.json's Gradle version placeholder untouched.

for path in [root / "gradle.properties", root / "settings.gradle", root / "README.md"]:
    if not path.exists():
        continue
    text = path.read_text(encoding="utf-8")
    revised = text.replace("BAROX-VS-v018", "BAROX-VS-v019")
    if path.name == "gradle.properties":
        revised = re.sub(r"(?m)^mod_version\s*=.*$", "mod_version=0.19.0", revised)
    if revised != text:
        path.write_text(revised, encoding="utf-8")

# Fail early if the project did not receive the required v019 source changes.
assert "held_item_glow" in catalog and "self_glass" in catalog and "arm_glow" in catalog
assert "renderGlowCosmetics" in engine and "glassColor" in engine
assert all(f"style == {i}" in engine for i in range(7, 11))
print("Applied v019 glass aura, dual-hand/arm/held-item glow and four additional Chinese Kasa styles.")
