#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")

def read(rel):
    path = root / rel
    if not path.is_file():
        raise SystemExit(f"Missing v020 source file: {rel}")
    return path.read_text(encoding="utf-8")

def write(rel, value):
    (root / rel).write_text(value, encoding="utf-8")

def once(src, old, new, label):
    count = src.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return src.replace(old, new, 1)

def replace_method(src, start, end, body, label):
    a = src.find(start)
    if a < 0:
        raise SystemExit(f"{label}: missing start marker {start!r}")
    b = src.find(end, a + len(start))
    if b < 0:
        raise SystemExit(f"{label}: missing end marker {end!r}")
    return src[:a] + body + src[b:]

# ---------------------------------------------------------------------------
# Module catalogue: consolidate ambient modules and remove duplicate/unused UI
catalog_rel = "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java"
catalog = read(catalog_rel)
catalog = once(
    catalog,
    '        toggle("aura_pulse", "Aura Pulse", "Slow breathing radius on the aura ring", EFFECTS, true);',
    '''        toggle("aura_pulse", "Aura Pulse", "Slow breathing radius on the aura ring", EFFECTS, true);
        styled("glint", "Glint", "Moving specular highlights on wings, capes, headwear and held items", EFFECTS, true,
                new String[]{"Pearl Flare", "Prism Glint", "Sakura Shimmer", "Moonlight", "Golden Glint"});
        toggle("music_aura_sync", "Music Aura Sync", "Liquid-glass aura rings pulse with the live audio level", EFFECTS, true);''',
    "Add glint and music aura modules")
catalog = once(
    catalog,
    '        toggle("jump_crystal", "Jump Crystal", "A rotating custom ring while airborne", TRAILS, true);',
    '''        styled("jump_crystal", "Jump Shapes", "Six selectable animated glass shapes on takeoff and while airborne", TRAILS, true,
                new String[]{"Crystal Halo", "Sakura Petals", "Butterfly Lift", "Moon Hearts", "Liquid Rings", "Prism Stars"});''',
    "Upgrade jump module to selectable shapes")
catalog = once(
    catalog,
    '        toggle("silk_ribbons", "Silk Ribbons", "Two flowing translucent ribbons orbiting the player", COSMETICS, false);',
    '''        toggle("silk_ribbons", "Silk Ribbons", "Two flowing translucent ribbons orbiting the player", COSMETICS, false);
        styled("butterfly_companion", "Butterfly Companion", "A close-up butterfly accessory with continuously animated wings", COSMETICS, false,
                new String[]{"Monarch", "Blue Morpho", "Sakura Moth", "Glasswing", "Luna Pearl"});''',
    "Add animated butterfly companion cosmetic")
catalog = once(
    catalog,
    '''        toggle("defeat_dissolve", "Defeat Dissolve", "A non-graphic shimmer dissolve when another player is defeated", EFFECTS, false);

''',
    "",
    "Remove Defeat Dissolve module")
catalog = once(
    catalog,
    '        toggle("crown_sparkles", "Crown Sparkles", "A small crown-shaped sparkle arc", EFFECTS, false);\n',
    "",
    "Remove duplicate Crown Sparkles module")
catalog = once(
    catalog,
    '        toggle("hit_numbers", "Hit Numbers", "Floating damage numbers near the crosshair", MISC, true);\n',
    "",
    "Remove Hit Numbers module")
catalog = once(
    catalog,
    '''        toggle("ambient_orbs", "Floating Orbs", "Soft luminous spheres that drift around the player", EFFECTS, true);
        toggle("ambient_cubes", "Floating Cubes", "Glass cubes that move around the player and react to swings", EFFECTS, true);
        toggle("ambient_bounce", "Impact Response", "Ambient orbs and cubes recoil when you hit them", EFFECTS, true);
        toggle("ambient_white", "Pearl Lighting", "Use a clean white pearl highlight on ambient objects", EFFECTS, true);''',
    '''        styled("ambient_forms", "Ambient Glass", "One control for floating pearl orbs, crystal cubes, stars and liquid rings", EFFECTS, true,
                new String[]{"Pearl Orbs", "Crystal Cubes", "Mixed Glass", "Prism Stars", "Liquid Rings"}, 2);
        toggle("ambient_bounce", "Impact Response", "Ambient glass objects gently recoil when interacted with", EFFECTS, true);''',
    "Consolidate ambient objects into one module")
catalog = once(
    catalog,
    '        toggle("music_visualizer", "Audio Visualizer", "Reactive light rings and drifting particles that respond to music", EFFECTS, true);',
    '        toggle("music_visualizer", "Audio Visualizer", "Reactive liquid-glass rings and subtle highlights that respond to music", EFFECTS, true);',
    "Clarify audio visualizer presentation")
write(catalog_rel, catalog)

# ---------------------------------------------------------------------------
# Sky catalogue: expand from 32 to 44 procedural presets
cosmetic_catalog_rel = "src/main/java/com/baroxvs/client/cosmetic/CosmeticCatalog.java"
cosmetic_catalog = read(cosmetic_catalog_rel)
cosmetic_catalog = once(
    cosmetic_catalog,
    '        "Golden Canopy", "Rose Aurora", "Moonlit Sakura"\n    };',
    '''        "Golden Canopy", "Rose Aurora", "Moonlit Sakura",
        "Opal Clouds", "Bluebell Twilight", "Sakura Rain", "Emerald Aurora",
        "Pearl Horizon", "Lavender Sea", "Golden Stardust", "Misty Mountains",
        "Rosewater Dawn", "Crystal Garden", "Moon Pearl", "Iridescent Heaven"
    };''',
    "Add twelve sky presets")
