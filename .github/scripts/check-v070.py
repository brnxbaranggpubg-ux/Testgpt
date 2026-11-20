from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
engine = (root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
modules = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
build = (root / "build.gradle").read_text(encoding="utf-8")
props = (root / "gradle.properties").read_text(encoding="utf-8")

assert "double waveA = pulseTime - Math.floor(pulseTime)" in engine
assert "double waveB = (waveA + 0.5) % 1.0" in engine
assert "waveColorA" in engine and "waveColorB" in engine
assert 'config.isOn("energy_shield")' in engine
assert "private void renderEnergyShield(" in engine
assert "drawGlassTorus(out, camera, core, right, up, forward" in engine
assert "for (int i = 0; i < 6; i++)" in engine
assert 'config.isOn("meteor_shower")' in engine
assert "private void renderMeteorShower(" in engine
assert "for (int segment = 0; segment < 5; segment++)" in engine
assert "emitQuad(out, camera, left0, right0, right1, left1, trailColor)" in engine
assert "drawGlassOrb(out, camera, head" in engine
assert "double rippleProgress = Math.min(1.0, age / 22.0)" in engine
assert "drawAuraRing(out, camera, point.add(0, 0.006, 0)" in engine
assert "Vec3d toeGlint = toe.add(0, 0.008, 0)" in engine
assert "double scanPhase = 0.5 + 0.5 * Math.sin(time * 0.058)" in engine
assert "double gemPulse = 1.0 + 0.12 * Math.sin(time * 0.073)" in engine

module_calls = re.findall(r'\b(?:toggle|styled|cycle)\("([^\"]+)"', modules)
assert len(module_calls) == 99, f"expected 99 modules, found {len(module_calls)}"
assert len(set(module_calls)) == 99, "module IDs must remain unique"
assert "BAROX-VS-v070.jar" in build
assert "mod_version=0.70.0" in props
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v070"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v070"
print("v070: five animation systems verified; 99 existing module IDs preserved")
