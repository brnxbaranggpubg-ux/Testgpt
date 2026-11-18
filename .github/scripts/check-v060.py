import hashlib
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

def sha(path):
    return hashlib.sha256((root / path).read_bytes()).hexdigest()

protected = {
    "src/main/java/com/baroxvs/client/gui/Ui.java": "4198ac5040937be397794aec2a86ea4049293870620539252904913b229a3cb3",
    "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java": "8b0409734fbbaad610c8fdd794505fdeeb30a5908113885bf323963bc3b9e0a3",
    "src/main/java/com/baroxvs/client/render/SkyboxEngine.java": "fcff4eba64138efc2070a6284ebf70ec541b2b80914e9cbd478cc2374dd25491",
    "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java": "fb41720a06dc0980e1fd723e80be11b1853f9e8977ecdefbedb67b4e928af4d8",
    "src/main/java/com/baroxvs/client/gui/ModuleSettingsScreen.java": "fecb35b4fd4763d4a8d078eadb846142b370c3c462657f721649f5285b0f89f6",
    "src/main/java/com/baroxvs/client/config/BaroxConfig.java": "4321a4ae512dae3c9f3e1a2b12f0e04bbcae14eef80cebdbea7f455ce879c40b",
    "src/main/java/com/baroxvs/client/theme/Themes.java": "e8e3a823a38720195b07c139199d7da3aca23376e588c364bd568afe2ea0cf23",
}
for path, expected in protected.items():
    actual = sha(path)
    assert actual == expected, f"Protected Liquid Glass/module file changed: {path} ({actual})"

screen = (root / "src/main/java/com/baroxvs/client/gui/ModuleClickGuiScreen.java").read_text(encoding="utf-8")
for forbidden in ("Ui.glassPanel", "Ui.glassButton", "Ui.roundRect", "glassPanel(", "glassButton("):
    assert forbidden not in screen, f"ClickGUI must not use Liquid Glass helper: {forbidden}"
for required in ("drawSidebar", "drawTopBar", "drawModulePanel", "drawInspector", "filteredModules",
                 "ModuleSettingsScreen", "mouseScrolled", "charTyped", "keepSelectionValid",
                 "ModuleCatalog.childrenOf", "Filter.ENABLED", "Filter.DISABLED", "detailsVisible"):
    assert required in screen, f"Missing ClickGUI feature or interaction: {required}"

catalog = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(ids) == len(set(ids)) == 99, f"Expected all 99 module IDs, got {len(ids)} declarations / {len(set(ids))} unique"

lang_dir = root / "src/main/resources/assets/baroxvs/lang"
locales = {name: json.loads((lang_dir / name).read_text(encoding="utf-8"))
           for name in ("en_us.json", "de_de.json", "tr_tr.json")}
keys = set(locales["en_us.json"])
assert all(set(values) == keys for values in locales.values()), "TR/DE/EN locale key parity failed"
menu_keys = ("visual_modules", "module_browser", "enabled_count", "search_modules", "studio", "theme",
             "modules_label", "all", "on", "off", "style", "no_modules", "change_search", "select_module",
             "selected_module", "disable_module", "enable_module", "open_settings", "submodules",
             "left_toggle", "right_settings", "scroll", "active")
for key in menu_keys:
    full = "baroxvs.clickgui." + key
    assert all(values.get(full) for values in locales.values()), f"Missing localized ClickGUI label: {full}"

assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v060"
assert "BAROX VS v060" in (root / "BUILD_VERSION.txt").read_text(encoding="utf-8")
assert "BAROX-VS-v060.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=0.60.0" in (root / "gradle.properties").read_text(encoding="utf-8")
print("v060 checks passed: redesigned dark ClickGUI, responsive inspector, search/filters/submodules, locale parity, 99 IDs; Liquid Glass and render/config files byte-identical to v059")