write(cosmetic_catalog_rel, cosmetic_catalog)

sky_rel = "src/main/java/com/baroxvs/client/render/SkyboxEngine.java"
sky = read(sky_rel)
sky = once(
    sky,
    '''            {0xFF23143D,0xFFAD619F,0xFFFFCADF}, {0xFF17234A,0xFF6E7BC1,0xFFFFC5DE}
    };''',
    '''            {0xFF23143D,0xFFAD619F,0xFFFFCADF}, {0xFF17234A,0xFF6E7BC1,0xFFFFC5DE},
            {0xFF202C4D,0xFFA5B7D8,0xFFF7E8EE}, {0xFF172A55,0xFF536DB2,0xFFB8D7F2},
            {0xFF4A1C4A,0xFFB95D89,0xFFFFD0DF}, {0xFF062F32,0xFF258E84,0xFFC4F4DC},
            {0xFF2A3455,0xFF9AAECD,0xFFFFE8D8}, {0xFF34265F,0xFF8C82C5,0xFFD9E9F8},
            {0xFF142044,0xFF6F67B8,0xFFFFD38F}, {0xFF1C334A,0xFF7697AA,0xFFE4F0E9},
            {0xFF5A3554,0xFFD18A9A,0xFFFFE5D0}, {0xFF203D55,0xFF8CC5C1,0xFFE7F5E8},
            {0xFF161A3E,0xFF686EAC,0xFFE4D5F4}, {0xFF172A4C,0xFF708CB8,0xFFFFE7C9}
    };''',
    "Extend procedural sky palette array")
sky = once(
    sky,
    "    /** A lightweight procedural panorama; 24 palettes require no downloaded assets. */",
    "    /** A lightweight procedural panorama; 44 palettes require no downloaded assets. */",
    "Update sky palette documentation")
sky = once(
    sky,
    "int starCount = preset >= 24 ? 118 : 86;",
    "int starCount = preset >= 32 ? 164 : preset >= 24 ? 118 : 86;",
    "Increase star density for latest sky set")
sky = once(
    sky,
    '''            int[] accents = {0xFFFFCBE4, 0xFFC4D8FF, 0xFFFFC28F, 0xFF7DE7E0,
                    0xFFDCC8FF, 0xFFE7C16E, 0xFFFFB8D8, 0xFFC6D4FF};''',
    '''            int[] accents = {0xFFFFCBE4, 0xFFC4D8FF, 0xFFFFC28F, 0xFF7DE7E0,
                    0xFFDCC8FF, 0xFFE7C16E, 0xFFFFB8D8, 0xFFC6D4FF,
                    0xFFFFE3EF, 0xFF8DDBC9, 0xFFFFD6AD, 0xFFD8D0FF};''',
    "Extend sky accent palette")
write(sky_rel, sky)

# ---------------------------------------------------------------------------
# Persistent config migration: merge old ambient toggles and retire redundant modules
config_rel = "src/main/java/com/baroxvs/client/config/BaroxConfig.java"
cfg = read(config_rel)
cfg = once(
    cfg,
    "    public int interfaceVersion = 0;",
    "    public int interfaceVersion = 0;\n    /** One-time v020 ambient-module consolidation and retired-widget migration. */\n    public int cosmeticVersion = 0;",
    "Add cosmetic config migration marker")
cfg = once(
    cfg,
    '''        styles.entrySet().removeIf(entry -> entry.getKey() == null || entry.getKey().isBlank() || entry.getValue() == null);
        if (interfaceVersion < 1) {''',
    '''        styles.entrySet().removeIf(entry -> entry.getKey() == null || entry.getKey().isBlank() || entry.getValue() == null);
        if (cosmeticVersion < 1) {
            migrateV020Modules(modules, styles);
            for (HudProfile profile : hudProfiles.values()) {
                if (profile != null) {
                    if (profile.modules == null) profile.modules = new HashMap<>();
                    if (profile.styles == null) profile.styles = new HashMap<>();
                    migrateV020Modules(profile.modules, profile.styles);
                }
            }
            cosmeticVersion = 1;
        }
        if (interfaceVersion < 1) {''',
    "Run v020 config migration")
insert = '''    private static void migrateV020Modules(Map<String, Boolean> moduleStates, Map<String, Integer> styleStates) {
        if (moduleStates == null || styleStates == null) return;
        Boolean previousOrbs = moduleStates.remove("ambient_orbs");
        Boolean previousCubes = moduleStates.remove("ambient_cubes");
        moduleStates.remove("ambient_white");

        if (previousOrbs != null || previousCubes != null) {
            boolean orbs = Boolean.TRUE.equals(previousOrbs);
            boolean cubes = Boolean.TRUE.equals(previousCubes);
            moduleStates.put("ambient_forms", orbs || cubes);
            styleStates.put("ambient_forms", orbs && cubes ? 2 : orbs ? 0 : 1);
        }

        // These old widgets overlapped the visual studio's newer cosmetic and status controls.
        moduleStates.remove("defeat_dissolve");
        moduleStates.remove("crown_sparkles");
        moduleStates.remove("hit_numbers");
    }

'''
cfg = once(
    cfg,
    "    private static float clamp01(float value, float fallback) {",
    insert + "    private static float clamp01(float value, float fallback) {",
    "Add v020 migration helper")
