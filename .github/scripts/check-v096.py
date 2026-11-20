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
assert len(ids) == len(set(ids)) == 99, f"module declarations changed: {len(ids)} / {len(set(ids))} unique"
assert ids.count("jump_circle") == 1 and ids.count("wings") == 1
assert '"jump_circle"' in config and '"wings"' in config

# Jump Circle retains its five selectable presets and the same module/config identity.
assert 'new String[]{"Aurora Ring", "Sakura Bloom", "Prism Pulse", "Starlight", "Glass Wave"}' in catalog
jump = engine[engine.index('private void renderJumpPulse('):engine.index('Audio visualizer built from layered radial surface blooms.')]
for token in ('case 0 ->', 'case 1 ->', 'case 2 ->', 'case 3 ->', 'default ->',
              'drawJumpPetal(', 'drawJumpSegmentedBand(', 'drawGlassTorus(', 'drawStar('):
    assert token in jump, f"Jump Circle model renderer missing {token}"
assert 'private static void drawJumpPetal(' in engine
assert 'private static void drawJumpSegmentedBand(' in engine
assert 'Five distinct ground models' in catalog

# Wings are rendered in the normal world pass and their hinge follows torso yaw at the back plane.
wing = engine[engine.index('private void renderWings('):engine.index('private void renderChineseHat(')]
for token in ('p.prevBodyYaw', 'p.bodyYaw', 'back.multiply(0.105)', 'back.multiply(0.035)'):
    assert token in wing, f"body-attached wing anchor missing {token}"
assert 'p.prevYaw' not in wing and 'p.getYaw()' not in wing
assert 'back.multiply(0.52)' not in wing
assert 'if (config.isOn("wings")) withModuleStrength("wings", () -> renderWings(output, camera, player, partial));' in engine

assert "BAROX-VS-v096.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=0.96.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v096"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v096"
assert (root / "RENDER_REPAIR_v096.md").is_file()
print("v096 checks passed: five distinct Jump Circle meshes, torso-anchored wings, 99 unique module IDs and v096 version stamps")
