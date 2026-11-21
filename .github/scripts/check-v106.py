from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1])
meta = json.loads((root / "src/main/resources/fabric.mod.json").read_text(encoding="utf-8"))
assert meta["depends"]["minecraft"] == "1.21.4"
assert meta["depends"]["java"] == ">=21"

checks = {
    "mixin/HeldItemFirstPersonGlassMixin.java": (
        "barox$endFirstPersonGlass",
        "renderFirstPersonItem(",
        "HeldItemGlassRenderer.end();",
    ),
    "mixin/PlayerHeldItemGlassMixin.java": (
        "barox$endThirdPersonHeldItem",
        "renderItem(",
        "HeldItemGlassRenderer.end();",
    ),
    "mixin/BackgroundRendererMixin.java": (
        "baroxvs$tintAtmosphere",
        "getFogColor",
        "cir.setReturnValue(SkyboxEngine.tintFogColor(color));",
    ),
}

java = root / "src/main/java/com/baroxvs/client"
for rel, (handler, target, effect) in checks.items():
    src = (java / rel).read_text(encoding="utf-8")
    assert handler in src, f"missing handler: {rel}"
    assert target in src, f"missing target method: {rel}"
    assert effect in src, f"handler behavior changed: {rel}"
    annotations = re.findall(r"@Inject\\(((?:(?!@Inject\\().)*?)\\)\\s*private (?:static )?void\\s+" + re.escape(handler), src, re.S)
    assert len(annotations) == 1, f"expected one injection for {handler}"
    annotation = annotations[0]
    assert '@At("RETURN")' in annotation, f"expected RETURN injection: {handler}"
    assert "require = 1" in annotation, f"missing target-presence guard: {handler}"
    assert "allow" not in annotation, f"RETURN injection still has a maximum site cap: {handler}"
    assert "expect" not in annotation, f"RETURN injection still assumes a fixed site count: {handler}"

assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v106"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v106"
assert "mod_version=1.06.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert "BAROX-VS-v106.jar" in (root / "build.gradle").read_text(encoding="utf-8")
print("v106 checks passed: all return callbacks handle each normal return path; Minecraft 1.21.4 / Java 21 and v106 metadata verified")
