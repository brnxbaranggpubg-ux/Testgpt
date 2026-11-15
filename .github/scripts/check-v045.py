#!/usr/bin/env python3
import sys
from pathlib import Path

root = Path(sys.argv[1])
read = lambda p: (root / p).read_text(encoding="utf-8")
engine = read("src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java")
render = engine.split("private void renderWorldEffects(", 1)[1].split("private void renderAura(", 1)[0]

rain = render.find("renderLiquidGlassRain(rainOutput")
glass = render.find("renderSelfGlass(glassOutput")
base = render.find("VertexConsumer output = context.consumers().getBuffer(RenderLayer.getEntityTranslucent(COSMETIC_TEXTURE))")
aura = render.find("renderAura(output")
assert -1 not in (rain, glass, base, aura), "missing render pass"
assert rain < glass < base < aura, "glass texture passes must finish before base buffer acquisition"
assert render.count("getBuffer(") == 3, "expected rain, self-glass and base layer acquisitions"
base_end = render.find("\n", base)
assert "getBuffer(" not in render[base_end + 1:], "RenderLayer switch after base consumer acquisition"
assert "renderGlowCosmetics(output, camera, player, partial, cameraRotation)" in render
assert "renderGlowCosmetics(output, glassOutput" not in render

start = engine.index("private void renderSelfGlass(")
end = engine.index("private void renderGlowCosmetics(", start)
assert "renderLiquidGlassAvatar(out" in engine[start:end]
assert "glassOut" not in engine[end:engine.index("private void renderLiquidGlassAvatar(", end)]
glow = engine[end:engine.index("private void renderLiquidGlassAvatar(", end)]
assert "renderLiquidGlassAvatar(" not in glow

assert "archiveFileName = 'BAROX-VS-v045.jar'" in read("build.gradle")
assert "mod_version=0.45.0" in read("gradle.properties")
assert read("VERSION").strip() == "BAROX VS v045"
assert read("BUILD_VERSION.txt").strip() == "BAROX VS v045"
assert read("README.md").startswith("# BAROX VS — v045")
assert "## v045 — Render Buffer Lifecycle Crash Fix" in read("README.md")
assert engine.count("{") == engine.count("}"), "unbalanced Java braces"
assert engine.count("(") == engine.count(")"), "unbalanced Java parentheses"
print("v045 checks passed: texture passes precede base buffer acquisition; no stale cross-layer VertexConsumer; release stamps valid.")
