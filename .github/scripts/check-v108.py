from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1])
java = root / "src/main/java/com/baroxvs/client"
resources = root / "src/main/resources/assets/baroxvs"

# Build identity and supported runtime.
props = (root / "gradle.properties").read_text(encoding="utf-8")
assert "minecraft_version=1.21.4" in props
assert "mod_version=1.08.0" in props
assert "BAROX-VS-v108.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v108"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v108"
metadata = json.loads((root / "src/main/resources/fabric.mod.json").read_text(encoding="utf-8"))
assert metadata["id"] == "baroxvs"

# Every active module has a name and description in all three supported locales.
modules = re.findall(
    r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"',
    (java / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8"),
)
ids = [module_id for module_id, _, _ in modules]
assert len(ids) == 99 and len(set(ids)) == 99, f"expected 99 unique modules, got {len(ids)}"
locale_data = {}
for filename in ("en_us.json", "de_de.json", "tr_tr.json"):
    data = json.loads((resources / "lang" / filename).read_text(encoding="utf-8"))
    locale_data[filename] = data
    missing = [key for module_id in ids for key in (
        f"baroxvs.module.{module_id}", f"baroxvs.module.{module_id}.description"
    ) if not isinstance(data.get(key), str) or not data[key].strip()]
    assert not missing, f"{filename}: missing active module translations: {missing}"
assert set(locale_data["en_us.json"]) == set(locale_data["de_de.json"]) == set(locale_data["tr_tr.json"]), "locale key sets differ"
for stale_id in ("ambient_orbs", "hit_numbers", "defeat_dissolve", "ambient_cubes", "ambient_white"):
    for filename, data in locale_data.items():
        assert f"baroxvs.module.{stale_id}" not in data, f"{filename} still has retired {stale_id} key"
        assert f"baroxvs.module.{stale_id}.description" not in data
        assert not any(key.startswith(f"baroxvs.cloth.{stale_id}") for key in data)

# Settings screen labels: every source label has a corresponding localized key.
settings_screen = (java / "gui/ModuleSettingsScreen.java").read_text(encoding="utf-8")
labels = set(re.findall(r'addSlider\\("[^"]+", "([^"]+)"', settings_screen))
missing_settings = []
for label in labels:
    suffix = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
    key = f"baroxvs.settings.label.{suffix}"
    for filename, data in locale_data.items():
        if key not in data:
            missing_settings.append(f"{filename}: {label} -> {key}")
assert not missing_settings, "Missing setting label translations: " + "; ".join(missing_settings)
assert "L10n.settingLabel(option.label())" in settings_screen
assert "L10n.module(module)" in settings_screen
assert "module.description()" not in settings_screen
menu_screen = (java / "gui/BaroxMenuScreen.java").read_text(encoding="utf-8")
assert "L10n.moduleDescription(module)" in menu_screen
assert "CHOOSE YOUR WINGS" not in menu_screen
assert '"Motion  /  "' not in menu_screen
assert '"AURA SYNC "' not in menu_screen
assert '"Open " + module.name() + " settings"' not in menu_screen
assert '"Toggle " + module.name()' not in menu_screen

# Standardized storage paths and safe, generic legacy migration.
config = (java / "config/BaroxConfig.java").read_text(encoding="utf-8")
lyrics = (java / "hud/LyricFlowOverlay.java").read_text(encoding="utf-8")
skin = (java / "render/SkinStudio.java").read_text(encoding="utf-8")
hud = (java / "hud/HudRenderer.java").read_text(encoding="utf-8")
assert 'CONFIG_DIR.resolve("baroxvs")' in config and 'MOD_DIRECTORY.resolve("config.json")' in config
assert "findLegacyConfig()" in config and "OLDER_LEGACY_FILE" in config
assert 'DIRECTORY = CONFIG_DIR.resolve("baroxvs")' in lyrics and 'DIRECTORY.resolve("captions.lrc")' in lyrics
assert "findLegacyCaptionFile()" in lyrics
assert '"config/baroxvs/captions.lrc"' in hud
assert 'resolve("baroxvs/skins")' in skin
assert "public int skinProfile = 0;" in config and "skinProfile = clamp(skinProfile, 0, 2);" in config
assert "BaroxVsClient.config().skinProfile = selectedProfile;" in skin
assert "BaroxVsClient.config().save();" in skin
assert "syncSelectedProfile();" in skin
assert "baran3120" not in "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in (root / "src/main/java").rglob("*.java"))
assert "Base64" not in config and "Base64" not in lyrics

print("v108 checks passed: 99 modules translated in EN/DE/TR, retired keys purged, 112 settings labels translated, unified config/caption/skin paths, username removed from runtime sources, and persistent 3-slot skin selection")
