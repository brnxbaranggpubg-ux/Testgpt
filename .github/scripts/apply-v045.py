#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1])
path = root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java"
engine = path.read_text(encoding="utf-8")

def rep(old, new, label):
    global engine
    n = engine.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected one match, found {n}")
    engine = engine.replace(old, new, 1)

# Immediate providers flush the active BufferBuilder when changing RenderLayer.
# Never retain a consumer across a texture switch.
rep(
"""        VertexConsumer output = context.consumers().getBuffer(RenderLayer.getEntityTranslucent(COSMETIC_TEXTURE));
        PlayerEntity player = client.player;
""",
"""        PlayerEntity player = client.player;
""",
"defer base buffer acquisition")

rep(
"""        if (config.isOn("liquid_rain")) {
            // Reuse the avatar's dedicated Liquid Glass material so rain droplets share the same
            // translucent texture, moving optical sheen and Fresnel response as the body shell.
            VertexConsumer rainOutput = context.consumers().getBuffer(
                    RenderLayer.getEntityTranslucent(LIQUID_GLASS_TEXTURE));
            withModuleStrength("liquid_rain",
                    () -> renderLiquidGlassRain(rainOutput, camera, player, partial, client));
        }
        if (config.isOn("aura")) withModuleStrength("aura", () -> renderAura(output, camera, player, partial));
""",
"""        if (config.isOn("liquid_rain")) {
            // Finish the separate Liquid Glass pass before acquiring the base cosmetic layer.
            VertexConsumer rainOutput = context.consumers().getBuffer(
                    RenderLayer.getEntityTranslucent(LIQUID_GLASS_TEXTURE));
            withModuleStrength("liquid_rain",
                    () -> renderLiquidGlassRain(rainOutput, camera, player, partial, client));
        }
        if (config.isOn("player_glass") && config.isOn("self_glass")) {
            // Complete avatar glass geometry before switching back to the base cosmetic layer.
            VertexConsumer glassOutput = context.consumers().getBuffer(
                    RenderLayer.getEntityTranslucent(LIQUID_GLASS_TEXTURE));
            withModuleStrength("player_glass",
                    () -> renderSelfGlass(glassOutput, camera, player, partial));
        }
        // Acquire the base layer last and keep this consumer on that layer until the pass ends.
        VertexConsumer output = context.consumers().getBuffer(RenderLayer.getEntityTranslucent(COSMETIC_TEXTURE));
        if (config.isOn("aura")) withModuleStrength("aura", () -> renderAura(output, camera, player, partial));
""",
"order texture passes")

rep(
"""        if (config.isOn("player_glass") && (config.isOn("self_glass") || config.isOn("arm_glow")
                || config.isOn("hand_glow") || config.isOn("held_item_glow"))) {
            VertexConsumer glassOutput = config.isOn("self_glass")
                    ? context.consumers().getBuffer(RenderLayer.getEntityTranslucent(LIQUID_GLASS_TEXTURE))
                    : output;
            withModuleStrength("player_glass", () -> renderGlowCosmetics(output, glassOutput, camera, player, partial, cameraRotation));
        }
""",
"""        if (config.isOn("player_glass") && (config.isOn("arm_glow")
                || config.isOn("hand_glow") || config.isOn("held_item_glow"))) {
            withModuleStrength("player_glass",
                    () -> renderGlowCosmetics(output, camera, player, partial, cameraRotation));
        }
""",
"separate glass and glow passes")

rep(
"""    private void renderGlowCosmetics(VertexConsumer out, VertexConsumer glassOut, Vec3d camera, PlayerEntity player,
                                     float partial, Quaternionf cameraRotation) {
""",
"""    private void renderGlowCosmetics(VertexConsumer out, Vec3d camera, PlayerEntity player,
                                     float partial, Quaternionf cameraRotation) {
""",
"update glow renderer signature")

