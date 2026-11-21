from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1])
java = root / "src/main/java/com/baroxvs/client"
meta = json.loads((root / "src/main/resources/fabric.mod.json").read_text(encoding="utf-8"))
assert meta["depends"]["minecraft"] == "1.21.4"
assert meta["depends"]["java"] == ">=21"

client = (java / "BaroxVsClient.java").read_text(encoding="utf-8")
config = (java / "config/BaroxConfig.java").read_text(encoding="utf-8")
menu = (java / "gui/BaroxMenuScreen.java").read_text(encoding="utf-8")
hud = (java / "gui/HudEditorScreen.java").read_text(encoding="utf-8")
cloth = (java / "gui/BaroxClothConfigScreen.java").read_text(encoding="utf-8")
commands = (java / "HudChatCommands.java").read_text(encoding="utf-8")
catalog = (java / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")

# All toggles flow through one config-aware group transition.
assert "setModuleEnabled(BaroxConfig config, String id, boolean enabled)" in client
for token in (
    "ModuleCatalog.childrenOf(id)",
    "String parent = ModuleCatalog.parentOf(id)",
    "for (ModuleCatalog.Module child : children) config.setOn(child.id(), false)",
    "if (parent != null) config.setOn(parent, true)",
    "noneMatch(child -> config.isOn(child.id()))",
    "child.defaultOn()",
    '"player_glass".equals(id)',
    '"head_accessories".equals(id)',
):
    assert token in client, f"missing grouped toggle behavior: {token}"

# Every visible switch path delegates; only the central owner may call setOn directly.
for name, source in (("BaroxMenuScreen", menu), ("HudEditorScreen", hud),
                     ("BaroxClothConfigScreen", cloth), ("HudChatCommands", commands)):
    assert ".setOn(" not in source, f"{name} bypasses BaroxVsClient.setModuleEnabled"
for token in (
    'BaroxVsClient.setModuleEnabled(cfg, "wings", true)',
    'BaroxVsClient.setModuleEnabled(cfg, "sky_studio", true)',
    "BaroxVsClient.setModuleEnabled(cfg, id, !cfg.isOn(id))",
):
    assert token in menu, f"menu route missing: {token}"
assert "BaroxVsClient.setModuleEnabled(config, module.id(), !config.isOn(module.id()))" in hud
assert "BaroxVsClient.setModuleEnabled(config, id, enabled)" in commands

# Cloth Reset values come from the catalog for all module toggles, not duplicated literals.
for module_id in ("wings", "head_accessories", "cape", "pet", "aura", "ambient_forms", "liquid_rain", "sky_studio"):
    assert f'catalogDefault("{module_id}")' in cloth, f"Cloth default not sourced from catalog: {module_id}"
    assert f'BaroxVsClient.setModuleEnabled(config, "{module_id}", v)' in cloth
assert 'catalogStyleDefault("geometry_quality")' in cloth
for module_id in ("head_accessories", "pet", "aura", "ambient_forms"):
    declaration = re.search(r'(?:toggle|styled)\("' + module_id + r'"[^\n]*', catalog)
    assert declaration and "false" in declaration.group(0), f"catalog default changed unexpectedly: {module_id}"

# The one-time performance marker no longer writes a mass false list or downgrades geometry.
start = config.index("if (performanceVersion < 1)")
end = config.index("modules.entrySet().removeIf", start)
migration = config[start:end]
assert "performanceVersion = 1;" in migration
assert "reducedCostModules" not in migration
assert "modules.put(" not in migration
assert "styles.put(" not in migration

# Legacy child=true values recover their parent; explicit parent=false clears stale children.
assert "private static void normalizeModuleGroups(Map<String, Boolean> moduleStates)" in config
assert "moduleStates.put(parent, true)" in config
assert "Boolean.FALSE.equals(moduleStates.get(parent.id()))" in config
assert "moduleStates.put(child.id(), false)" in config
assert "normalizeModuleGroups(modules);" in config
assert "normalizeModuleGroups(profile.modules);" in config

module_ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(module_ids) == len(set(module_ids)) == 99, f"module IDs changed: {len(module_ids)} declarations"
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v107"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v107"
assert "mod_version=1.07.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert "BAROX-VS-v107.jar" in (root / "build.gradle").read_text(encoding="utf-8")

print("v107 checks passed: unified module toggles, parent/child persistence, catalog-backed Cloth defaults, and non-destructive startup migration")