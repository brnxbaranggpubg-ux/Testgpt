#!/usr/bin/env python3
"""Validate BAROX VS v030 reference-inspired visual HUD systems."""
from __future__ import annotations
import json
import pathlib
import re
import sys


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit("v030 check failed: " + message)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: check-v030.py <project-directory>")
    root = pathlib.Path(sys.argv[1])
    base = root / "src/main/java/com/baroxvs/client"
    catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
    hud = (base / "hud/HudRenderer.java").read_text(encoding="utf-8")
    editor = (base / "gui/HudEditorScreen.java").read_text(encoding="utf-8")
    settings = (base / "gui/ModuleSettingsScreen.java").read_text(encoding="utf-8")
    sky = (base / "render/SkyboxEngine.java").read_text(encoding="utf-8")

    ids = re.findall(r'(?:toggle|styled|cycle)\("([^\"]+)', catalog)
    require(len(ids) == 81, f"expected 81 unique modules, found {len(ids)}")
    require(len(ids) == len(set(ids)), "module IDs are not unique")
    require('styled("active_modules", "Active Visuals"' in catalog, "Active Visuals module is missing")
    require('toggle("dynamic_island", "Dynamic Island"' in catalog, "Dynamic Island module is missing")

    for token in ("updateActiveModuleBlend()", "visibleActiveModules()", "drawActiveModules(",
                  "drawDynamicIsland(", "activeModuleBlend", "dynamicIslandWidth"):
        require(token in hud, f"HUD renderer missing {token}")
    for token in ('"x"', '"y"', '"scale"', '"opacity"'):
        require(token in hud, f"per-widget transform missing {token}")
    for category in ("ModuleCatalog.EFFECTS", "ModuleCatalog.COSMETICS", "ModuleCatalog.TRAILS"):
        require(category in hud, f"Active Visuals scope is missing {category}")
    require("MusicEngine.audioLevel()" in hud and "MusicEngine.isPlaying()" in hud,
            "Dynamic Island is not wired to BAROX player/audio state")
    require("BEFORE_ENTITIES" not in hud, "late world-pass hook must not be used by HUD renderer")

    for token in ('selectedWidget = "global"', 'canSelectWidget(', 'hasShiftDown()',
                  'drawWidgetControls(', 'moveSelected(', 'config.setModuleValue(selectedWidget, "x"',
                  'config.setModuleValue(selectedWidget, "y"', 'config.setModuleValue(selectedWidget, "scale"'):
        require(token in editor, f"HUD Studio interaction missing {token}")
    for widget in ("active_modules", "dynamic_island", "status_bar", "coordinates", "world_card"):
        require(f'"{widget}"' in editor, f"HUD Studio does not whitelist {widget}")
    for token in ("moduleRows", "moduleWidth", "islandWidth"):
        require(token in settings, f"module-specific setting missing {token}")

    require("WorldRenderEvents" not in sky and "register(WorldRenderEvents" not in sky,
            "v029 vanilla sky protection regressed")
    require("MAX_FILE_BYTES = 32L * 1024L * 1024L" in sky and "try (NativeImage image" in sky,
            "bounded sky image validation regressed")

    language_dir = root / "src/main/resources/assets/baroxvs/lang"
    language_files = ("en_us.json", "de_de.json", "tr_tr.json")
    languages = [json.loads((language_dir / name).read_text(encoding="utf-8")) for name in language_files]
    keys = set(languages[0])
    require(set(languages[1]) == keys and set(languages[2]) == keys, "language key sets differ")
    for data in languages:
        for key in ("baroxvs.module.active_modules", "baroxvs.module.active_modules.description",
                    "baroxvs.module.dynamic_island", "baroxvs.module.dynamic_island.description",
                    "baroxvs.hud.active_visuals", "baroxvs.hud.island.ready",
                    "baroxvs.hud.editor.widget_drag", "baroxvs.hud.editor.reset_widget"):
            require(key in data and data[key], f"missing translation {key}")

    build = (root / "build.gradle").read_text(encoding="utf-8")
    props = (root / "gradle.properties").read_text(encoding="utf-8")
    require("BAROX-VS-v030.jar" in build, "JAR filename is stale")
    require("mod_version=0.30.0" in props, "mod version is stale")
    require((root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v030",
            "VERSION marker is stale")
    require((root / "REFERENCE_REVIEW_v030.md").is_file(), "reference audit document is missing")
    report = (root / "REFERENCE_REVIEW_v030.md").read_text(encoding="utf-8")
    for name in ("Wyvern", "SpaceVisuals", "Nursultan", "Phobia", "LyricsFlow",
                 "Rockstar", "EvolutionDLC", "CatLean"):
        require(name.lower() in report.lower(), f"reference audit omits {name}")

    print("v030 checks passed: 81 modules, Active Visuals, Dynamic Island, per-widget HUD editor, TR/DE/EN parity and v029 sky protection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
