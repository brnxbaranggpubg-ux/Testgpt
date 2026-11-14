#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")

def read(rel):
    path = root / rel
    if not path.is_file():
        raise SystemExit(f"Missing v025 source file: {rel}")
    return path.read_text(encoding="utf-8")

def write(rel, value):
    path = root / rel
    path.write_text(value, encoding="utf-8")

def once(src, old, new, label):
    count = src.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return src.replace(old, new, 1)

# Preserve the existing four preset indices and append two new motion styles.
catalog_rel = "src/main/java/com/baroxvs/client/cosmetic/CosmeticCatalog.java"
catalog = read(catalog_rel)
catalog = once(
    catalog,
    'public static final String[] WING_MOTIONS = {"Gentle", "Flap", "Pulse", "Still"};',
    'public static final String[] WING_MOTIONS = {"Gentle", "Flap", "Pulse", "Still", "Flight", "Flow"};',
    "Expand wing motion presets"
)
write(catalog_rel, catalog)

engine_rel = "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java"
engine = read(engine_rel)

engine = once(
    engine,
    '    private double currentWingScale = 1.0;\n    private double currentWingFlapAngle;\n',
    '''    private double previousWingScale = 1.0;
    private double currentWingScale = 1.0;
    private double renderWingScale = 1.0;
    private double previousWingFlapAngle;
    private double currentWingFlapAngle;
    private double renderWingFlapAngle;
    private double wingFlapVelocity;
    private double wingPhase;
    private double wingActivity;
    private double previousWingFlex;
    private double currentWingFlex;
    private double renderWingFlex;
    private double renderAnimationTime;
    private double capeMoveState;
    private double capeTurnState;
    private double capeVerticalState;
    private double capeGlideState;
''',
    "Add interpolated animation state"
)

engine = once(
    engine,
    '            previousAttackDown = false;\n            lastVelocityY = 0;\n            return;',
    '''            previousAttackDown = false;
            lastVelocityY = 0;
            previousWingFlapAngle = currentWingFlapAngle = renderWingFlapAngle = 0.0;
            wingFlapVelocity = wingActivity = 0.0;
            previousWingFlex = currentWingFlex = renderWingFlex = 0.0;
            previousWingScale = currentWingScale = renderWingScale = 1.0;
            capeMoveState = capeTurnState = capeVerticalState = capeGlideState = 0.0;
            return;''',
    "Reset animation state when no player is active"
)

engine = once(
    engine,
    '        currentWingScale = wingScaleForConfig();\n        currentWingFlapAngle = wingFlapForTick();\n        updateAmbientBodies(client, player);',
    '        updateAnimationState(player);\n        updateAmbientBodies(client, player);',
    "Use stateful animation update"
)

