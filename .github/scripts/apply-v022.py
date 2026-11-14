#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")

def read(rel):
    path = root / rel
    if not path.is_file():
        raise SystemExit(f"Missing v022 source file: {rel}")
    return path.read_text(encoding="utf-8")

def write(rel, value):
    path = root / rel
    path.write_text(value, encoding="utf-8")

def once(src, old, new, label):
    count = src.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return src.replace(old, new, 1)

# Upgrade the existing wing cosmetic into a style-selectable Celestial Wings module.
catalog_rel = "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java"
catalog = read(catalog_rel)
wing_pattern = re.compile(
    r'(?m)^(\s*)toggle\("wings",\s*"[^"]+",\s*"[^"]+",\s*COSMETICS,\s*(true|false)\);'
)
catalog, wing_count = wing_pattern.subn(
    lambda m: (
        m.group(1)
        + 'styled("wings", "Celestial Wings", "A luminous pair of ornamental wings with selectable celestial palettes", COSMETICS, '
        + m.group(2)
        + ', new String[]{"Aurora", "Moonlight", "Sakura", "Starlight", "Solar Flare", "Prism"});'
    ),
    catalog,
    count=1,
)
if wing_count != 1:
    raise SystemExit(f"Could not upgrade existing Wings module (matches: {wing_count}).")

new_modules = '''        styled("meteor_shower", "Meteor Shower", "A gentle stream of falling stars around your avatar", EFFECTS, false,
                new String[]{"Moon Dust", "Aurora Rain", "Rose Comets", "Prism Night"});
        styled("energy_shield", "Energy Shield", "Layered translucent rings form a decorative energy barrier", EFFECTS, false,
                new String[]{"Aqua Guard", "Violet Guard", "Rose Guard", "Golden Guard"});
        styled("dragon_aura", "Dragon Aura", "A graceful ribbon of light coils around your avatar", COSMETICS, false,
                new String[]{"Azure Wyrm", "Jade Wyrm", "Rose Wyrm", "Solar Wyrm"});
        styled("floating_crystals", "Floating Crystals", "Small faceted crystals drift in a calm orbit", EFFECTS, false,
                new String[]{"Ice Quartz", "Rose Quartz", "Amethyst", "Prism"});
        styled("rgb_outline", "RGB Outline", "Animated contour rings and light accents around your avatar", COSMETICS, false,
                new String[]{"Spectrum", "Neon Blue", "Violet Pulse", "Sunset"});
        styled("footprint_fx", "Footprint FX", "Subtle luminous marks appear beneath your steps", TRAILS, false,
                new String[]{"Stardust", "Frost", "Petals", "Prism"});
        styled("nameplate_designer", "Nameplate Designer", "A floating ornamental frame above your avatar", HUD, false,
                new String[]{"Minimal", "Crystal Frame", "Royal Frame", "Celestial Frame"});
        styled("weather_aura", "Weather Aura", "A soft orbit of snowflakes, petals or leaves", EFFECTS, false,
                new String[]{"Snowfall", "Sakura", "Golden Leaves", "Stardust"});
        styled("pet_companion", "Pet Companion", "A tiny floating crystal familiar follows beside you", COSMETICS, false,
                new String[]{"Pearl Sprite", "Blue Sprite", "Rose Sprite", "Golden Sprite"});
        styled("cosmic_halo", "Cosmic Halo", "Layered celestial rings and stars hover above your head", COSMETICS, false,
                new String[]{"Lunar", "Solar", "Nebula", "Prism"});
        styled("prism_trail", "Prism Trail", "A short multicolour trail follows your movement", TRAILS, false,
                new String[]{"Aurora", "Spectrum", "Pastel", "Neon"});
'''
catalog = once(
    catalog,
    '        toggle("music_visualizer", "Audio Visualizer", "Reactive liquid-glass rings and subtle highlights that respond to music", EFFECTS, true);',
    '        toggle("music_visualizer", "Audio Visualizer", "Reactive liquid-glass rings and subtle highlights that respond to music", EFFECTS, true);\n' + new_modules.rstrip(),
    "Register v022 cosmetic modules"
)
write(catalog_rel, catalog)

