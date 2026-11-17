#!/usr/bin/env python3
"""BAROX VS v050: first ten visual modules audit and refinements."""
from pathlib import Path
import sys
root = Path(sys.argv[1]).resolve()
ep = root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java"
cp = root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java"

def once(s, old, new, label):
    n = s.count(old)
    if n != 1: raise SystemExit(f"v050 {label}: expected 1 match, found {n}")
    return s.replace(old, new, 1)

def method(s, start, end, body, label):
    a = s.find(start)
    if a < 0 or s.find(start, a + 1) >= 0: raise SystemExit(f"v050 {label}: bad start marker")
    b = s.find(end, a + len(start))
    if b < 0: raise SystemExit(f"v050 {label}: missing end marker")
    return s[:a] + body.rstrip() + "\n\n    " + s[b:]

e = ep.read_text(encoding="utf-8")
e = once(e, "import net.minecraft.registry.tag.FluidTags;\n", "", "FluidTags import")
e = once(e, "        boolean cameraInWater = client.world.getFluidState(net.minecraft.util.math.BlockPos.ofFloored(\n                camera.x, camera.y, camera.z)).isIn(FluidTags.WATER);\n        if (cameraInWater) return;\n", "", "underwater early return")
e = once(e, "import java.awt.Color;\n", "", "AWT import")
e = once(e, "    private static final int[] SIDES = {-1, 1};\n",
"""    private static final int[] SIDES = {-1, 1};
    private static final int[] GLINT_COLOURS = {0xFFFFFFFF, 0xFF8EF3FF, 0xFFFFB8D8, 0xFFD8D5FF, 0xFFFFD58D};

    private static int hsbToRgb(float hue, float saturation, float brightness) {
        float h = Float.isFinite(hue) ? hue - (float)Math.floor(hue) : 0f;
        float s = Float.isFinite(saturation) ? Math.max(0f, Math.min(1f, saturation)) : 0f;
        float v = Float.isFinite(brightness) ? Math.max(0f, Math.min(1f, brightness)) : 0f;
        float r, g, b;
        if (s <= 0f) r = g = b = v;
        else {
            float scaled = h * 6f;
            int sector = (int)Math.floor(scaled);
            float f = scaled - sector;
            float p = v * (1f - s), q = v * (1f - s * f), t = v * (1f - s * (1f - f));
            switch (sector % 6) {
                case 0 -> { r = v; g = t; b = p; }
                case 1 -> { r = q; g = v; b = p; }
                case 2 -> { r = p; g = v; b = t; }
                case 3 -> { r = p; g = q; b = v; }
                case 4 -> { r = t; g = p; b = v; }
                default -> { r = v; g = p; b = q; }
            }
        }
        return 0xFF000000 | (Math.round(r * 255f) << 16) | (Math.round(g * 255f) << 8) | Math.round(b * 255f);
    }
""", "mobile-safe HSB helper")
e = e.replace("Color.HSBtoRGB(", "hsbToRgb(")
e = e.replace("    /** Broad specular colour blooms are painted onto existing cosmetic surfaces. */\n", "")
e = once(e, "        int[] colours = {0xFFFFFFFF, 0xFF8EF3FF, 0xFFFFB8D8, 0xFFD8D5FF, 0xFFFFD58D};\n        int base = colours[Math.max(0, Math.min(colours.length - 1, config.style(\"glint\")))];",
"        int base = GLINT_COLOURS[Math.max(0, Math.min(GLINT_COLOURS.length - 1, config.style(\"glint\")))];",
"allocation-free Glint palette")

