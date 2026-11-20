from pathlib import Path
import sys
root = Path(sys.argv[1])
engine = (root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text()
glass = (root / "src/main/java/com/baroxvs/client/render/SelfGlassRenderer.java").read_text()
assert "drawAuraDisc(out, camera, pos, radius" in engine
assert "drawGlassEllipsoid(out, camera, centre, side, WORLD_UP, tangent" not in engine
assert "Vec3d centre = jumpPulseOrigin.add(0, 0.055, 0)" in engine
assert "position.squaredDistanceTo(lastPrismTrailPos) >= 0.0064" in engine
assert "int layers = activeRenderQuality == 0 ? 1 : 2" in engine
assert "Math.min(0.34f, alpha)" in glass
assert "0.0012f * scale" in glass
assert "BAROX-VS-v066.jar" in (root / "build.gradle").read_text()
assert "mod_version=0.66.0" in (root / "gradle.properties").read_text()
print("v066 render repair checks passed")