write(config_rel, cfg)

# ---------------------------------------------------------------------------
# Engine: replace duplicated ambient toggles with a single shape selector
engine_rel = "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java"
engine = read(engine_rel)
ambient_method = '''    private void updateAmbientBodies(MinecraftClient client, PlayerEntity player) {
        if (!config.isOn("ambient_forms")) {
            ambientBodies.clear();
            return;
        }
        ThreadLocalRandom random = ThreadLocalRandom.current();
        int target = Math.round(config.value("ambient_count", 24f, 4f, 80f));
        double range = config.value("ambient_range", 12f, 2f, 28f);
        float size = config.value("ambient_size", 0.085f, 0.035f, 0.22f);
        int form = config.style("ambient_forms");
        String composition = form + ":" + target;
        if (!composition.equals(ambientComposition)) {
            ambientBodies.clear();
            ambientComposition = composition;
        }
        while (ambientBodies.size() < target) {
            Shape shape = switch (form) {
                case 0 -> Shape.ORB;
                case 1 -> Shape.CUBE;
                case 3 -> Shape.STAR;
                case 4 -> Shape.RING;
                default -> random.nextBoolean() ? Shape.ORB : Shape.CUBE;
            };
            double phase = random.nextDouble(0, Math.PI * 2);
            double radiusFactor = random.nextDouble();
            double radius = 1.2 + radiusFactor * Math.max(0.1, range - 1.2);
            double height = random.nextDouble(0.7, 4.4);
            float sizeFactor = (float) random.nextDouble(0.82, 1.22);
            Vec3d offset = new Vec3d(Math.cos(phase) * radius, height, Math.sin(phase) * radius);
            ambientBodies.add(new AmbientBody(offset, shape, size * sizeFactor, sizeFactor, radius,
                    radiusFactor, height, phase, "ambient_forms"));
        }
        while (ambientBodies.size() > target) ambientBodies.remove(ambientBodies.size() - 1);

        double speed = config.value("ambient_speed", 0.55f, 0.10f, 2f);
        double audioKick = config.isOn("music_visualizer") || config.isOn("music_aura_sync")
                ? MusicEngine.audioLevel() * config.musicSensitivity : 0.0;
        for (AmbientBody body : ambientBodies) {
            body.size = size * body.sizeFactor;
            body.radius = 1.2 + body.radiusFactor * Math.max(0.1, range - 1.2);
            float objectFrequency = config.moduleValue("ambient_forms", "frequency", 1f, 0.25f, 3f);
            body.phase += 0.010 * speed * objectFrequency * (1.0 + Math.min(1.2, audioKick * 0.25));
            Vec3d targetOffset = new Vec3d(
                    Math.cos(body.phase) * body.radius,
                    body.height + Math.sin(body.phase * 0.72) * 0.62,
                    Math.sin(body.phase) * body.radius);
            Vec3d spring = targetOffset.subtract(body.offset).multiply(0.0032 * speed);
            body.velocity = body.velocity.multiply(body.hitFlash > 0 ? 0.986 : 0.91).add(spring);
            body.offset = body.offset.add(body.velocity);
            if (body.hitFlash > 0) body.hitFlash--;
        }
        boolean attackDown = client.currentScreen == null && client.options.attackKey.isPressed();
        if (config.isOn("ambient_bounce") && attackDown && !previousAttackDown) {
            repelAmbientBodies(player);
        }
        previousAttackDown = attackDown;
    }


'''
engine = replace_method(engine, "    private void updateAmbientBodies(", "    private boolean moduleTick(", ambient_method, "Replace ambient-body simulator")

# Detect takeoff once, in addition to the existing airborne animation.
engine = once(
    engine,
    '''        boolean onGround = player.isOnGround();
        if (config.isOn("landing_burst") && onGround && !wasOnGround && lastVelocityY < -0.25) {''',
    '''        boolean onGround = player.isOnGround();
        if (config.isOn("jump_crystal") && wasOnGround && !onGround && player.getVelocity().y > 0.10) {
            emitJumpBurst(player);
        }
        if (config.isOn("landing_burst") && onGround && !wasOnGround && lastVelocityY < -0.25) {''',
    "Add one-shot jump takeoff event")

jump_method = '''    private void emitJumpBurst(PlayerEntity player) {
        int style = config.style("jump_crystal");
        Shape shape = switch (style) {
            case 1 -> Shape.PETAL;
            case 2 -> Shape.BUTTERFLY;
            case 3 -> Shape.HEART;
            case 4 -> Shape.RING;
            case 5 -> Shape.STAR;
            default -> Shape.SHARD;
        };
        int[] colours = {0xFFBFEFFF, 0xFFFFB9D5, 0xFFFFC0D8, 0xFFE6D5FF, 0xFF9CECE2, 0xFFFFE5A9};
        int color = colours[Math.max(0, Math.min(colours.length - 1, style))];
        Vec3d centre = player.getPos().add(0, 0.10, 0);
        int count = style == 2 ? 6 : 8;
        for (int i = 0; i < count; i++) {
            double angle = Math.PI * 2.0 * i / count;
            Vec3d position = centre.add(Math.cos(angle) * 0.34, 0.02 + (i % 2) * 0.07, Math.sin(angle) * 0.34);
            Vec3d velocity = new Vec3d(Math.cos(angle) * 0.012, 0.022 + (i % 3) * 0.004, Math.sin(angle) * 0.012);
            add("jump_crystal", position, velocity, withAlpha(color, 0xE8), shape,
                    style == 2 ? 0.105f : 0.065f, (float) angle, 34);
        }
    }

'''
engine = once(
    engine,
    "    private void emitLanding(PlayerEntity player) {",
    jump_method + "    private void emitLanding(PlayerEntity player) {",
    "Add jump burst geometry")