glints = r'''    /** Broad specular blooms follow actual cosmetic and hand locations in both camera modes. */
    private void renderGlints(VertexConsumer out, Vec3d camera, PlayerEntity player, float partial,
                              Quaternionf cameraRotation) {
        if (player.isInvisible() || player.isSpectator()) return;
        Vec3d pos = player.getLerpedPos(partial);
        float yaw = MathHelper.lerpAngleDegrees(partial, player.prevYaw, player.getYaw());
        double angle = Math.toRadians(yaw);
        Vec3d right = new Vec3d(Math.cos(angle), 0, Math.sin(angle));
        Vec3d back = new Vec3d(Math.sin(angle), 0, -Math.cos(angle));
        double pulse = 0.76 + 0.24 * Math.sin(renderAnimationTime * 0.10);
        int base = GLINT_COLOURS[Math.max(0, Math.min(GLINT_COLOURS.length - 1, config.style("glint")))];
        float opacity = config.fxOpacity * config.moduleValue("glint", "opacity", 0.92f, 0.10f, 1.0f);
        double scale = config.moduleValue("glint", "scale", 1f, 0.30f, 3.0f);
        int highlight = scaleAlpha(withAlpha(base, 0xC8), opacity * (0.38f + 0.42f * (float)pulse));
        MinecraftClient client = MinecraftClient.getInstance();
        int mainSide = player.getMainArm() == net.minecraft.util.Arm.RIGHT ? 1 : -1;
        int offSide = -mainSide;
        boolean mainHeld = !player.getMainHandStack().isEmpty();
        boolean offHeld = !player.getOffHandStack().isEmpty();
        if (client.options.getPerspective().isFirstPerson()) {
            Vector3f rv = new Vector3f(1, 0, 0).rotate(cameraRotation);
            Vector3f uv = new Vector3f(0, 1, 0).rotate(cameraRotation);
            Vector3f fv = new Vector3f(0, 0, 1).rotate(cameraRotation);
            Vec3d viewRight = new Vec3d(rv.x, rv.y, rv.z).normalize();
            Vec3d viewUp = new Vec3d(uv.x, uv.y, uv.z).normalize();
            Vec3d viewForward = new Vec3d(fv.x, fv.y, fv.z).normalize();
            if (mainHeld) {
                Vec3d item = camera.add(viewRight.multiply(mainSide * 0.34)).add(viewUp.multiply(-0.29)).add(viewForward.multiply(0.70));
                drawBillboard(out, camera, item, 0.24 * scale, 0.30 * scale, highlight,
                        renderAnimationTime * 0.009, viewRight, viewUp);
            }
            if (offHeld) {
                Vec3d item = camera.add(viewRight.multiply(offSide * 0.31)).add(viewUp.multiply(-0.30)).add(viewForward.multiply(0.60));
                drawBillboard(out, camera, item, 0.20 * scale, 0.27 * scale, scaleAlpha(highlight, 0.86f),
                        -renderAnimationTime * 0.008, viewRight, viewUp);
            }
            return;
        }
        if (config.isOn("wings")) for (int side : SIDES) {
            Vec3d sheen = wingPoint(pos, right, back, side, 0.62, renderWingFlapAngle, 0.045);
            drawBillboard(out, camera, sheen, 0.34 * scale, 0.22 * scale, highlight,
                    renderAnimationTime * 0.006, right, new Vec3d(0, 1, 0));
        }
        if (config.isOn("cape")) {
            Vec3d sheen = pos.add(back.multiply(0.37)).add(0, 0.95, 0);
            drawBillboard(out, camera, sheen, 0.42 * scale, 0.54 * scale, scaleAlpha(highlight, 0.72f),
                    0, right, new Vec3d(0, 1, 0));
        }
        if (config.isOn("chinese_hat") || config.isOn("headwear")) {
            Vec3d crown = pos.add(0, 2.00, 0).add(back.multiply(-0.04));
            drawBillboard(out, camera, crown, 0.30 * scale, 0.16 * scale, highlight,
                    0, right, new Vec3d(0, 1, 0));
        }
        if (mainHeld) {
            Vec3d item = pos.add(right.multiply(mainSide * 0.39)).add(back.multiply(0.12)).add(0, 0.91, 0);
            drawBillboard(out, camera, item, 0.22 * scale, 0.30 * scale, scaleAlpha(highlight, 0.88f),
                    renderAnimationTime * 0.007, right, new Vec3d(0, 1, 0));
        }
        if (offHeld) {
            Vec3d item = pos.add(right.multiply(offSide * 0.39)).add(back.multiply(0.12)).add(0, 0.91, 0);
            drawBillboard(out, camera, item, 0.20 * scale, 0.27 * scale, scaleAlpha(highlight, 0.78f),
                    -renderAnimationTime * 0.006, right, new Vec3d(0, 1, 0));
        }
    }'''