# Add the new render pass to the existing geometry-only world cosmetic dispatcher.
engine_rel = "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java"
engine = read(engine_rel)
engine = once(
    engine,
    '        if (config.isOn("music_aura_sync")) renderMusicAura(output, camera, player, partial);\n',
    '        if (config.isOn("music_aura_sync")) renderMusicAura(output, camera, player, partial);\n'
    '        renderV022Cosmetics(output, camera, player, partial);\n',
    "Connect v022 cosmetic render pass"
)

renderer = r'''    /**
     * v022 additions: deterministic, geometry-only cosmetic effects.
     * This pass never changes held-item transforms, player movement, damage or combat state.
     */
    private void renderV022Cosmetics(VertexConsumer out, Vec3d camera, PlayerEntity player, float partial) {
        Vec3d pos = player.getLerpedPos(partial);
        double time = tick + partial;
        float yaw = MathHelper.lerpAngleDegrees(partial, player.prevYaw, player.getYaw());
        double angle = Math.toRadians(yaw);
        Vec3d right = new Vec3d(Math.cos(angle), 0, Math.sin(angle));
        Vec3d forward = new Vec3d(-Math.sin(angle), 0, Math.cos(angle));
        Vec3d back = forward.multiply(-1);
        Vec3d up = new Vec3d(0, 1, 0);

        // Meteor Shower: stars descend through a small, fixed-radius sky volume.
        if (config.isOn("meteor_shower")) {
            int color = v022Color("meteor_shower");
            for (int i = 0; i < 8; i++) {
                double phase = (time * 0.018 + i * 0.137) % 1.0;
                double a = i * 2.399963229728653 + time * 0.002;
                Vec3d at = pos.add(Math.cos(a) * (1.4 + (i % 3) * 0.45),
                        1.9 + (1.0 - phase) * 3.2,
                        Math.sin(a) * (1.4 + (i % 3) * 0.45));
                drawStar(out, camera, at, 0.040 + (i % 2) * 0.012, color, time * 0.035 + i, right, up);
            }
        }

        // Energy Shield: three translucent, non-interactive geometry rings.
        if (config.isOn("energy_shield")) {
            Vec3d centre = pos.add(0, 1.02, 0);
            int color = withAlpha(v022Color("energy_shield"), 0xA8);
            double pulse = 1.0 + Math.sin(time * 0.065) * 0.035;
            drawRing(out, camera, centre, 0.72 * pulse, color, time * 0.012, right, forward);
            drawRing(out, camera, centre, 0.77 * pulse, withAlpha(color, 0x72), -time * 0.009, up, forward);
            drawRing(out, camera, centre, 0.82 * pulse, withAlpha(color, 0x58), time * 0.008, right, up);
        }

        // Dragon Aura: a smooth orbiting light ribbon, not a creature model.
        if (config.isOn("dragon_aura")) {
            int color = withAlpha(v022Color("dragon_aura"), 0xD0);
            Vec3d previous = null;
            for (int i = 0; i <= 24; i++) {
                double a = time * 0.025 + i * 0.28;
                Vec3d point = pos.add(Math.cos(a) * 0.66, 0.48 + i * 0.065,
                        Math.sin(a) * 0.66);
                if (previous != null) {
                    ribbon(out, camera, previous, point, up, 0.028 + 0.007 * Math.sin(i * 0.4), color);
                }
                previous = point;
            }
            drawStar(out, camera, previous, 0.085, withAlpha(color, 0xEE), time * 0.02, right, up);
        }

        // Floating Crystals: small faceted diamonds at staggered heights.
        if (config.isOn("floating_crystals")) {
            int color = withAlpha(v022Color("floating_crystals"), 0xDC);
            for (int i = 0; i < 7; i++) {
                double a = time * 0.014 + i * (Math.PI * 2.0 / 7.0);
                double y = 0.72 + (i % 3) * 0.47 + Math.sin(time * 0.045 + i) * 0.12;
                Vec3d at = pos.add(Math.cos(a) * 0.92, y, Math.sin(a) * 0.92);
                drawDiamond(out, camera, at, 0.074 + (i % 2) * 0.018, color, a + time * 0.01);
            }
        }

        // RGB Outline: layered contour bands around the avatar silhouette.
        if (config.isOn("rgb_outline")) {
            int[] colors = {0xFFFF5D9E, 0xFF65DFFF, 0xFFB58BFF, 0xFFFFD36E};
            for (int i = 0; i < 4; i++) {
                int c = withAlpha(colors[(i + (int) (time / 8)) % colors.length], 0xB0);
                double y = 0.18 + i * 0.48;
                double radius = i == 3 ? 0.28 : 0.34;
                drawRing(out, camera, pos.add(0, y, 0), radius, c,
                        time * (0.012 + i * 0.002), right, forward);
            }
            for (int side : new int[]{-1, 1}) {
                Vec3d a = pos.add(right.multiply(side * 0.31)).add(0, 0.36, 0);
                Vec3d b = pos.add(right.multiply(side * 0.27)).add(0, 1.48, 0);
                ribbon(out, camera, a, b, forward, 0.018,
                        withAlpha(colors[(int) (time / 5 + (side > 0 ? 1 : 0)) % colors.length], 0xA0));
            }
        }

        // Celestial Wings: decorative light-feather geometry on the back.
        if (config.isOn("wings")) {
            int color = withAlpha(v022WingColor(), 0xD8);
            for (int side : new int[]{-1, 1}) {
                Vec3d root = pos.add(back.multiply(0.25)).add(0, 1.23, 0);
                for (int i = 0; i < 7; i++) {
                    double spread = 0.24 + i * 0.075;
                    Vec3d tip = root.add(back.multiply(0.18 + i * 0.045))
                            .add(right.multiply(side * spread))
                            .add(0, 0.13 + Math.sin(i * 0.48 + time * 0.025) * 0.07, 0);
                    ribbon(out, camera, root, tip, up, 0.025 - i * 0.001, color);
                    drawStar(out, camera, tip, 0.026, withAlpha(color, 0xD0), time * 0.02 + i, right, up);
                }
            }
        }

        // Footprint FX: alternating ground-level glimmers, only while walking.
        if (config.isOn("footprint_fx") && player.isOnGround()) {
            double vx = player.getVelocity().x;
            double vz = player.getVelocity().z;
            double speed = Math.sqrt(vx * vx + vz * vz);
            if (speed > 0.035) {
                Vec3d travel = new Vec3d(-vx / speed, 0, -vz / speed);
                Vec3d side = new Vec3d(-travel.z, 0, travel.x);
                int color = withAlpha(v022Color("footprint_fx"), 0xB0);
                for (int i = 0; i < 3; i++) {
                    int step = (int) Math.floor(time / 7.0) - i;
                    double fade = 1.0 - i * 0.22;
                    Vec3d at = pos.add(travel.multiply(0.45 + i * 0.34))
                            .add(side.multiply((step & 1) == 0 ? 0.17 : -0.17))
                            .add(0, 0.025, 0);
                    drawRing(out, camera, at, 0.105 * fade, withAlpha(color, (int) (0xB0 * fade)),
                            0, side, travel);
                }
            }
        }

        // Nameplate Designer: an ornamental floating frame above the avatar.
        if (config.isOn("nameplate_designer")) {
            Vec3d centre = pos.add(0, 2.48, 0);
            int color = withAlpha(v022Color("nameplate_designer"), 0xD8);
            drawRing(out, camera, centre, 0.36, color, time * 0.008, right, forward);
            drawRing(out, camera, centre.add(0, 0.025, 0), 0.29,
                    withAlpha(0xFFFFFFFF, 0x80), -time * 0.006, right, forward);
            drawStar(out, camera, centre.add(right.multiply(-0.43)), 0.045, color, time * 0.03, right, up);
            drawStar(out, camera, centre.add(right.multiply(0.43)), 0.045, color, -time * 0.03, right, up);
        }

        // Weather Aura: drifting snow, petals or leaves selected from its style.
        if (config.isOn("weather_aura")) {
            int style = Math.max(0, Math.min(3, config.style("weather_aura")));
            int color = withAlpha(v022Color("weather_aura"), 0xC8);
            for (int i = 0; i < 9; i++) {
                double a = time * 0.018 + i * 2.399963229728653;
                double y = 0.72 + (i % 4) * 0.43 + Math.sin(time * 0.035 + i) * 0.16;
                Vec3d at = pos.add(Math.cos(a) * 0.88, y, Math.sin(a) * 0.88);
                if (style == 0) {
                    drawStar(out, camera, at, 0.035, color, a, right, up);
                } else {
                    drawDiamond(out, camera, at, style == 1 ? 0.045 : 0.052, color, a);
                }
            }
        }

        // Pet Companion: a small hovering crystal sprite with two tiny decorative fins.
        if (config.isOn("pet_companion")) {
            int color = withAlpha(v022Color("pet_companion"), 0xD8);
            Vec3d pet = pos.add(right.multiply(0.82 + Math.sin(time * 0.035) * 0.08))
                    .add(0, 1.05 + Math.sin(time * 0.055) * 0.14, 0)
                    .add(back.multiply(0.16));
            drawGlassOrb(out, camera, pet, 0.115, color, right, up);
            drawDiamond(out, camera, pet.add(right.multiply(-0.105)).add(0, 0.065, 0),
                    0.052, withAlpha(0xFFFFFFFF, 0xDA), -0.25);
            drawDiamond(out, camera, pet.add(right.multiply(0.105)).add(0, 0.065, 0),
                    0.052, withAlpha(0xFFFFFFFF, 0xDA), 0.25);
            drawStar(out, camera, pet.add(0, 0.15, 0), 0.026, color, time * 0.04, right, up);
        }

        // Cosmic Halo: a layered crown-like orbit above the head.
        if (config.isOn("cosmic_halo")) {
            Vec3d centre = pos.add(0, 2.06 + Math.sin(time * 0.035) * 0.025, 0);
            int color = withAlpha(v022Color("cosmic_halo"), 0xDC);
            drawRing(out, camera, centre, 0.34, color, time * 0.016, right, forward);
            drawRing(out, camera, centre.add(0, 0.055, 0), 0.25,
                    withAlpha(0xFFFFFFFF, 0x9A), -time * 0.012, right, forward);
            for (int i = 0; i < 4; i++) {
                double a = time * 0.012 + i * Math.PI / 2.0;
                Vec3d star = centre.add(right.multiply(Math.cos(a) * 0.38))
                        .add(forward.multiply(Math.sin(a) * 0.38)).add(0, 0.03, 0);
                drawStar(out, camera, star, 0.043, color, a, right, up);
            }
        }

        // Prism Trail: short spectrum glimmers behind the player while moving.
        if (config.isOn("prism_trail")) {
            double vx = player.getVelocity().x;
            double vz = player.getVelocity().z;
            double speed = Math.sqrt(vx * vx + vz * vz);
            if (speed > 0.025) {
                Vec3d trail = new Vec3d(-vx / speed, 0, -vz / speed);
                int[] colors = {0xFFFF6D9C, 0xFFFFC36B, 0xFFE8E86C, 0xFF72E0B8, 0xFF71C9FF, 0xFFB58CFF};
                for (int i = 0; i < colors.length; i++) {
                    Vec3d at = pos.add(trail.multiply(0.48 + i * 0.24))
                            .add(0, 0.10 + Math.sin(time * 0.06 + i) * 0.06, 0);
                    drawStar(out, camera, at, 0.032 + i * 0.002,
                            withAlpha(colors[i], 0xC0 - i * 0x12), time * 0.025 + i, right, up);
                }
            }
        }
    }

    private int v022Color(String moduleId) {
        int style = Math.max(0, Math.min(3, config.style(moduleId)));
        int[][] palette = {
                {0xFFB9E9FF, 0xFFFFBEDB, 0xFFD9C7FF, 0xFFFFD98F},
                {0xFF73DBF2, 0xFF9E8BFF, 0xFFFF8FBF, 0xFF6CE4BC},
                {0xFFFF9FC2, 0xFF8CDFFF, 0xFFC5A5FF, 0xFFFFCB75},
                {0xFFE6F7FF, 0xFFC6FFF0, 0xFFFFE0EA, 0xFFFFF2C8}
        };
        return palette[style][Math.floorMod(moduleId.hashCode(), 4)];
    }

    private int v022WingColor() {
        int style = Math.max(0, Math.min(5, config.style("wings")));
        int[] palette = {0xFF8DE4FF, 0xFFE9F3FF, 0xFFFFB7D5, 0xFFD8C6FF, 0xFFFFD58A, 0xFF9CEBDA};
        return palette[style];
    }

'''
engine = once(
    engine,
    "    private void renderGlowCosmetics(",
    renderer + "    private void renderGlowCosmetics(",
    "Add v022 cosmetic geometry renderer"
)
write(engine_rel, engine)

print("Applied v022: 11 new cosmetic modules, Celestial Wings style upgrade and geometry-only render effects.")