engine = once(
    engine,
    '''        if (config.isOn("jump_crystal") && !p.isOnGround() && moduleTick("jump_crystal", 2)) {
            double phase = tick * 0.14;
            for (int i = 0; i < 4; i++) {
                double a = phase + Math.PI * 2 * i / 4;
                Vec3d at = pos.add(Math.cos(a) * 0.38, 0.16 + (i % 2) * 0.14, Math.sin(a) * 0.38);
                add("jump_crystal", at, new Vec3d(0, 0.012, 0), primary, Shape.SHARD, 0.04f, (float) a, 28);
            }
        }''',
    '''        if (config.isOn("jump_crystal") && !p.isOnGround() && moduleTick("jump_crystal", 2)) {
            int jumpStyle = config.style("jump_crystal");
            Shape jumpShape = switch (jumpStyle) {
                case 1 -> Shape.PETAL;
                case 2 -> Shape.BUTTERFLY;
                case 3 -> Shape.HEART;
                case 4 -> Shape.RING;
                case 5 -> Shape.STAR;
                default -> Shape.SHARD;
            };
            int[] jumpColours = {0xFFBFEFFF, 0xFFFFB9D5, 0xFFFFC0D8, 0xFFE6D5FF, 0xFF9CECE2, 0xFFFFE5A9};
            int jumpColor = jumpColours[Math.max(0, Math.min(jumpColours.length - 1, jumpStyle))];
            double phase = tick * 0.14;
            for (int i = 0; i < 4; i++) {
                double a = phase + Math.PI * 2 * i / 4;
                Vec3d at = pos.add(Math.cos(a) * 0.38, 0.16 + (i % 2) * 0.14, Math.sin(a) * 0.38);
                add("jump_crystal", at, new Vec3d(0, 0.012, 0), jumpColor, jumpShape,
                        jumpStyle == 2 ? 0.085f : 0.055f, (float) a, 28);
            }
        }''',
    "Select jump animation style while airborne")

# Keep glint as geometry and apply the glass material to all orb-shaped cosmetics.
engine = once(
    engine,
    "case ORB -> drawOrb(out, camera, spark.position, size, color, right, up);",
    "case ORB -> drawGlassOrb(out, camera, spark.position, size, color, right, up);",
    "Render every orb as liquid glass")
engine = once(
    engine,
    '''            if (body.shape == Shape.ORB) {
                drawGlassOrb(out, camera, world, size, color, right, up);
            } else {
                drawCube(out, camera, world, size, withAlpha(color, 0xC8), right, up);
                drawCube(out, camera, world, size * 0.66, withAlpha(0xFFFFFFFF, body.hitFlash > 0 ? 0xD0 : 0x72), right, up);
            }''',
    '''            switch (body.shape) {
                case ORB -> drawGlassOrb(out, camera, world, size, color, right, up);
                case CUBE -> {
                    drawCube(out, camera, world, size, withAlpha(color, 0xC8), right, up);
                    drawCube(out, camera, world, size * 0.66, withAlpha(0xFFFFFFFF, body.hitFlash > 0 ? 0xD0 : 0x72), right, up);
                }
                case STAR -> drawStar(out, camera, world, size * 1.45, color, body.phase, right, up);
                case RING -> {
                    drawRing(out, camera, world, size * 1.4, color, body.phase, right, up);
                    drawGlassOrb(out, camera, world, size * 0.45, withAlpha(color, 0x95), right, up);
                }
                default -> drawGlassOrb(out, camera, world, size, color, right, up);
            }''',
    "Render consolidated ambient shapes")

# The ambient module has only one id after migration.
engine = engine.replace('config.isOn("ambient_orbs")', 'config.isOn("ambient_forms")')
engine = engine.replace('config.isOn("ambient_cubes")', 'config.isOn("ambient_forms")')
engine = engine.replace('config.isOn("ambient_white") ? 0xDDF6FCFF : withAlpha(ambientTheme().primary(), 0xD8)',
                        'withAlpha(ambientTheme().primary(), 0xE0)')
engine = engine.replace('"ambient_orbs"', '"ambient_forms"').replace('"ambient_cubes"', '"ambient_forms"')

