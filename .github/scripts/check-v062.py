import re
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
base = root / "src/main/java/com/baroxvs/client"

ui = (base / "gui/Ui.java").read_text(encoding="utf-8")
settings = (base / "gui/ModuleSettingsScreen.java").read_text(encoding="utf-8")
menu = (base / "gui/BaroxMenuScreen.java").read_text(encoding="utf-8")
click = (base / "gui/ModuleClickGuiScreen.java").read_text(encoding="utf-8")
hud = (base / "hud/HudRenderer.java").read_text(encoding="utf-8")

assert "public static void flatPanel(" in ui
assert "public static void hudGlassPanel(" in ui
assert "public static void glassPanel(" not in ui
assert "public static void glassButton(" not in ui
for label, source in [("module settings", settings), ("visual gallery/music page", menu)]:
    assert "Ui.flatPanel(" in source, f"{label} did not adopt matte panels"
    assert "Ui.glassPanel(" not in source, f"{label} still uses GUI Liquid Glass"
    assert "Ui.glassButton(" not in source, f"{label} still uses GUI glass buttons"
assert "visualTime" not in settings, "old animated material clock remains in settings GUI"
assert "Ui.glassPanel(" not in click and "Ui.glassButton(" not in click
assert "Ui.hudGlassPanel(" in hud, "in-game HUD glass renderer was not retained"
assert "HUD-only Liquid Glass" in ui, "HUD-specific glass documentation missing"

catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(ids) == len(set(ids)) == 99, "module registrations changed"

engine = (base / "cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
for token in [
    "AVATAR_GLASS_TEXTURE", "drawAvatarGlassPrism(",
    "SELF_GLASS_GRID_SEGMENTS = 8", "double fresnel = Math.pow(1.0 - Math.max(0.0, facing), 2.65);"
]:
    assert token in engine, f"Self Glass pilot missing: {token}"
for token in ["selfGlassRefraction", "selfGlassEdge", "selfGlassGloss"]:
    assert token in settings, f"Self Glass setting missing: {token}"

assert (root / "GUI_MATTE_REDESIGN_v062.md").is_file()
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v062"
assert "BAROX VS v062" in (root / "BUILD_VERSION.txt").read_text(encoding="utf-8")
assert "BAROX-VS-v062.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=0.62.0" in (root / "gradle.properties").read_text(encoding="utf-8")
print("v062 checks passed: GUI Liquid Glass removed, flat opaque panels active, HUD and Self Glass preserved, 99 modules intact")