old_wing_method = '''    private double wingFlapForTick() {
        return switch (config.style("wing_motion")) {
            case 0 -> Math.sin(tick * 0.045) * 0.085;
            case 1 -> Math.sin(tick * 0.18) * 0.255;
            case 2 -> Math.sin(tick * 0.10) * 0.175;
            default -> 0.0;
        };
    }
'''
new_wing_method = '''    /**
     * Advances the cosmetic pose on the fixed client tick. A damped spring follows
     * a movement-aware target; the renderer interpolates the previous/current poses.
     */
    private void updateAnimationState(PlayerEntity player) {
        previousWingScale = currentWingScale;
        previousWingFlapAngle = currentWingFlapAngle;
        previousWingFlex = currentWingFlex;

        Vec3d velocity = player.getVelocity();
        double horizontalSpeed = Math.sqrt(velocity.x * velocity.x + velocity.z * velocity.z);
        double airborne = player.isOnGround() ? 0.0 : 1.0;
        double glide = player.checkGliding() ? 1.0 : 0.0;
        double vertical = clamp01(Math.abs(velocity.y) * 1.7);
        double targetActivity = clamp01(horizontalSpeed * 2.7
                + (player.isSprinting() ? 0.18 : 0.0) + airborne * 0.16 + glide * 0.60);
        wingActivity += (targetActivity - wingActivity) * (targetActivity > wingActivity ? 0.22 : 0.11);

        double targetScale = wingScaleForConfig();
        currentWingScale += (targetScale - currentWingScale) * 0.24;

        int motionStyle = config.style("wing_motion");
        double phaseRate = switch (motionStyle) {
            case 0 -> 0.070;
            case 1 -> 0.172;
            case 2 -> 0.108;
            case 3 -> 0.0;
            case 4 -> 0.078;
            default -> 0.060;
        };
        wingPhase += phaseRate * (1.0 + wingActivity * 0.48 + airborne * 0.18 + glide * 0.48);

        double targetFlap = switch (motionStyle) {
            case 0 -> Math.sin(wingPhase) * (0.078 + wingActivity * 0.075 + vertical * 0.018);
            case 1 -> (Math.sin(wingPhase) + 0.20 * Math.sin(wingPhase * 2.0 + 0.72))
                    * (0.155 + wingActivity * 0.085 + glide * 0.025);
            case 2 -> (Math.sin(wingPhase) * 0.68 + Math.sin(wingPhase * 0.52 + 0.8) * 0.32)
                    * (0.145 + wingActivity * 0.055);
            case 3 -> 0.0;
            case 4 -> Math.sin(wingPhase) * (0.060 + wingActivity * 0.15 + glide * 0.10 + vertical * 0.025);
            default -> (Math.sin(wingPhase * 0.72) + 0.24 * Math.sin(wingPhase * 1.44 + 0.9))
                    * (0.070 + wingActivity * 0.045);
        };
        targetFlap = Math.max(-0.38, Math.min(0.38, targetFlap));
        double acceleration = (targetFlap - currentWingFlapAngle) * 0.27 - wingFlapVelocity * 0.62;
        wingFlapVelocity += acceleration;
        currentWingFlapAngle = Math.max(-0.40, Math.min(0.40, currentWingFlapAngle + wingFlapVelocity));
        currentWingFlex = Math.sin(wingPhase * 0.47 + wingActivity * 0.4)
                * (0.018 + wingActivity * 0.027 + glide * 0.016);

        double targetMove = clamp01(horizontalSpeed * 3.6);
        capeMoveState += (targetMove - capeMoveState) * (targetMove > capeMoveState ? 0.19 : 0.105);
        double targetTurn = Math.max(-1.0, Math.min(1.0,
                MathHelper.wrapDegrees(player.getYaw() - player.prevYaw) / 34.0));
        capeTurnState += (targetTurn - capeTurnState) * 0.20;
        double targetVertical = clamp01(Math.abs(velocity.y) * 1.8);
        capeVerticalState += (targetVertical - capeVerticalState) * 0.17;
        capeGlideState += (glide - capeGlideState) * 0.14;
    }

    private static double clamp01(double value) {
        return Math.max(0.0, Math.min(1.0, value));
    }
'''
engine = once(engine, old_wing_method, new_wing_method, "Replace fixed sine wing motion with spring-driven state")

engine = once(
    engine,
    '        float partial = context.tickCounter().getTickDelta(false);\n        Quaternionf cameraRotation = context.camera().getRotation();',
    '''        float partial = context.tickCounter().getTickDelta(false);
        renderAnimationTime = tick + partial;
        renderWingScale = previousWingScale + (currentWingScale - previousWingScale) * partial;
        renderWingFlapAngle = previousWingFlapAngle
                + (currentWingFlapAngle - previousWingFlapAngle) * partial;
        renderWingFlex = previousWingFlex + (currentWingFlex - previousWingFlex) * partial;
        Quaternionf cameraRotation = context.camera().getRotation();''',
    "Interpolate animation pose before drawing"
)

anchor = '    private void renderWings(VertexConsumer out, Vec3d camera, PlayerEntity p, float partial) {'
if engine.count(anchor) != 1:
    raise SystemExit("Could not locate the wing geometry section")
head, tail = engine.split(anchor, 1)
tail = tail.replace("currentWingScale", "renderWingScale")
tail = tail.replace("currentWingFlapAngle", "renderWingFlapAngle")
tail = re.sub(r"\btick\b(?!\s*\+\s*partial)", "renderAnimationTime", tail)
tail = tail.replace('        renderWingScale = wingScaleForConfig();\n', '')
tail = tail.replace('        double motion = renderWingFlapAngle * 0.62;', '        double motion = renderWingFlapAngle * 0.88;')
engine = head + anchor + tail

