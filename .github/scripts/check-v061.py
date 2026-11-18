import hashlib
import re
import struct
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

def sha(path):
    return hashlib.sha256((root / path).read_bytes()).hexdigest()

protected = {
    "src/main/java/com/baroxvs/client/gui/Ui.java": "4198ac5040937be397794aec2a86ea4049293870620539252904913b229a3cb3",
    "src/main/java/com/baroxvs/client/hud/HudRenderer.java": "b7cd90e0e280e1fb721ec36b21338759927b166a5389a8d7e5d0b7db2ab0d6b1",
    "src/main/java/com/baroxvs/client/gui/HudEditorScreen.java": "cef7b4a29fce165912016fd5626feefe88d112d5737532835ed8aa55abf2ca7e",
    "src/main/java/com/baroxvs/client/render/SkyboxEngine.java": "fcff4eba64138efc2070a6284ebf70ec541b2b80914e9cbd478cc2374dd25491",
    "src/main/java/com/baroxvs/client/config/BaroxConfig.java": "4321a4ae512dae3c9f3e1a2b12f0e04bbcae14eef80cebdbea7f455ce879c40b",
    "src/main/java/com/baroxvs/client/theme/Themes.java": "e8e3a823a38720195b07c139199d7da3aca23376e588c364bd568afe2ea0cf23",
    "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java": "fb41720a06dc0980e1fd723e80be11b1853f9e8977ecdefbedb67b4e928af4d8",
    "src/main/java/com/baroxvs/client/gui/BaroxMenuScreen.java": "b999545362eedcf9cf0985471e23fe19dddb8e394c357b939832034073aab490",
}
for path, expected in protected.items():
    actual = sha(path)
    assert actual == expected, f"Unrelated glass/UI source changed: {path} ({actual})"


def java_method(source, name):
    match = re.search(r'\b(?:private|public|protected)\s+(?:static\s+)?[\w<>\[\], ?]+\s+'
                      + re.escape(name) + r'\s*\([^;]*?\)\s*\{', source, re.S)
    assert match, f"Method not found: {name}"
    i = match.end() - 1
    depth, state, escaped = 0, "code", False
    while i < len(source):
        c = source[i]
        n = source[i + 1] if i + 1 < len(source) else ""
        if state == "line":
            if c == "\n": state = "code"
        elif state == "block":
            if c == "*" and n == "/": state = "code"; i += 1
        elif state == "string":
            if escaped: escaped = False
            elif c == "\\": escaped = True
            elif c == '"': state = "code"
        elif state == "char":
            if escaped: escaped = False
            elif c == "\\": escaped = True
            elif c == "'": state = "code"
        else:
            if c == "/" and n == "/": state = "line"; i += 1
            elif c == "/" and n == "*": state = "block"; i += 1
            elif c == '"': state = "string"
            elif c == "'": state = "char"
            elif c == "{": depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0: return source[match.start():i + 1]
        i += 1
    raise AssertionError("Unclosed method: " + name)


engine = (root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
unchanged_methods = {
    "renderGlowCosmetics": "bb7371b0f4207510dc8cb5e2f175d7b81631fb5b22d2197c5e38c6c4d684a2de",
    "renderLiquidGlassRain": "a3fe48876c91650a7e1e1d89306bea4f3a80bbb0f0daba61d0b75ec07ccd60d2",
    "renderAmbientGeometry": "2e2fe9303cd304aff335222574b88b038e92c5e464f34fe41ed1df258ce3789b",
    "drawGlassOrb": "ca98f942acb343fa7b5e3ce4d2e0bcd49805ade677abf5de1d42429d0c888bba",
    "drawGlassRaindrop": "9fa83b7bab02c0842db5afb43acf32ebd1ac5e708e6c760d0b8f36e650156931",
    "renderWings": "097b92ef7ee8c582c469740554750362f20dcaff2e0f631916df5066f1b2da47",
}
for name, expected in unchanged_methods.items():
    actual = hashlib.sha256(java_method(engine, name).encode()).hexdigest()
    assert actual == expected, f"Non-pilot renderer changed: {name} ({actual})"

assert 'Identifier.of("baroxvs", "textures/misc/avatar_glass.png")' in engine
assert 'RenderLayer.getEntityTranslucent(AVATAR_GLASS_TEXTURE)' in engine
assert 'RenderLayer.getEntityTranslucent(LIQUID_GLASS_TEXTURE)' in engine
assert 'drawAvatarGlassPrism(' in engine and 'drawGlassBoxShell(' not in engine
assert 'private static void emitAvatarGlassVertex(' in engine
assert 'SELF_GLASS_GRID_SEGMENTS = 8' in engine
assert 'selfGlassPosX = new double[SELF_GLASS_GRID_SIZE]' in engine
assert 'selfGlassNormalZ = new double[SELF_GLASS_GRID_SIZE]' in engine
assert 'double fresnel = Math.pow(1.0 - Math.max(0.0, facing), 2.65);' in engine
assert 'double specularPower = 12.0 + gloss * 52.0;' in engine
assert 'double sweepPhase = positiveMod(time * 0.018 + phaseOffset, 1.0);' in engine
avatar = java_method(engine, "renderLiquidGlassAvatar")
assert 'drawAvatarGlassPrism(' in avatar and 'drawBillboard(' not in avatar
prism = java_method(engine, "drawAvatarGlassPrism")
assert 'new Vec3d' not in prism and 'new double[' not in prism and 'new int[' not in prism
assert 'own + 1.0E-5 < otherA' in prism and 'own + 1.0E-5 < otherB' in prism

catalog = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(ids) == len(set(ids)) == 99, "module registrations changed"
assert 'styled("self_glass"' in catalog and 'group("player_glass"' in catalog

settings = (root / "src/main/java/com/baroxvs/client/gui/ModuleSettingsScreen.java").read_text(encoding="utf-8")
for token in [
    'addSlider("selfGlassRefraction", "Pearl transmission"',
    'addSlider("selfGlassEdge", "Fresnel edge"',
    'addSlider("selfGlassGloss", "Surface gloss"',
    'case "selfGlassRefraction" -> config.moduleValue("self_glass", "refraction"',
    'case "selfGlassEdge" -> config.moduleValue("self_glass", "edge"',
    'case "selfGlassGloss" -> config.moduleValue("self_glass", "gloss"',
    'case "selfGlassRefraction" -> config.setModuleValue("self_glass", "refraction"',
    'case "selfGlassEdge" -> config.setModuleValue("self_glass", "edge"',
    'case "selfGlassGloss" -> config.setModuleValue("self_glass", "gloss"',
]:
    assert token in settings, f"Missing Self Glass control: {token}"

png = (root / "src/main/resources/assets/baroxvs/textures/misc/avatar_glass.png").read_bytes()
assert png[:8] == b"\x89PNG\r\n\x1a\n"
assert struct.unpack(">II", png[16:24]) == (64, 64)
assert (root / "SELF_GLASS_MATERIAL_REDESIGN_v061.md").is_file()
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v061"
assert "BAROX VS v061" in (root / "BUILD_VERSION.txt").read_text(encoding="utf-8")
assert "BAROX-VS-v061.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=0.61.0" in (root / "gradle.properties").read_text(encoding="utf-8")
print("v061 Self Glass pilot checks passed: rounded optical mesh, dedicated material, tunable Fresnel/gloss/transmission; 99 modules and all non-pilot renderers preserved")