# Replace world-render dispatch, then add three direct-geometry cosmetic renderers.
world_method = '''    private void renderWorldEffects(WorldRenderContext context) {
        MinecraftClient client = MinecraftClient.getInstance();
        if (client.player == null || client.world == null || context.consumers() == null) return;
        Vec3d camera = context.camera().getPos();
        boolean cameraInWater = client.world.getFluidState(net.minecraft.util.math.BlockPos.ofFloored(
                camera.x, camera.y, camera.z)).isIn(FluidTags.WATER);
        if (cameraInWater) return;
        VertexConsumer output = context.consumers().getBuffer(RenderLayer.getEntityTranslucent(COSMETIC_TEXTURE));
        PlayerEntity player = client.player;
        float partial = context.tickCounter().getTickDelta(false);
        Quaternionf cameraRotation = context.camera().getRotation();

        if (config.isOn("liquid_rain")) renderChunkRain(output, camera, player, partial, client);
        boolean targetingWater = client.crosshairTarget instanceof BlockHitResult hit
                && client.world.getFluidState(hit.getBlockPos()).isIn(FluidTags.WATER);
        if (targetingWater) return;

        if (config.isOn("self_glass") || config.isOn("arm_glow")
                || config.isOn("hand_glow") || config.isOn("held_item_glow")) {
            renderGlowCosmetics(output, camera, player, partial, cameraRotation);
        }
        if (config.isOn("wings")) renderWings(output, camera, player, partial);
        if (config.isOn("chinese_hat")) renderChineseHat(output, camera, player, partial);
        else if (config.isOn("headwear")) renderHeadwear(output, camera, player, partial);
        if (config.isOn("hanfu_ornament")) renderHanfuOrnament(output, camera, player, partial);
        if (config.isOn("silk_ribbons")) renderSilkRibbons(output, camera, player, partial);
        if (config.isOn("cape")) renderCape(output, camera, player, partial);
        if (config.isOn("butterfly_companion")) renderButterflyCompanion(output, camera, player, partial, cameraRotation);
        if (config.isOn("glint")) renderGlints(output, camera, player, partial, cameraRotation);
        if (config.isOn("music_aura_sync")) renderMusicAura(output, camera, player, partial);
        renderCompanionShape(output, camera, player, partial);
        renderSparks(output, camera, cameraRotation, player.getLerpedPos(partial));
    }

'''
engine = replace_method(engine, "    private void renderWorldEffects(", "    private void renderGlowCosmetics(", world_method, "Replace world cosmetic dispatcher")

