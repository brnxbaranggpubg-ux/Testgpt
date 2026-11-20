from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
engine = (root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
modules = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
build = (root / "build.gradle").read_text(encoding="utf-8")
props = (root / "gradle.properties").read_text(encoding="utf-8")

assert "double featherLag = Math.sin(wingPhase * 0.66" in engine
assert "double hingeWave = Math.sin(wingPhase * 0.34" in engine
assert "private void updateCompanionMotion(MinecraftClient client, PlayerEntity player)" in engine
assert "companionMotionVelocity = companionMotionVelocity.multiply(0.66).add(error.multiply(0.18))" in engine
assert "previousCompanionCentre.lerp(currentCompanionCentre, partial)" in engine
silk = engine[engine.index("private void renderSilkRibbons("):engine.index("private static final int[][] CAPE_PALETTES")]
assert "int segments = Math.max(6, Math.min(12, qualitySegments(10)))" in silk
assert "emitQuad(out, camera, previousLeft, previousRight, rightEdge, left, fabric)" in silk
assert "emitQuad(out, camera, previousSheenLeft, previousSheenRight, sheenRight, sheenLeft, sheen)" in silk
assert "double windPhase = renderAnimationTime * (0.068 + capeMoveState * 0.042)" in engine
assert "Vec3d tasselTip = tasselBottom.add(right.multiply(sideFlutter * 0.42))" in engine
assert "double leftBeat = 0.5 + 0.5 * Math.sin(phase + 0.16)" in engine
assert "double rightBeat = 0.5 + 0.5 * Math.sin(phase - 0.16)" in engine
assert "double dragonBeat = Math.sin(phase * 4.6 + side * 0.42)" in engine
assert "Math.sin(phase * 7.2 + side)" in engine
assert "double outerPulse = 1.0 + 0.035 * Math.sin(renderAnimationTime * 0.052 + 0.8)" in engine
assert engine.count("drawAuraRing(out, camera, pos") >= 4
assert "BAROX-VS-v068.jar" in build
assert "mod_version=0.68.0" in props
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v068"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v068"
module_calls = re.findall(r'\b(?:toggle|styled|cycle)\("([^"]+)"', modules)
assert len(module_calls) == 99, f"expected 99 existing modules, found {len(module_calls)}"
assert len(set(module_calls)) == 99, "module IDs must remain unique"
print("v068 animation, interpolation, geometry-budget, module-count and version checks passed")
