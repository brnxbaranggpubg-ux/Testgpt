#!/usr/bin/env python3
from pathlib import Path
import re, sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")
base = root / "src/main/java/com/baroxvs/client"
screen = (base / "gui/ModuleClickGuiScreen.java").read_text(encoding="utf-8")
client = (base / "BaroxVsClient.java").read_text(encoding="utf-8")
catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
settings = (base / "gui/ModuleSettingsScreen.java").read_text(encoding="utf-8")
ids = re.findall(r'(?:toggle|styled|cycle)\("([^"]+)"', catalog)
assert len(ids) == 78, f"Expected 78 modules, got {len(ids)}"
assert "ModuleClickGuiScreen" in client and "new ModuleClickGuiScreen(CONFIG)" in client
for feature in [
    "ModuleCatalog.all()", "ModuleCatalog.categories()", "ModuleCatalog.inCategory(",
    "mouseClicked(", "mouseScrolled(", "charTyped(", "keyPressed(",
    "button == 1", "button == 0", "new ModuleSettingsScreen(this, cfg, module)",
    "searchFocused", "Filter.ENABLED", "Filter.DISABLED", "openProgress",
    "Ui.glassPanel", "approach(", "LMB  TOGGLE", "RMB  SETTINGS"
]:
    assert feature in screen, f"Missing ClickGUI feature: {feature}"
assert "public ModuleSettingsScreen(Screen parent, BaroxConfig config, ModuleCatalog.Module module)" in settings
assert "new BaroxMenuScreen(cfg)" in screen, "The original Visual Studio page must remain accessible."
assert "toggleModule(module.id())" in screen, "Toggle must use the central config/toast path."
print("v021 passed: 78 modules; animated ClickGUI; category navigation; search and enabled filters; left-click toggle; right-click settings; original Studio preserved.")
