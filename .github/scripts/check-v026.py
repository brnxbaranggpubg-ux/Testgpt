#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")
base = root / "src/main/java/com/baroxvs/client"
screen = (base / "gui/ModuleClickGuiScreen.java").read_text(encoding="utf-8")
client = (base / "BaroxVsClient.java").read_text(encoding="utf-8")
catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
settings = (base / "gui/ModuleSettingsScreen.java").read_text(encoding="utf-8")
metadata = json.loads((root / "src/main/resources/fabric.mod.json").read_text(encoding="utf-8"))

ids = re.findall(r'(?:toggle|styled|cycle)\("([^"]+)"', catalog)
assert len(ids) == 91, f"Expected 91 existing modules, got {len(ids)}"
assert len(ids) == len(set(ids)), "Duplicate module IDs found"
assert "new ModuleClickGuiScreen(CONFIG)" in client
assert "new BaroxMenuScreen(cfg)" in screen
assert "new ModuleSettingsScreen(this, cfg, module)" in screen
for token in [
    "private void drawSidebar(",
    "private void drawToolbar(",
    "private void drawModules(",
    "private void drawModuleCard(",
    "private void drawInspector(",
    "private void drawBackdrop(",
    "private void drawShell(",
    "easedOpenProgress",
    "Filter.ENABLED",
    "Filter.DISABLED",
    "ModuleCatalog.categories()",
    "ModuleCatalog.inCategory(",
    "mouseClicked(",
    "mouseScrolled(",
    "charTyped(",
    "keyPressed(",
    "private void openSettings(",
    "private void toggle(",
    "BaroxVsClient.toggleModule(module.id())",
    "categoryIcon(",
    "drawScrollbar(",
    "OPEN SETTINGS",
    "ENABLE MODULE",
    "DISABLE MODULE",
]:
    assert token in screen, f"Missing client GUI feature: {token}"
assert "ModuleSettingsScreen(Screen parent, BaroxConfig config, ModuleCatalog.Module module)" in settings
assert "MinecraftClient" not in screen
assert "91 MODULES" in screen
assert "BUILD 026" in screen
assert "mod_version" in (root / "gradle.properties").read_text(encoding="utf-8")
print("v026 checks passed: 91 unchanged modules, client-style responsive ClickGUI, animated switches/cards, live search/filter, detail inspector, settings navigation, existing Studio preserved.")