glint_and_aura_methods = '''    /** Geometry-only specular glints over cosmetic surfaces and held objects. */
    private void renderGlints(VertexConsumer out, Vec3d camera, PlayerEntity player, float partial,
                              Quaternionf cameraRotation) {
        Vec3d pos = player.getLerpedPos(partial);
        float yaw = MathHelper.lerpAngleDegrees(partial, player.prevYaw, player.getYaw());
        double angle = Math.toRadians(yaw);
        Vec3d right = new Vec3d(Math.cos(angle), 0, Math.sin(angle));
        Vec3d back = new Vec3d(Math.sin(angle), 0, -Math.cos(angle));
        Vector3f rv = new Vector3f(1, 0, 0).rotate(cameraRotation);
        Vector3f uv = new Vector3f(0, 1, 0).rotate(cameraRotation);
        Vec3d viewRight = new Vec3d(rv.x, rv.y, rv.z).normalize();
        Vec3d viewUp = new Vec3d(uv.x, uv.y, uv.z).normalize();

        int style = config.style("glint");
        int[] colours = {0xFFFFFFFF, 0xFF8EF3FF, 0xFFFFB8D8, 0xFFD8D5FF, 0xFFFFD58D};
        int base = colours[Math.max(0, Math.min(colours.length - 1, style))];
        float opacity = config.fxOpacity * config.moduleValue("glint", "opacity", 0.92f, 0.10f, 1.0f);
        double scale = config.moduleValue("glint", "scale", 1f, 0.30f, 3.0f);
        double pulse = 0.72 + 0.28 * Math.sin((tick + partial) * 0.16);

        if (config.isOn("wings")) {
            for (int side : new int[]{-1, 1}) {
                for (int i = 0; i < 3; i++) {
                    double t = 0.48 + i * 0.20;
                    Vec3d point = wingPoint(pos, right, back, side, t, 0.0, 0.0);
                    double phase = tick * 0.035 + side * 0.8 + i * 1.7;
                    int alpha = Math.round((90 + 150 * (0.5 + 0.5 * Math.sin(phase))) * opacity);
                    drawStar(out, camera, point, (0.028 + 0.014 * pulse) * scale,
                            scaleAlpha(base, alpha / 255f), phase, viewRight, viewUp);
                }
            }
        }
        if (config.isOn("cape")) {
            for (int side : new int[]{-1, 1}) {
                Vec3d point = pos.add(back.multiply(0.28)).add(right.multiply(side * 0.22)).add(0, 1.24, 0);
                double phase = tick * 0.025 + side * 1.4;
                drawStar(out, camera, point, 0.045 * scale * pulse,
                        scaleAlpha(base, opacity * (0.55f + 0.40f * (float)(0.5 + 0.5 * Math.sin(phase)))),
                        phase, viewRight, viewUp);
            }
        }
        if (config.isOn("chinese_hat") || config.isOn("headwear")) {
            Vec3d crown = pos.add(0, 2.00, 0).add(back.multiply(-0.04));
            for (int i = 0; i < 3; i++) {
                double phase = tick * 0.025 + i * Math.PI * 2.0 / 3.0;
                Vec3d point = crown.add(right.multiply(Math.cos(phase) * 0.19))
                        .add(back.multiply(Math.sin(phase) * 0.12));
                drawDiamond(out, camera, point, 0.028 * scale, scaleAlpha(base, opacity * 0.78f),
                        phase, viewRight, viewUp);
            }
        }
        boolean mainHeld = !player.getMainHandStack().isEmpty();
        boolean offHeld = !player.getOffHandStack().isEmpty();
        for (int side : new int[]{-1, 1}) {
            if (!(side == 1 ? mainHeld : offHeld)) continue;
            Vec3d point = pos.add(right.multiply(side * 0.38)).add(back.multiply(0.10)).add(0, 0.88, 0);
            double phase = tick * 0.04 + side;
            drawStar(out, camera, point, 0.05 * scale * pulse,
                    scaleAlpha(base, opacity), phase, viewRight, viewUp);
            drawDiamond(out, camera, point.add(viewUp.multiply(0.075)), 0.022 * scale,
                    scaleAlpha(0xFFFFFFFF, opacity * 0.90f), -phase, viewRight, viewUp);
        }
    }

    /** A decorative butterfly companion; its wings flap continuously and it has no blade/weapon geometry. */
    private void renderButterflyCompanion(VertexConsumer out, Vec3d camera, PlayerEntity player, float partial,
                                          Quaternionf cameraRotation) {
        Vec3d pos = player.getLerpedPos(partial);
        float yaw = MathHelper.lerpAngleDegrees(partial, player.prevYaw, player.getYaw());
        double angle = Math.toRadians(yaw);
        Vec3d right = new Vec3d(Math.cos(angle), 0, Math.sin(angle));
        Vec3d back = new Vec3d(Math.sin(angle), 0, -Math.cos(angle));
        Vector3f rv = new Vector3f(1, 0, 0).rotate(cameraRotation);
        Vector3f uv = new Vector3f(0, 1, 0).rotate(cameraRotation);
        Vec3d viewRight = new Vec3d(rv.x, rv.y, rv.z).normalize();
        Vec3d viewUp = new Vec3d(uv.x, uv.y, uv.z).normalize();

        int style = config.style("butterfly_companion");
        int[] primary = {0xFFFFA84C, 0xFF4DA9FF, 0xFFFFA9D0, 0xFF9AE6E0, 0xFFE1D2FF};
        int[] secondary = {0xFF3C254B, 0xFF203D77, 0xFFE85F9D, 0xFFECFFFF, 0xFF8C7AC4};
        int index = Math.max(0, Math.min(primary.length - 1, style));
        float opacity = config.fxOpacity * config.moduleValue("butterfly_companion", "opacity", 0.96f, 0.10f, 1f);
        double scale = config.moduleValue("butterfly_companion", "scale", 1f, 0.35f, 2.5f);
        double phase = (tick + partial) * 0.20;
        Vec3d centre = pos.add(right.multiply(0.44 + Math.sin(phase * 0.43) * 0.10))
                .add(back.multiply(0.20)).add(0, 1.50 + Math.sin(phase * 1.25) * 0.13, 0);
        double size = 0.20 * scale;
        int main = scaleAlpha(primary[index], opacity);
        int trim = scaleAlpha(secondary[index], opacity);
        drawButterflyParticle(out, camera, centre, size, main, phase, viewRight, viewUp);
        drawButterflyParticle(out, camera, centre.add(right.multiply(0.10)).add(0, 0.17, 0),
                size * 0.38, trim, phase + 1.8, viewRight, viewUp);
        drawRing(out, camera, centre, size * 1.12,
                scaleAlpha(trim, opacity * 0.62f), phase * 0.25, viewRight, viewUp);
        drawStar(out, camera, centre.add(viewUp.multiply(size * 1.45)), size * 0.20,
                scaleAlpha(0xFFFFFFFF, opacity), phase, viewRight, viewUp);
    }

    /** The music player drives this translucent aura directly from its smoothed PCM level. */
    private void renderMusicAura(VertexConsumer out, Vec3d camera, PlayerEntity player, float partial) {
        float response = Math.max(0f, Math.min(1f, MusicEngine.audioLevel() * config.musicSensitivity));
        if (response < 0.025f) return;
        Vec3d pos = player.getLerpedPos(partial);
        float opacity = config.fxOpacity * config.moduleValue("music_aura_sync", "opacity", 0.95f, 0.10f, 1f);
        double scale = config.moduleValue("music_aura_sync", "scale", 1f, 0.35f, 3f);
        double radius = config.musicPulseRadius * scale * (0.72 + response * 0.78);
        double pulse = 0.95 + 0.05 * Math.sin((tick + partial) * 0.12);
        Theme audio = audioTheme();
        Vec3d right = new Vec3d(1, 0, 0);
        Vec3d forward = new Vec3d(0, 0, 1);
        int alpha = Math.round((65 + response * 175) * opacity);
        drawRing(out, camera, pos.add(0, 0.12, 0), radius * pulse,
                scaleAlpha(audio.primary(), alpha / 255f), tick * 0.018, right, forward);
        drawRing(out, camera, pos.add(0, 0.18, 0), radius * 0.72,
                scaleAlpha(audio.secondary(), alpha / 255f * 0.78f), -tick * 0.025, right, forward);
        drawRing(out, camera, pos.add(0, 0.24, 0), radius * 0.44,
                scaleAlpha(0xFFFFFFFF, alpha / 255f * 0.38f), tick * 0.031, right, forward);
        drawGlassOrb(out, camera, pos.add(0, 0.20, 0), 0.10 + response * 0.12,
                scaleAlpha(audio.secondary(), opacity * (0.30f + response * 0.45f)), right, new Vec3d(0, 1, 0));
    }

'''
engine = once(
    engine,
    "    private void renderGlowCosmetics(VertexConsumer out, Vec3d camera, PlayerEntity player,",
    glint_and_aura_methods + "    private void renderGlowCosmetics(VertexConsumer out, Vec3d camera, PlayerEntity player,",
    "Add glint, butterfly companion and music aura geometry")
write(engine_rel, engine)

