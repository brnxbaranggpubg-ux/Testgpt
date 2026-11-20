#!/usr/bin/env python3
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
hud = (root / "src/main/java/com/baroxvs/client/hud/HudRenderer.java").read_text(encoding="utf-8")
cosmetic = (root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
held = (root / "src/main/java/com/baroxvs/client/render/HeldItemGlassRenderer.java").read_text(encoding="utf-8")
self_glass = (root / "src/main/java/com/baroxvs/client/render/SelfGlassRenderer.java").read_text(encoding="utf-8")
catalog = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([^"]+)"', catalog)
assert len(ids) == 99, f"expected 99 module declarations, found {len(ids)}"
assert len(set(ids)) == 99, "module IDs must stay unique"
for module_id in ("crosshair_ring", "hand_glow", "arm_glow", "held_item_glow", "self_glass"):
    assert re.search(r'\b(?:toggle|styled|cycle)\("' + re.escape(module_id) + r'"', catalog), module_id

checks = {
    "Crosshair Bloom orbiting pearl markers": "double bloomOrbit = -ticks * 0.027;" in hud,
    "Hand Glow paired wrist satellites": "double handOrbit = renderAnimationTime * 0.046;" in cosmetic,
    "Arm Glow travelling forearm beacon": "double beaconT = 0.24 + 0.56 * (0.5 + 0.5 * Math.sin(renderAnimationTime * 0.092));" in cosmetic,
    "Held Item Glow counter-moving surface sweep": "float counterCoord = fract((u * 0.22f + v * 0.78f - settings.phase() * 0.61f + 0.19f)" in held,
    "Self Glass layered optical echo": "float echoCoord = fract((u * 0.24f - v * 0.78f - phase * 0.72f + 0.31f) * 1.14f);" in self_glass,
    "archive filename": "archiveFileName = 'BAROX-VS-v089.jar'" in (root / "build.gradle").read_text(encoding="utf-8"),
    "version property": "mod_version=0.89.0" in (root / "gradle.properties").read_text(encoding="utf-8"),
    "version markers": "BAROX VS v089" in (root / "VERSION").read_text(encoding="utf-8") and "BAROX VS v089" in (root / "BUILD_VERSION.txt").read_text(encoding="utf-8"),
}
for label, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + label)
assert all(checks.values()), "one or more v089 invariants failed"
print(f"PASS: {len(ids)} unique module IDs retained")
