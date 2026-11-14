#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")
base = root / "src/main/java/com/baroxvs/client"
engine = (base / "cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
catalog = (base / "cosmetic/CosmeticCatalog.java").read_text(encoding="utf-8")
module_catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
gui = (base / "gui/ModuleClickGuiScreen.java").read_text(encoding="utf-8")

ids = re.findall(r'(?:toggle|styled|cycle)\("([^"]+)"', module_catalog)
assert len(ids) == 91, f"Expected 91 v024 modules preserved, found {len(ids)}"
assert len(ids) == len(set(ids)), "Duplicate module IDs found"
assert 'WING_MOTIONS = {"Gentle", "Flap", "Pulse", "Still", "Flight", "Flow"}' in catalog

for token in [
    "private void updateAnimationState(PlayerEntity player)",
    "previousWingFlapAngle = currentWingFlapAngle",
    "renderWingFlapAngle = previousWingFlapAngle",
    "renderWingFlex = previousWingFlex",
    "double acceleration = (targetFlap - currentWingFlapAngle) * 0.27 - wingFlapVelocity * 0.62",
    "case 4 -> Math.sin(wingPhase)",
    "case 3 -> 0.0",
    "capeMoveState",
    "capeTurnState",
    "renderAnimationTime = tick + partial",
    "double travelling = Math.sin(phase)",
    "for (int i = 0; i <= 34; i++)",
    "double leftOpen = 0.14 + 0.86",
    "double rightOpen = 0.14 + 0.86",
    "renderWingFlex * span * span * 0.34",
]:
    assert token in engine, f"Missing animation system feature: {token}"

assert 'double movement = capeMoveState;' in engine
assert 'double turn = capeTurnState;' in engine
assert 'double verticalMotion = capeVerticalState;' in engine
assert 'double glide = capeGlideState;' in engine

for start, end in [
    ("    private void renderGlints(", "    /** A decorative butterfly companion"),
    ("    private void renderMusicAura(", "    /**\n     * v022 additions"),
    ("    private void renderGlowCosmetics(", "    private void renderChunkRain("),
    ("    private void renderSilkRibbons(", "    private static final int[][] CAPE_PALETTES"),
]:
    a = engine.index(start)
    b = engine.index(end, a)
    section = engine[a:b]
    assert not re.search(r"(?<![+])\btick\s*\*", section), f"Raw tick-step animation remains in {start.strip()}"

assert "private float easedOpenProgress;" in gui
assert "easedOpenProgress = 1f - inverse * inverse * inverse;" in gui
assert "(1f - easedOpenProgress)" in gui
print("v025 checks passed: 91 modules preserved; six wing motion presets; spring-driven movement-aware wing pose; interpolated frame clock; feather follow-through; smoother cape/silk; folding butterfly wings; eased ClickGUI.")