rep(
"""        if (config.isOn("self_glass")) {
            renderLiquidGlassAvatar(glassOut, camera, player, pos, right, forward, up, partial, pulse);
        }

""",
"",
"remove cross-layer avatar render")

selfGlass = """    /**
     * Renders the avatar glass material in its own texture pass. Consumers returned by an
     * Immediate provider are only valid while their RenderLayer remains active.
     */
    private void renderSelfGlass(VertexConsumer out, Vec3d camera, PlayerEntity player, float partial) {
        Vec3d pos = player.getLerpedPos(partial);
        float yaw = MathHelper.lerpAngleDegrees(partial, player.prevYaw, player.getYaw());
        double angle = Math.toRadians(yaw);
        Vec3d right = new Vec3d(Math.cos(angle), 0, Math.sin(angle));
        Vec3d forward = new Vec3d(-Math.sin(angle), 0, Math.cos(angle));
        Vec3d up = new Vec3d(0, 1, 0);
        double pulse = 0.94 + 0.06 * Math.sin((tick + partial) * 0.075);
        renderLiquidGlassAvatar(out, camera, player, pos, right, forward, up, partial, pulse);
    }

"""
rep(
"    private void renderGlowCosmetics(VertexConsumer out, Vec3d camera, PlayerEntity player,\n",
selfGlass + "    private void renderGlowCosmetics(VertexConsumer out, Vec3d camera, PlayerEntity player,\n",
"insert isolated self-glass renderer")

path.write_text(engine, encoding="utf-8")

build = root / "build.gradle"
s = build.read_text(encoding="utf-8")
if s.count("archiveFileName = 'BAROX-VS-v044.jar'") != 1:
    raise SystemExit("build.gradle release stamp mismatch")
build.write_text(s.replace("archiveFileName = 'BAROX-VS-v044.jar'", "archiveFileName = 'BAROX-VS-v045.jar'", 1), encoding="utf-8")

props = root / "gradle.properties"
s = props.read_text(encoding="utf-8")
if s.count("mod_version=0.44.0") != 1:
    raise SystemExit("gradle.properties version mismatch")
props.write_text(s.replace("mod_version=0.44.0", "mod_version=0.45.0", 1), encoding="utf-8")

for name in ("VERSION", "BUILD_VERSION.txt"):
    p = root / name
    s = p.read_text(encoding="utf-8")
    if s.strip() != "BAROX VS v044":
        raise SystemExit(f"{name} version mismatch")
    p.write_text("BAROX VS v045\n", encoding="utf-8")

readme = root / "README.md"
s = readme.read_text(encoding="utf-8")
if not s.startswith("# BAROX VS — v044\n"):
    raise SystemExit("README version mismatch")
s = s.replace("# BAROX VS — v044", "# BAROX VS — v045", 1)
section = """## v045 — Render Buffer Lifecycle Crash Fix

- Fixes the v044 mobile-log crash: IllegalStateException: Not building! in CosmeticEngine.drawSoftDisc during Aura rendering.
- The Immediate vertex provider flushes its active BufferBuilder when switching to a different RenderLayer. BAROX previously retained the base cosmetic VertexConsumer, switched to the Liquid Glass texture for rain, then reused the flushed consumer in Aura.
- Liquid Glass Rain and Self Glass now complete in dedicated texture passes first. The base cosmetic consumer is acquired only after those passes and stays on its RenderLayer for the remainder of the world-effects pass.
- Separates avatar glass rendering from arm/hand glow rendering. Existing module IDs, saved settings and visual effects are preserved.

"""
if s.count("## v044 — iPhone-style Liquid Glass Rain\n") != 1:
    raise SystemExit("README v044 section missing or duplicated")
s = s.replace("## v044 — iPhone-style Liquid Glass Rain\n", section + "## v044 — iPhone-style Liquid Glass Rain\n", 1)
readme.write_text(s, encoding="utf-8")

print("Applied v045 RenderLayer/VertexConsumer lifecycle fix.")
