from pathlib import Path
import sys
root = Path(sys.argv[1])
ui = (root / "src/main/java/com/baroxvs/client/gui/Ui.java").read_text(encoding="utf-8")
menu = (root / "src/main/java/com/baroxvs/client/gui/BaroxMenuScreen.java").read_text(encoding="utf-8")
click = (root / "src/main/java/com/baroxvs/client/gui/ModuleClickGuiScreen.java").read_text(encoding="utf-8")
assert "public static void glassFrame(" in ui
assert "hudGlassPanel(" in ui and "specular sweep" in ui and "Fresnel rim" in ui
assert "Ui.glassFrame(" in menu and "this.frameW" in menu and "this.frameH" in menu
assert "Ui.glassFrame(" in click and "this.panelW" in click and "this.panelH" in click
assert "Ui.alpha(" in click
assert "BAROX-VS-v109.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=1.09.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v109"
print("v109 Liquid Glass regression checks passed")