# ---------------------------------------------------------------------------
# Module settings: provide useful controls for new geometry
settings_rel = "src/main/java/com/baroxvs/client/gui/ModuleSettingsScreen.java"
settings = read(settings_rel)
settings = once(
    settings,
    '''            case "aura", "orbit_stars", "halo", "crown_sparkles", "shoulder_wisp", "hand_glow",
                    "pet_sparkles", "defeat_dissolve", "footsteps", "jump_crystal",
                    "landing_burst", "sparkle_trail", "heart_trail", "bubble_trail", "trail_afterimage",
                    "butterfly_swarm", "wing_glints", "wing_runes" -> true;''',
    '''            case "aura", "orbit_stars", "halo", "shoulder_wisp", "hand_glow",
                    "pet_sparkles", "footsteps", "jump_crystal", "landing_burst", "sparkle_trail",
                    "heart_trail", "bubble_trail", "trail_afterimage", "butterfly_swarm",
                    "butterfly_companion", "wing_glints", "wing_runes", "glint", "music_aura_sync" -> true;''',
    "Add tuning support for new effects")
settings = once(
    settings,
    '''        } else if (id.equals("ambient_orbs") || id.equals("ambient_cubes")) {
            addSlider("moduleScale", "Object scale", 0.25f, 4f, 0.05f);
            addSlider("moduleOpacity", "Object opacity", 0.10f, 1f, 0.02f);
            addSlider("moduleFrequency", "Drift frequency", 0.25f, 3f, 0.05f);
        } else if (id.equals("ambient_bounce")) {''',
    '''        } else if (id.equals("ambient_forms")) {
            addSlider("moduleScale", "Glass object scale", 0.25f, 4f, 0.05f);
            addSlider("moduleOpacity", "Glass object opacity", 0.10f, 1f, 0.02f);
            addSlider("moduleFrequency", "Drift frequency", 0.25f, 3f, 0.05f);
            addSlider("ambient_count", "Objects around you", 4f, 80f, 1f);
            addSlider("ambient_range", "Distance", 2f, 28f, 0.5f);
        } else if (id.equals("glint") || id.equals("butterfly_companion")) {
            addSlider("moduleScale", "Cosmetic size", 0.25f, 3f, 0.05f);
            addSlider("moduleOpacity", "Cosmetic opacity", 0.10f, 1f, 0.02f);
        } else if (id.equals("music_aura_sync")) {
            addSlider("moduleScale", "Aura size", 0.35f, 3f, 0.05f);
            addSlider("moduleOpacity", "Aura opacity", 0.10f, 1f, 0.02f);
            addSlider("musicSensitivity", "Sound sensitivity", 0.40f, 3.50f, 0.05f);
            addSlider("musicPulseRadius", "Pulse radius", 0.50f, 4.00f, 0.05f);
        } else if (id.equals("ambient_bounce")) {''',
    "Add settings for consolidated modules")
settings = settings.replace('"crown_sparkles", ', '')
settings = settings.replace('"defeat_dissolve", ', '')
write(settings_rel, settings)

# ---------------------------------------------------------------------------
# Liquid Glass UI: specular sheen on every shared rounded panel/button surface
ui_rel = "src/main/java/com/baroxvs/client/gui/Ui.java"
ui = read(ui_rel)
a = ui.index("    public static void roundRect(")
b = ui.index("    public static void glassPanel(", a)
round_rect = '''    public static void roundRect(DrawContext c, int x1, int y1, int x2, int y2, int r, int color) {
        if (x2 <= x1 || y2 <= y1) return;
        int width = x2 - x1;
        int height = y2 - y1;
        int maxRadius = Math.min(width / 2, height / 2);
        r = Math.max(0, Math.min(maxRadius, r <= 0 ? 0 : Math.max(7, r)));
        if (r <= 0) {
            c.fill(x1, y1, x2, y2, color);
            return;
        }
        for (int y = y1; y < y2; y++) {
            double inset = 0.0;
            if (y < y1 + r) {
                double dy = r - (y - y1) - 0.5;
                inset = r - Math.sqrt(Math.max(0.0, r * r - dy * dy));
            } else if (y >= y2 - r) {
                double dy = r - (y2 - 1 - y) - 0.5;
                inset = r - Math.sqrt(Math.max(0.0, r * r - dy * dy));
            }
            double left = x1 + inset, right = x2 - inset;
            int coreLeft = (int)Math.ceil(left), coreRight = (int)Math.floor(right);
            if (coreRight > coreLeft) c.fill(coreLeft, y, coreRight, y + 1, color);
            int leftPixel = (int)Math.floor(left);
            float leftCoverage = (float)(coreLeft - left);
            if (leftCoverage > 0.001f && leftPixel >= x1 && leftPixel < x2)
                c.fill(leftPixel, y, leftPixel + 1, y + 1, fade(color, leftCoverage));
            int rightPixel = (int)Math.floor(right);
            float rightCoverage = (float)(right - rightPixel);
            if (rightCoverage > 0.001f && rightPixel >= x1 && rightPixel < x2)
                c.fill(rightPixel, y, rightPixel + 1, y + 1, fade(color, rightCoverage));
        }
        // Shared liquid-glass finish: only surfaces large enough to read as panels get reflections.
        int sourceAlpha = (color >>> 24) & 255;
        if (width >= 54 && height >= 22 && sourceAlpha >= 84) {
            int inset = Math.min(Math.max(6, r), Math.max(6, width / 3));
            int specular = Math.min(38, Math.round(sourceAlpha * 0.13f));
            int edge = Math.min(20, Math.round(sourceAlpha * 0.07f));
            if (x2 - inset > x1 + inset) {
                c.fill(x1 + inset, y1 + 1, x2 - inset, y1 + 2, (specular << 24) | 0x00FFFFFF);
                c.fill(x1 + inset + 5, y1 + 3, x2 - inset - 5, y1 + 4, (Math.max(0, specular / 2) << 24) | 0x00DDF5FF);
            }
            if (height > r * 2 + 8) {
                c.fill(x1 + 1, y1 + r, x1 + 2, y2 - r, (edge << 24) | 0x00C5E8FF);
                c.fill(x2 - 2, y1 + r, x2 - 1, y2 - r, (Math.max(0, edge / 2) << 24) | 0x00FFFFFF);
            }
        }
    }

'''
ui = ui[:a] + round_rect + ui[b:]
a = ui.index("    public static void glassPanel(")
b = ui.index("    public static void circle(", a)
glass_panel = '''    public static void glassPanel(DrawContext c, int x1, int y1, int x2, int y2, int radius, int base, int accent) {
        if (x2 <= x1 || y2 <= y1) return;
        int width = x2 - x1, height = y2 - y1;
        int safe = Math.min(Math.max(4, radius), Math.min(width / 2, height / 2));
        roundRect(c, x1 - 1, y1 + 4, x2 + 1, y2 + 5, safe + 2, 0x30000000);
        roundRect(c, x1, y1, x2, y2, safe, base);
        roundRect(c, x1 + 1, y1 + 1, x2 - 1, y2 - 1, Math.max(1, safe - 1),
                fade(lerp(base, 0xFFB9E6F4, 0.16f), 0.42f));
        roundRect(c, x1 + Math.max(6, safe), y1 + 2, x2 - Math.max(6, safe), y1 + 3,
                1, fade(accent, 0.82f));
        roundRect(c, x1 + Math.max(8, safe), y1 + 5, x2 - Math.max(8, safe), y1 + 6,
                1, 0x22FFFFFF);
        if (height > safe * 2 + 8) {
            c.fill(x1 + 2, y1 + safe, x1 + 3, y2 - safe, 0x20D7F5FF);
            c.fill(x2 - 3, y1 + safe, x2 - 2, y2 - safe, 0x14FFFFFF);
        }
    }

'''
ui = ui[:a] + glass_panel + ui[b:]
write(ui_rel, ui)

