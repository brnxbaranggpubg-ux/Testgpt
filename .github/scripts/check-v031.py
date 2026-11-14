#!/usr/bin/env python3
"""Validate BAROX VS v031's Kimiko-inspired, original visual HUD additions."""
from __future__ import annotations
import json
import pathlib
import re
import sys


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit("v031 check failed: " + message)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: check-v031.py <project-directory>")
    root = pathlib.Path(sys.argv[1])
    base = root / "src/main/java/com/baroxvs/client"
    catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
    hud = (base / "hud/HudRenderer.java").read_text(encoding="utf-8")
    editor = (base / "gui/HudEditorScreen.java").read_text(encoding="utf-8")
    settings = (base / "gui/ModuleSettingsScreen.java").read_text(encoding="utf-8")
    config = (base / "config/BaroxConfig.java").read_text(encoding="utf-8")
    sky = (base / "render/SkyboxEngine.java").read_text(encoding="utf-8")

    ids = re.findall(r'(?:toggle|styled|cycle)\("([^\"]+)', catalog)
    require(len(ids) == 84, f"expected 84 modules, found {len(ids)}")
    require(len(ids) == len(set(ids)), "module IDs are not unique")
    for module_id in ("keystrokes_hud", "fps_graph", "watermark"):
        require(f'"{module_id}"' in catalog, f"module {module_id} missing from catalogue")
        require(f'cfg.isOn("{module_id}")' in hud, f"module {module_id} missing HUD render hook")
        require(f'"{module_id}"' in editor, f"module {module_id} missing HUD editor whitelist")
    require('module.category().equals(ModuleCatalog.HUD)' in settings,
            "generic HUD settings path missing for Watermark")

    for token in ("mc.options.forwardKey.isPressed()", "mc.options.leftKey.isPressed()",
                  "mc.options.backKey.isPressed()", "mc.options.rightKey.isPressed()",
                  "mc.options.jumpKey.isPressed()", "mc.options.sneakKey.isPressed()",
                  "keyPressBlend", "drawKeyCap("):
        require(token in hud, f"Keystrokes HUD missing {token}")
    require("GLFW" not in hud, "unexpected GLFW dependency in HUD renderer")
    require("clickCount" not in hud and "sendChatMessage" not in hud,
            "Keystrokes HUD must not add click counting or automation")

    for token in ("new float[48]", "fpsSamples[fpsSampleCursor]", "ticks % 4 == 0",
                  "fpsSampleCount", "drawFpsGraph(", "styleGraphLine()", "1000f / fps"):
        require(token in hud, f"FPS graph missing {token}")
    graph = hud[hud.find("private void drawFpsGraph"):hud.find("private boolean styleGraphLine")]
    require("new ArrayList" not in graph,
            "FPS graph should not allocate per-sample object lists while drawing")

    for token in ('cfg.style("potions_list")', 'cfg.moduleValue("potions_list", "rows"',
                  "effects.sort(Comparator.comparingInt(HudRenderer::remaining))",
                  'cfg.style("armor_hud")', "case 2 -> 108", "EquipmentSlot.HEAD"):
        require(token in hud, f"Armor/Potion HUD enhancement missing {token}")
    require('new String[]{"Classic", "Orbit", "Pulse", "Diamond"}' in catalog,
            "crosshair style variants are missing")
    for token in ("drawCrosshairRing", "Ui.ring(c, cx, cy"):
        require(token in hud, f"crosshair rendering missing {token}")
    crosshair = hud[hud.find("private void drawCrosshairRing"):hud.find("// ------------------------------------------------------------------ Kimiko-inspired")]
    require("targetedEntity" not in crosshair,
            "decorative crosshair must not access target state")

    for token in ("keySize", "keyGap", "fpsGraphWidth", "potionRows"):
        require(token in settings, f"setting {token} not present")
    for token in ('config.setModuleValue("keystrokes_hud", "keySize"',
                  'config.setModuleValue("keystrokes_hud", "keyGap"',
                  'config.setModuleValue("fps_graph", "width"',
                  'config.setModuleValue("potions_list", "rows"'):
        require(token in settings, f"setting persistence missing {token}")
    require("moduleValue" in config and "baran3120.cfg" in config,
            "existing BAROX config store is not present")
    require("WorldRenderEvents" not in sky and "register(WorldRenderEvents" not in sky,
            "v029 vanilla sky fallback regressed")

    lang_dir = root / "src/main/resources/assets/baroxvs/lang"
    names = ("en_us.json", "de_de.json", "tr_tr.json")
    languages = [json.loads((lang_dir / name).read_text(encoding="utf-8")) for name in names]
    keyset = set(languages[0])
    require(all(set(doc) == keyset for doc in languages[1:]), "locale key sets differ")
    expected = ("baroxvs.module.keystrokes_hud", "baroxvs.module.keystrokes_hud.description",
                "baroxvs.module.fps_graph", "baroxvs.module.fps_graph.description",
                "baroxvs.module.watermark", "baroxvs.module.watermark.description",
                "baroxvs.hud.keystrokes", "baroxvs.hud.fps_graph")
    for lang, doc in zip(names, languages):
        for key in expected:
            require(key in doc and doc[key], f"{lang} missing {key}")

    build = (root / "build.gradle").read_text(encoding="utf-8")
    props = (root / "gradle.properties").read_text(encoding="utf-8")
    require("BAROX-VS-v031.jar" in build, "JAR filename is stale")
    require("mod_version=0.31.0" in props, "mod version is stale")
    require((root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v031",
            "VERSION marker is stale")
    report = (root / "KIMIKO_REFERENCE_AUDIT_v031.md").read_text(encoding="utf-8")
    for name in ("Keystrokes", "FPS Graph", "Watermark", "Crosshair", "Armor HUD", "Potion List"):
        require(name.lower() in report.lower(), f"reference report omits {name}")
    require("No bytecode" in report and "not binary-compatible" in report,
            "reference/license and compatibility boundaries are not documented")

    print("v031 checks passed: 84 unique modules, KeyStrokes HUD, FPS history, Watermark, advanced Armor/Potions, crosshair styles, locale parity and v029 sky protection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