e = method(e, "    private void renderGlints(", "private void renderButterflyCompanion(", glints, "Glint renderer")

e = once(e, "    private void renderAura(VertexConsumer out, Vec3d camera, PlayerEntity player, float partial) {\n        Vec3d pos =",
"    private void renderAura(VertexConsumer out, Vec3d camera, PlayerEntity player, float partial) {\n        if (player.isInvisible() || player.isSpectator()) return;\n        Vec3d pos =", "Aura visibility gate")
e = once(e, "    private void renderMusicAura(VertexConsumer out, Vec3d camera, PlayerEntity player, float partial) {\n        float response =",
"    private void renderMusicAura(VertexConsumer out, Vec3d camera, PlayerEntity player, float partial) {\n        if (player.isInvisible() || player.isSpectator()) return;\n        float response =", "Music Aura visibility gate")

e = once(e,
"            Vec3d wrist = camera.add(viewRight.multiply(0.34)).add(viewUp.multiply(-0.29)).add(viewForward.multiply(0.62));\n            Vec3d forearm = camera.add(viewRight.multiply(0.17)).add(viewUp.multiply(-0.17)).add(viewForward.multiply(0.48));",
"            int mainSide = player.getMainArm() == net.minecraft.util.Arm.RIGHT ? 1 : -1;\n            int offSide = -mainSide;\n            Vec3d wrist = camera.add(viewRight.multiply(mainSide * 0.34)).add(viewUp.multiply(-0.29)).add(viewForward.multiply(0.62));\n            Vec3d forearm = camera.add(viewRight.multiply(mainSide * 0.17)).add(viewUp.multiply(-0.17)).add(viewForward.multiply(0.48));",
"first-person handedness")
e = once(e, "            if (config.isOn(\"held_item_glow\") && mainHeld) {",
'''            if (offHeld) {
                Vec3d offWrist = camera.add(viewRight.multiply(offSide * 0.34)).add(viewUp.multiply(-0.29)).add(viewForward.multiply(0.62));
                Vec3d offForearm = camera.add(viewRight.multiply(offSide * 0.17)).add(viewUp.multiply(-0.17)).add(viewForward.multiply(0.48));
                if (config.isOn("arm_glow")) {
                    float opacity = config.fxOpacity * config.moduleValue("arm_glow", "opacity", 0.88f, 0.10f, 1.0f);
                    double scale = config.moduleValue("arm_glow", "scale", 1f, 0.50f, 2.50f);
                    int arm = scaleAlpha(withAlpha(glassColor("arm_glow", false), 0xB0), opacity);
                    int trim = scaleAlpha(withAlpha(glassColor("arm_glow", true), 0xD0), opacity);
                    surfaceBloom(out, camera, offForearm, offWrist, viewUp, 0.090 * scale, arm);
                    drawSoftDisc(out, camera, offWrist, 0.105 * scale, trim, -renderAnimationTime * 0.03, viewRight, viewForward);
                }
                if (config.isOn("hand_glow")) {
                    float opacity = config.fxOpacity * config.moduleValue("hand_glow", "opacity", 0.95f, 0.10f, 1.0f);
                    double scale = config.moduleValue("hand_glow", "scale", 1f, 0.50f, 2.50f);
                    drawGlassOrb(out, camera, offWrist, 0.105 * scale * pulse,
                            scaleAlpha(withAlpha(glassColor("hand_glow", false), 0xC0), opacity), viewRight, viewUp);
                    drawSoftDisc(out, camera, offWrist.add(viewUp.multiply(0.035)), 0.072 * scale,
                            scaleAlpha(withAlpha(glassColor("hand_glow", true), 0xC0), opacity),
                            -renderAnimationTime * 0.018, viewRight, viewUp);
                }
            }
            if (config.isOn("held_item_glow") && mainHeld) {''', "first-person offhand rendering")
