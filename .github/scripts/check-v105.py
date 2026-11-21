from pathlib import Path
import json
import sys

root = Path(sys.argv[1])
meta = json.loads((root / "src/main/resources/fabric.mod.json").read_text(encoding="utf-8"))
assert meta["depends"]["minecraft"] == "1.21.4"
assert meta["depends"]["java"] == ">=21"

gui = (root / "src/main/java/com/baroxvs/client/gui/ModuleClickGuiScreen.java").read_text(encoding="utf-8")
required = [
    "private float entryProgress;",
    "entryProgress = Math.min(1f, entryProgress + step * 7.5f);",
    "private static float easeOutCubic(float value)",
    "float windowScale = 0.955f + 0.045f * eased;",
    "matrices.scale(windowScale, windowScale, 1f);",
    "float rowStart = 0.08f + Math.min(i, 10) * 0.035f;",
    "matrices.translate((1f - rowEase) * 12f, 0f, 0f);",
    "int alpha = Math.round(0xB8 * easeOutCubic(entryProgress));",
    "Ui.alpha(theme.primary(), sweepAlpha)",
]
for token in required:
    assert token in gui, f"missing GUI entrance feature: {token}"
assert gui.count("if (entryProgress < 0.985f) return true;") == 2
assert "getFramebuffer" not in gui and "Thread.sleep" not in gui
assert "ModuleClickGuiScreen.class" not in gui

assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v105"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v105"
assert "mod_version=1.05.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert "BAROX-VS-v105.jar" in (root / "build.gradle").read_text(encoding="utf-8")
print("v105 checks passed: eased ClickGUI entrance, centre scale/settle, staggered module rows, safe input lock, Minecraft 1.21.4 / Java 21 and v105 metadata")