# Smooth older render passes too, retaining explicit (tick + partial) expressions.
for start, end in [
    ("    private void renderGlints(", "    /** A decorative butterfly companion"),
    ("    private void renderMusicAura(", "    /**\n     * v022 additions"),
    ("    private void renderGlowCosmetics(", "    private void renderChunkRain("),
]:
    a = engine.index(start)
    b = engine.index(end, a)
    section = engine[a:b]
    section = re.sub(r"\btick\b(?!\s*\+\s*partial)", "renderAnimationTime", section)
    engine = engine[:a] + section + engine[b:]

engine = once(
    engine,
    '''        double angle = flap;
        double c = Math.cos(angle), sn = Math.sin(angle);
        double px = x * renderWingScale;
        double py = y * renderWingScale;''',
    '''        double px = x * renderWingScale;
        double py = y * renderWingScale;
        double span = Math.min(1.8, Math.max(0.0, px));
        double angle = flap + renderWingFlex * span * span * 0.34;
        double c = Math.cos(angle), sn = Math.sin(angle);''',
    "Add feather tip follow-through"
)

engine = once(
    engine,
    '''        double phase = (tick + partial) * 0.20;
        Vec3d centre = pos.add(right.multiply(0.44 + Math.sin(phase * 0.43) * 0.10))
                .add(back.multiply(0.20)).add(0, 1.50 + Math.sin(phase * 1.25) * 0.13, 0);''',
    '''        double activity = capeMoveState;
        double phase = renderAnimationTime * (0.215 + activity * 0.055);
        Vec3d centre = pos.add(right.multiply(0.43 + Math.sin(phase * 0.43) * (0.09 + activity * 0.025)))
                .add(back.multiply(0.20 + Math.sin(phase * 0.31) * 0.035))
                .add(0, 1.49 + Math.sin(phase * 1.18) * 0.11 + capeGlideState * 0.08, 0);''',
    "Improve butterfly companion flight path"
)

silk_old = '''    /** Two translucent silk trails orbit the torso with a slow, asymmetric wave. */
    private void renderSilkRibbons(VertexConsumer out, Vec3d camera, PlayerEntity player, float partial) {
        Vec3d pos = player.getLerpedPos(partial);
        double yaw = Math.toRadians(MathHelper.lerpAngleDegrees(partial, player.prevYaw, player.getYaw()));
        Vec3d right = new Vec3d(Math.cos(yaw), 0, Math.sin(yaw));
        Vec3d back = new Vec3d(Math.sin(yaw), 0, -Math.cos(yaw));
        double scale = config.moduleValue("silk_ribbons", "scale", 1f, 0.25f, 4f);
        float opacity = config.moduleValue("silk_ribbons", "opacity", 1f, 0.10f, 1f);
        Theme theme = Themes.current(config);
        for (int strand = 0; strand < 2; strand++) {
            Vec3d previous = null;
            int color = scaleAlpha(withAlpha(strand == 0 ? theme.primary() : theme.secondary(), 0xB8), opacity);
            for (int i = 0; i <= 28; i++) {
                double t = i / 28.0;
                double a = renderAnimationTime * (strand == 0 ? 0.018 : -0.014) + t * Math.PI * 2.25 + strand * Math.PI;
                double radius = (0.36 + Math.sin(t * Math.PI) * 0.22) * scale;
                double height = (0.62 + t * 1.22 + Math.sin(a * 1.3) * 0.075) * scale;
                Vec3d point = pos.add(right.multiply(Math.cos(a) * radius))
                        .add(back.multiply(Math.sin(a) * radius + 0.24 * scale)).add(0, height, 0);
                if (previous != null) {
                    double width = (0.026 - t * 0.008) * scale;
                    ribbon(out, camera, previous, point, right, width, color);
                }
                if (i % 7 == 0) drawDiamond(out, camera, point, 0.026 * scale, withAlpha(theme.secondary(), 0xCE), a);
                previous = point;
            }
        }
    }
'''
silk_new = '''    /** Two tapered silk ribbons with delayed waves, flutter and velocity-aware trailing. */
    private void renderSilkRibbons(VertexConsumer out, Vec3d camera, PlayerEntity player, float partial) {
        Vec3d pos = player.getLerpedPos(partial);
        double yaw = Math.toRadians(MathHelper.lerpAngleDegrees(partial, player.prevYaw, player.getYaw()));
        Vec3d right = new Vec3d(Math.cos(yaw), 0, Math.sin(yaw));
        Vec3d back = new Vec3d(Math.sin(yaw), 0, -Math.cos(yaw));
        double scale = config.moduleValue("silk_ribbons", "scale", 1f, 0.25f, 4f);
        float opacity = config.moduleValue("silk_ribbons", "opacity", 1f, 0.10f, 1f);
        Theme theme = Themes.current(config);
        double movement = capeMoveState;
        double turn = capeTurnState;
        for (int strand = 0; strand < 2; strand++) {
            Vec3d previous = null;
            int color = scaleAlpha(withAlpha(strand == 0 ? theme.primary() : theme.secondary(), 0xB8), opacity);
            for (int i = 0; i <= 34; i++) {
                double t = i / 34.0;
                double delayed = t * 2.0 * Math.PI * 2.15;
                double phase = renderAnimationTime * (strand == 0 ? 0.020 : -0.016)
                        - delayed + strand * Math.PI;
                double travelling = Math.sin(phase) * (0.035 + movement * 0.055) * (0.25 + t);
                double secondaryWave = Math.sin(phase * 0.58 + strand * 1.3) * 0.035 * t;
                double a = renderAnimationTime * (strand == 0 ? 0.016 : -0.013)
                        + t * Math.PI * 2.15 + strand * Math.PI;
                double radius = (0.31 + Math.sin(t * Math.PI) * 0.19 + movement * 0.045) * scale;
                double height = (0.60 + t * 1.25 + Math.sin(phase * 0.72) * 0.055
                        + secondaryWave + capeGlideState * t * 0.10) * scale;
                Vec3d point = pos.add(right.multiply(Math.cos(a) * radius + travelling + turn * t * 0.07))
                        .add(back.multiply(Math.sin(a) * radius + 0.23 * scale + secondaryWave))
                        .add(0, height, 0);
                if (previous != null) {
                    double taper = 1.0 - t * 0.68;
                    double flutterWidth = 0.92 + 0.12 * Math.sin(phase * 0.8);
                    ribbon(out, camera, previous, point, right, 0.025 * scale * taper * flutterWidth, color);
                }
                if (i % 8 == 0) {
                    drawDiamond(out, camera, point, 0.022 * scale,
                            withAlpha(theme.secondary(), (int) Math.round(0xCE * (1.0 - t * 0.25))), phase);
                }
                previous = point;
            }
        }
    }
'''
engine = once(engine, silk_old, silk_new, "Upgrade silk ribbon motion")

