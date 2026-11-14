#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")
base = root / "src/main/java/com/baroxvs/client"
catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
engine = (base / "cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
gui = (base / "gui/ModuleClickGuiScreen.java").read_text(encoding="utf-8")
metadata = json.loads((root / "src/main/resources/fabric.mod.json").read_text(encoding="utf-8"))

ids = re.findall(r'(?:toggle|styled|cycle)\("([^"]+)"', catalog)
assert len(ids) == 91, f"Expected 91 modules after v024, got {len(ids)}"
assert len(ids) == len(set(ids)), "Duplicate module IDs found"
assert 'styled("module_resonance"' in catalog
for preset in ["Balanced", "Brilliant", "Soft", "Prismatic"]:
    assert preset in catalog, f"Missing Module Resonance preset: {preset}"

for token in [
    'config.isOn("module_resonance")',
    "renderV024ModuleResonance(out, camera, pos, right, forward, up, time);",
    'ModuleCatalog.inCategory(category)',
    '"Cosmetics", "Effects", "Trails"',
    "ModuleCatalog.Kind.CYCLE",
    "v024ModuleCacheTick != tick",
    "drawRing(out, camera, centre",
    "drawStar(out, camera, at",
]:
    assert token in engine, f"Missing v024 engine feature: {token}"

assert "BUILD 024" in gui
assert 'allCount + " MODULES"' in gui
assert '"78 MODULES"' not in gui
assert "Math.max(220, Math.min(960, width - 12))" in gui
assert "panelW < 400 ? 72 : 148" in gui
assert bool(metadata.get("id")), "fabric.mod.json is missing its mod id"
print("v024 checks passed: 91 unique modules; shared active-module palette; cached visuals; phone-responsive ClickGUI; live module count.")
