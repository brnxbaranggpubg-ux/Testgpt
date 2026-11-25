from pathlib import Path
import sys

root = Path(sys.argv[1])
gui = root / "src/main/java/com/baroxvs/client/gui"
required = {
    "helper": gui / "LiquidGlassModuleUi.java",
    "clickgui": gui / "ModuleClickGuiScreen.java",
    "mobile_chooser": gui / "BaroxMenuScreen.java",
    "settings": gui / "ModuleSettingsScreen.java",
    "ui": gui / "Ui.java",
    "catalog": root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java",
    "self_glass": root / "src/main/java/com/baroxvs/client/render/SelfGlassRenderer.java",
    "held_glass": root / "src/main/java/com/baroxvs/client/render/HeldItemGlassRenderer.java",
    "hud": root / "src/main/java/com/baroxvs/client/hud/HudRenderer.java",
}
for name, path in required.items():
    if not path.is_file():
        raise SystemExit(f"Missing required v110 source: {name}: {path}")

helper = required["helper"].read_text(encoding="utf-8")
click = required["clickgui"].read_text(encoding="utf-8")
menu = required["mobile_chooser"].read_text(encoding="utf-8")
settings = required["settings"].read_text(encoding="utf-8")
ui = required["ui"].read_text(encoding="utf-8")
catalog = required["catalog"].read_text(encoding="utf-8")
hud = required["hud"].read_text(encoding="utf-8")
self_glass = required["self_glass"].read_text(encoding="utf-8")
held_glass = required["held_glass"].read_text(encoding="utf-8")

modules = (
    "player_glass", "hand_glow", "arm_glow", "held_item_glow", "self_glass",
    "liquid_rain", "glint", "music_aura_sync", "orbit_stars", "halo",
    "pet_glow", "jump_circle", "wing_glints", "wing_outline",
    "sky_mood", "sky_aurora", "sky_nebula", "sky_meteors", "sky_constellations",
    "keystrokes_hud", "biome_toast", "watermark", "dynamic_island", "crosshair_ring",
)
for module_id in modules:
    if f'"{module_id}"' not in helper:
        raise SystemExit(f"Glass module missing from shared material catalog: {module_id}")
    if f'"{module_id}"' not in catalog:
        raise SystemExit(f"Glass module missing from ModuleCatalog: {module_id}")

checks = {
    "shared class exposes Liquid Glass surfaces": "Ui.hudGlassPanel" in helper and "Ui.glassFrame" in helper,
    "ClickGUI module rows use shared Liquid Glass": "LiquidGlassModuleUi.drawSurface" in click,
    "ClickGUI selected inspector uses shared material": "LiquidGlassModuleUi.supports(module.id()" in click,
    "ClickGUI child rows use shared material": "LiquidGlassModuleUi.supports(child.id()" in click,
    "mobile Choose cards use shared material": "LiquidGlassModuleUi.supports(module.id()" in menu,
    "module style chooser highlights glass variants": "LiquidGlassModuleUi.isGlassVariant(target.id(), value)" in settings,
    "base UI includes animated Glass frame": "public static void glassFrame" in ui and "public static void hudGlassPanel" in ui,
    "HUD modules still share Liquid Glass": "Ui.hudGlassPanel" in hud,
    "Self Glass renderer remains present": "Liquid Glass" in self_glass or "glass" in self_glass.lower(),
    "Held Item Glass renderer remains present": "glass" in held_glass.lower(),
    "version metadata uses v110": "BAROX-VS-v110.jar" in (root / "build.gradle").read_text(encoding="utf-8"),
    "Gradle mod version is 1.10.0": "mod_version=1.10.0" in (root / "gradle.properties").read_text(encoding="utf-8"),
    "release version metadata is v110": (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v110",
}
for label, ok in checks.items():
    if not ok:
        raise SystemExit(f"v110 integration check failed: {label}")
print(f"v110 source checks passed ({len(modules)} explicit glass modules, {len(checks)} assertions)")