e = once(e, "Vec3d item = camera.add(viewRight.multiply(-0.31)).add(viewUp.multiply(-0.30)).add(viewForward.multiply(0.60));",
"Vec3d item = camera.add(viewRight.multiply(offSide * 0.31)).add(viewUp.multiply(-0.30)).add(viewForward.multiply(0.60));",
"offhand item alignment")
e = once(e, "        boolean firstPerson = client.options.getPerspective().isFirstPerson();\n        boolean mainHeld =",
"        boolean firstPerson = client.options.getPerspective().isFirstPerson();\n        if (player.isInvisible() || player.isSpectator()) return;\n        boolean mainHeld =", "Player Glass visibility gate")
e = once(e, "        for (int side : SIDES) {\n            Vec3d shoulder = pos.add(right.multiply(side * 0.25)).add(0, 1.32, 0);",
"        int mainSide = player.getMainArm() == net.minecraft.util.Arm.RIGHT ? 1 : -1;\n        for (int side : SIDES) {\n            Vec3d shoulder = pos.add(right.multiply(side * 0.25)).add(0, 1.32, 0);", "third-person handedness")
e = once(e, "            boolean held = side == 1 ? mainHeld : offHeld;",
"            boolean held = side == mainSide ? mainHeld : offHeld;", "third-person item mapping")

e = e.replace("    /** Player-attached soft surfaces replace orbiting points, stars, and halo strokes. */\n", "")
attached = r'''    /** Player-attached soft volumes replace point sprites and hollow halo strokes. */
    private void renderAttachedGeometryEffects(VertexConsumer out, Vec3d camera, PlayerEntity player, float partial) {
        if (player.isInvisible() || player.isSpectator()) return;
        Vec3d pos = player.getLerpedPos(partial);
        double time = renderAnimationTime;
        float opacity = config.fxOpacity;
        float yaw = MathHelper.lerpAngleDegrees(partial, player.prevYaw, player.getYaw());
        double yawRad = Math.toRadians(yaw);
        Vec3d right = new Vec3d(Math.cos(yawRad), 0, Math.sin(yawRad));
        Vec3d forward = new Vec3d(-Math.sin(yawRad), 0, Math.cos(yawRad));
        Vec3d up = new Vec3d(0, 1, 0);
        if (config.isOn("orbit_stars")) withModuleStrength("orbit_stars", () -> {
            double phase = time * 0.032;
            Theme theme = Themes.current(config);
            for (int i = 0; i < 2; i++) {
                double angle = phase + i * Math.PI;
                double orbitX = Math.cos(angle) * 0.47;
                double orbitZ = Math.sin(angle) * 0.28;
                double height = 1.10 + Math.sin(angle * 0.72) * 0.27;
                Vec3d centre = pos.add(right.multiply(orbitX)).add(forward.multiply(orbitZ)).add(0, height, 0);
                int color = i == 0 ? scaleAlpha(theme.primary(), opacity * 0.78f) : scaleAlpha(theme.secondary(), opacity * 0.72f);
                drawGlassOrb(out, camera, centre, i == 0 ? 0.145 : 0.125, color, right, up);
                drawBillboard(out, camera, centre.add(up.multiply(0.035)), 0.30, 0.22,
                        scaleAlpha(withAlpha(0xFFFFFFFF, 0x58), opacity * 0.70f), angle * 0.12, right, up);
            }
        });
        if (config.isOn("halo")) withModuleStrength("halo", () -> {
            Vec3d head = pos.add(0, player.isInSneakingPose() ? 1.72 : 2.02, 0);
            double scale = config.moduleValue("halo", "scale", 1f, 0.35f, 2.50f);
            float haloOpacity = opacity * config.moduleValue("halo", "opacity", 1f, 0.10f, 1f);
            double pulse = 1.0 + Math.sin(time * 0.055) * 0.025;
            drawSoftDisc(out, camera, head, 0.28 * scale * pulse, scaleAlpha(Themes.current(config).primary(), haloOpacity), time * 0.01, right, forward);
            drawSoftDisc(out, camera, head.add(0, 0.025 * scale, 0), 0.22 * scale * pulse,
                    scaleAlpha(0xFFFFFFFF, haloOpacity * 0.58f), -time * 0.008, right, forward);
            drawGlassOrb(out, camera, head.add(0, 0.045 * scale, 0), 0.085 * scale,
                    scaleAlpha(Themes.current(config).secondary(), haloOpacity * 0.74f), right, up);
        });
    }'''
