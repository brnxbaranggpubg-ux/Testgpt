from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
engine = (root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
modules = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
build = (root / "build.gradle").read_text(encoding="utf-8")
props = (root / "gradle.properties").read_text(encoding="utf-8")

assert "double breath0 = Math.sin(p0 * 1.72 + time * 0.042) * 0.035" in engine
assert "double crownPhase = time * 0.052 * speed" in engine
assert "drawGlassTorus(out, camera, crown.add(0, -0.075 * scale, 0)" in engine
assert "double orbitBreath = 1.0 + Math.sin(phase * 0.58 + i * 0.73) * 0.055" in engine
assert "Vec3d facetGlint = centre.add(right.multiply(Math.sin(phase * 1.3 + i)" in engine
assert "double weatherPhase = time * 0.021 * speed" in engine
assert "Vec3d cloudLeft = pos.add(right.multiply(-0.58 + Math.sin(weatherPhase * 0.92) * 0.075))" in engine
assert "withAlpha(tint, (int) Math.round(0x46 * opacity * weatherGain))" in engine
assert "drawAuraRing(out, camera, pos.add(0, 1.02 + lift, 0), 0.72 * scale * pulse" in engine
assert "double orbitZ = Math.sin(angle * 0.88) * 0.38" in engine
assert "Vec3d satellite = centre.add(right.multiply(Math.cos(angle * 1.8 + i)" in engine
assert "drawAuraRing(out, camera, centre, orbRadius * 1.42, 0.075" in engine
assert "double haloPhase = time * 0.018" in engine
assert "Vec3d tiltedAxis = right.add(up.multiply(0.14 * Math.sin(haloPhase * 0.7))).normalize()" in engine
assert "Vec3d pearl = head.add(right.multiply(Math.cos(angle) * 0.34 * scale * pulse))" in engine

module_calls = re.findall(r'\b(?:toggle|styled|cycle)\("([^"]+)"', modules)
assert len(module_calls) == 99, f"expected 99 modules, found {len(module_calls)}"
assert len(set(module_calls)) == 99, "module IDs must remain unique"
assert "BAROX-VS-v069.jar" in build
assert "mod_version=0.69.0" in props
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v069"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v069"
print("v069: 5 new module animation checks passed; 99 existing module IDs preserved")