# ---------------------------------------------------------------------------
# Music page gets a live PCM signal meter and explains the synced aura.
gui_rel = "src/main/java/com/baroxvs/client/gui/BaroxMenuScreen.java"
gui = read(gui_rel)
gui = once(
    gui,
    '''        Ui.text(c, textRenderer, Ui.fit(textRenderer, MusicEngine.status(), w - 75, 0.76f), x + 43, statusY + 31, WHITE, 0.76f, false);

        int volY = statusY + 77;''',
    '''        Ui.text(c, textRenderer, Ui.fit(textRenderer, MusicEngine.status(), w - 75, 0.76f), x + 43, statusY + 31, WHITE, 0.76f, false);
        float signal = MusicEngine.audioLevel();
        int signalX = x + 16, signalY = statusY + 48, signalW = w - 32;
        c.fill(signalX, signalY, signalX + signalW, signalY + 3, 0x66384B5A);
        c.fill(signalX, signalY, signalX + Math.round(signalW * signal), signalY + 3,
                Ui.alpha(t.primary(), Math.round(90 + signal * 165)));
        Ui.textRight(c, textRenderer, "AURA SYNC " + Math.round(signal * 100) + "%", x + w - 16,
                statusY + 14, Ui.alpha(t.secondary(), 0xE0), 0.58f, true);

        int volY = statusY + 77;''',
    "Add live audio signal meter")
gui = gui.replace("Paste starts automatically. Direct MP3 or M3U/PLS only; no local MP4 is needed.",
                  "Direct MP3 or M3U/PLS stream. Enable Music Aura Sync in Effects for reactive glass rings.")
gui = gui.replace("BAROX VS   /   v018", "BAROX VS   /   v020")
write(gui_rel, gui)

# Update source documentation labels.
readme = root / "README.md"
if readme.exists():
    text = readme.read_text(encoding="utf-8")
    text = text.replace("BAROX VS v019", "BAROX VS v020").replace("BAROX-VS-v019", "BAROX-VS-v020")
    readme.write_text(text, encoding="utf-8")

# Fail early before Java compilation if any expected source area was missed.
assert all(x in catalog for x in ['"glint"', '"music_aura_sync"', '"ambient_forms"', '"butterfly_companion"'])
assert all(x not in catalog for x in ['"ambient_orbs"', '"ambient_cubes"', '"ambient_white"', '"hit_numbers"', '"defeat_dissolve"', '"crown_sparkles"'])
assert "emitJumpBurst" in engine and "renderMusicAura" in engine and "renderGlints" in engine
assert "renderButterflyCompanion" in engine and "drawGlassOrb(out, camera, spark.position" in engine
assert "Pearl Horizon" in cosmetic_catalog and sky.count("0xFF") > 130
assert "migrateV020Modules" in cfg and "cosmeticVersion" in cfg
assert "ambient_forms" in settings and "moduleScale" in settings
assert "Shared liquid-glass finish" in ui and "AURA SYNC" in gui
print("Applied v020: 44 sky presets, liquid-glass UI, glints, music-reactive aura, six jump shapes, animated butterfly companion and ambient-module consolidation.")
