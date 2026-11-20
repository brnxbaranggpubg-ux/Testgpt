#!/usr/bin/env python3
import re
import sys
from pathlib import Path
root = Path(sys.argv[1])
base = root / "src/main/java/com/baroxvs/client"
engine = (base / "cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
config = (base / "config/BaroxConfig.java").read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(ids) == len(set(ids)) == 99, f"module IDs changed: {len(ids)} / {len(set(ids))} unique"
for module_id in ("jump_circle", "cape"):
    assert ids.count(module_id) == 1, f"missing/duplicate module ID {module_id}"
    assert f'"{module_id}"' in config, f"saved config key {module_id} missing"

# Every take-off is its own ring record, rendered until its own configured duration expires.
for token in (
    "private static final int JUMP_PULSE_CAPACITY = 24;",
    "private record JumpPulse(long startTick, Vec3d origin, ClientWorld world)",
    "private final List<JumpPulse> jumpPulses = new ArrayList<>(JUMP_PULSE_CAPACITY);",
    "jumpPulses.removeIf(pulse -> pulse.world() != client.world",
    "tick - pulse.startTick() >= jumpDuration",
    "jumpPulses.add(new JumpPulse(tick, player.getPos(), client.world));",
    "renderJumpPulseInstance(out, camera, pulse.origin(), progress);",
    "if (progress >= 1.0) continue;",
    "Vec3d centre = pulseOrigin.add(0, 0.014, 0)",
):
    assert token in engine, f"jump ring lifetime/history invariant missing: {token}"
assert "jumpPulseTick" not in engine and "jumpPulseOrigin" not in engine and "jumpPulseWorld" not in engine
assert 'if (!config.isOn("jump_circle")) {\n            jumpPulses.clear();' in engine

# The cape body is submitted using a dedicated fresh layer, not the shared cosmetic consumer.
for token in (
    'CAPE_BODY_TEXTURE = Identifier.of("baroxvs", "textures/misc/cape_body.png")',
    'context.consumers().getBuffer(\n                        RenderLayer.getEntityTranslucent(CAPE_BODY_TEXTURE))',
    'renderCape(capeOutput, context.consumers(), camera, player, partial)',
    'catch (IllegalStateException bufferState)',
    'LOGGER.warn("Cape frame skipped',
    'VertexConsumer logoOut = consumers.getBuffer(RenderLayer.getEntityTranslucent(CAPE_LOGO_TEXTURE));',
):
    assert token in engine, f"cape buffer safety invariant missing: {token}"
assert 'renderCape(output, context.consumers()' not in engine
texture = root / "src/main/resources/assets/baroxvs/textures/misc/cape_body.png"
white = root / "src/main/resources/assets/baroxvs/textures/misc/white.png"
assert texture.is_file() and texture.stat().st_size > 0, "dedicated cape material texture missing"
assert texture.read_bytes() == white.read_bytes(), "cape body material must match the opaque white material texel"
assert "BAROX-VS-v101.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=1.01.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v101"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v101"
assert (root / "RENDER_REPAIR_v101.md").is_file()
print("v101 checks passed: independent duration-based Jump Ring history, isolated cape buffer with crash guard, 99 unique module IDs")