e = method(e, "    private void renderAttachedGeometryEffects(", "private void renderAmbientGeometry(", attached, "Orbit/Halo geometry")
ep.write_text(e, encoding="utf-8")

c = cp.read_text(encoding="utf-8")
c = once(c, 'toggle("orbit_stars", "Orbit Glow", "Two soft filled light volumes hover around your player", EFFECTS, true);',
'toggle("orbit_stars", "Orbit Glow", "Two shaded glass orbs circle the player at different heights", EFFECTS, true);', "Orbit description")
c = once(c, 'toggle("halo", "Halo Bloom", "Layered filled light volumes above your head", EFFECTS, true);',
'toggle("halo", "Halo Bloom", "A floating soft halo with a small glass highlight above your head", EFFECTS, true);', "Halo description")
c = once(c, 'styled("hand_glow", "Hand Glow", "Paired glass highlights around both hands", EFFECTS, true,',
'styled("hand_glow", "Hand Glow", "Glass highlights follow the visible hands in first and third person", EFFECTS, true,', "Hand description")
c = once(c, 'styled("held_item_glow", "Held Item Glow", "A soft crystal halo around items in either hand", EFFECTS, false,',
'styled("held_item_glow", "Held Item Glow", "A soft crystal halo follows items in the main or off hand", EFFECTS, false,', "Held Item description")
cp.write_text(c, encoding="utf-8")

for rel, old, new in [
("gradle.properties", "mod_version=0.49.0", "mod_version=0.50.0"),
("build.gradle", "archiveFileName = 'BAROX-VS-v049.jar'", "archiveFileName = 'BAROX-VS-v050.jar'"),
("VERSION", "BAROX VS v049", "BAROX VS v050"),
("BUILD_VERSION.txt", "BAROX VS v049", "BAROX VS v050")]:
    p = root / rel
    p.write_text(once(p.read_text(encoding="utf-8"), old, new, rel), encoding="utf-8")

(root / "FIRST_TEN_MODULE_REVIEW_v050.md").write_text("""# BAROX VS v050 — First ten visual modules review

Scope: the first ten registrations in ModuleCatalog, traced through render dispatch, geometry, settings, configuration and parent-child activation.

## Audited modules
1. Aura Bloom (aura)
2. Aura Pulse (aura_pulse)
3. Glint (glint)
4. Music Aura Sync (music_aura_sync)
5. Orbit Glow (orbit_stars)
6. Halo Bloom (halo)
7. Player Glass (player_glass)
8. Hand Glow (hand_glow)
9. Arm Glow (arm_glow)
10. Held Item Glow (held_item_glow)

## Findings and changes
- Removed the camera-underwater early return that skipped the complete world-cosmetic pass; the translucent entity layer remains depth-tested against vanilla geometry.
- Rebuilt Orbit Glow as two shaded glass volumes moving at distinct heights instead of nearly coplanar discs at one centre.
- Added a small glass highlight to Halo Bloom while retaining its broad filled halo surfaces.
- Made first-person hand, arm and item effects respect PlayerEntity.getMainArm() and added matching off-hand accents when an off-hand item is visible.
- Made third-person held-item mapping respect handedness. Glint now follows each actually occupied hand, and in first person follows each visible held item rather than placing one generic bloom over the chest.
- Removed java.awt.Color from this renderer using a finite/clamped pure-Java HSB conversion. Moved the Glint palette to a static constant to avoid per-frame array allocation.
- Suppressed Aura, Music Aura, Player Glass, Glint, Orbit Glow and Halo on invisible/spectator players to prevent attached visuals revealing hidden player models.
- Updated module descriptions to match their visible behavior.

All 99 module IDs, child option IDs, parent groups and saved configuration keys are retained. No vanilla particle emitters, combat features, movement changes or server actions were added.

CI validates source invariants, Java 21 compilation and remapped JAR structure. Live Minecraft/ZalithLauncher2 visual QA has not yet been performed.
""", encoding="utf-8")
print("Applied BAROX VS v050 first-ten-module review.")