engine = once(
    engine,
    '''        double movement = Math.min(1.0, Math.sqrt(velocity.x * velocity.x + velocity.z * velocity.z) * 3.6);
        double turn = Math.max(-1.0, Math.min(1.0,
                MathHelper.wrapDegrees(player.getYaw() - player.prevYaw) / 34.0));
        double verticalMotion = Math.max(0.0, Math.min(1.0, Math.abs(velocity.y) * 1.8));
        double glide = player.checkGliding() ? 1.0 : 0.0;''',
    '''        double movement = capeMoveState;
        double turn = capeTurnState;
        double verticalMotion = capeVerticalState;
        double glide = capeGlideState;''',
    "Smooth cape response inputs"
)
engine = once(
    engine,
    '        double flutter = 0.065 + movement * 0.24 + Math.abs(turn) * 0.095 + verticalMotion * 0.045 + glide * 0.17;\n',
    '        double flutter = 0.055 + movement * 0.235 + Math.abs(turn) * 0.085 + verticalMotion * 0.040 + glide * 0.16;\n',
    "Retune cape flutter amplitude"
)

particle_old = '''    private static void drawButterflyParticle(VertexConsumer out, Vec3d camera, Vec3d centre, double size,
                                              int color, double phase, Vec3d right, Vec3d up) {
        double flap = 0.26 + 0.72 * Math.abs(Math.sin(phase));
        Vec3d bodyTop = centre.add(up.multiply(size * 0.72));
        Vec3d bodyBottom = centre.subtract(up.multiply(size * 0.72));
        Vec3d leftRoot = centre.subtract(right.multiply(size * 0.10));
        Vec3d rightRoot = centre.add(right.multiply(size * 0.10));
        Vec3d leftOuter = centre.subtract(right.multiply(size * 1.18)).add(up.multiply(size * flap));
        Vec3d leftTrailing = centre.subtract(right.multiply(size * 0.92)).subtract(up.multiply(size * flap * 0.64));
        Vec3d rightOuter = centre.add(right.multiply(size * 1.18)).add(up.multiply(size * flap));
        Vec3d rightTrailing = centre.add(right.multiply(size * 0.92)).subtract(up.multiply(size * flap * 0.64));
        emitQuad(out, camera, bodyTop, leftRoot, leftOuter, leftTrailing, withAlpha(color, 0xC8));
        emitQuad(out, camera, bodyTop, rightOuter, rightRoot, rightTrailing, withAlpha(color, 0xC8));
        drawBillboard(out, camera, centre, size * 0.15, size * 1.42, 0xEFFFFFFF, 0, right, up);
        drawDiamond(out, camera, bodyTop.add(right.multiply(-size * 0.12)), size * 0.20,
                withAlpha(color, 0xE8), phase * 0.2);
    }
'''
particle_new = '''    private static void drawButterflyParticle(VertexConsumer out, Vec3d camera, Vec3d centre, double size,
                                              int color, double phase, Vec3d right, Vec3d up) {
        double leftOpen = 0.14 + 0.86 * (0.5 - 0.5 * Math.cos(phase));
        double rightOpen = 0.14 + 0.86 * (0.5 - 0.5 * Math.cos(phase + 0.17));
        Vec3d bodyTop = centre.add(up.multiply(size * 0.72));
        Vec3d leftRoot = centre.subtract(right.multiply(size * 0.10));
        Vec3d rightRoot = centre.add(right.multiply(size * 0.10));
        Vec3d leftOuter = centre.subtract(right.multiply(size * (0.36 + 0.82 * leftOpen)))
                .add(up.multiply(size * (0.10 + 0.48 * leftOpen)));
        Vec3d leftTrailing = centre.subtract(right.multiply(size * (0.28 + 0.64 * leftOpen)))
                .subtract(up.multiply(size * (0.16 + 0.42 * leftOpen)));
        Vec3d rightOuter = centre.add(right.multiply(size * (0.36 + 0.82 * rightOpen)))
                .add(up.multiply(size * (0.10 + 0.48 * rightOpen)));
        Vec3d rightTrailing = centre.add(right.multiply(size * (0.28 + 0.64 * rightOpen)))
                .subtract(up.multiply(size * (0.16 + 0.42 * rightOpen)));
        int membrane = withAlpha(color, 0xC8);
        emitQuad(out, camera, bodyTop, leftRoot, leftOuter, leftTrailing, membrane);
        emitQuad(out, camera, bodyTop, rightOuter, rightRoot, rightTrailing, membrane);
        drawDiamond(out, camera, centre.subtract(right.multiply(size * 0.68)).add(up.multiply(size * 0.08)),
                size * 0.105, withAlpha(0xFFFFFFFF, 0xB8), phase * 0.14, right, up);
        drawDiamond(out, camera, centre.add(right.multiply(size * 0.68)).add(up.multiply(size * 0.08)),
                size * 0.105, withAlpha(0xFFFFFFFF, 0xB8), -phase * 0.14, right, up);
        drawBillboard(out, camera, centre, size * 0.15, size * 1.42, 0xEFFFFFFF, 0, right, up);
        drawDiamond(out, camera, bodyTop.add(right.multiply(-size * 0.12)), size * 0.20,
                withAlpha(color, 0xE8), phase * 0.2, right, up);
    }
'''
engine = once(engine, particle_old, particle_new, "Upgrade butterfly wing stroke geometry")
write(engine_rel, engine)

gui_rel = "src/main/java/com/baroxvs/client/gui/ModuleClickGuiScreen.java"
gui = read(gui_rel)
gui = once(gui, '    private float openProgress;\n', '    private float openProgress;\n    private float easedOpenProgress;\n', "Add eased GUI progress")
gui = once(gui, '        openProgress = Math.min(1f, openProgress + step * 0.13f);\n        animationTime += step;',
                '        openProgress = Math.min(1f, openProgress + step * 0.16f);\n        float inverse = 1f - openProgress;\n        easedOpenProgress = 1f - inverse * inverse * inverse;\n        animationTime += step;',
                "Ease ClickGUI opening")
gui = gui.replace('(1f - openProgress)', '(1f - easedOpenProgress)')
gui = gui.replace('Math.round(listW * openProgress)', 'Math.round(listW * easedOpenProgress)')
write(gui_rel, gui)

print("Applied v025: spring-driven movement-aware wing poses, fractional-tick interpolation, flexing feather tips, smoother cape and silk cloth, folding butterfly wings, and eased ClickGUI entrance.")
