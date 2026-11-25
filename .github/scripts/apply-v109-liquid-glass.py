from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
gui = root / "src/main/java/com/baroxvs/client/gui"
ui_path = gui / "Ui.java"
if not ui_path.is_file():
    raise SystemExit(f"Missing UI renderer: {ui_path}")
ui = ui_path.read_text(encoding="utf-8")


def method_span(source, name, required_prefix=""):
    pattern = re.compile(
        r"(?m)^[ \t]*(?P<sig>(?:public|private|protected)\s+(?:static\s+)?[^;{}]*?\b"
        + re.escape(name) + r"\s*\((?P<params>[^)]*)\)\s*)(?P<brace>\{)"
    )
    matches = [m for m in pattern.finditer(source)
               if not required_prefix or required_prefix in m.group("sig")]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {name} method, found {len(matches)}")
    m = matches[0]
    opening = m.start("brace")
    depth, state, escaped, i = 0, "code", False, opening
    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""
        if state == "code":
            if ch == '"': state = "string"
            elif ch == "'": state = "char"
            elif ch == "/" and nxt == "/": state = "line"; i += 1
            elif ch == "/" and nxt == "*": state = "block"; i += 1
            elif ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0: return m, opening, i
        elif state == "string":
            if escaped: escaped = False
            elif ch == "\\": escaped = True
            elif ch == '"': state = "code"
        elif state == "char":
            if escaped: escaped = False
            elif ch == "\\": escaped = True
            elif ch == "'": state = "code"
        elif state == "line":
            if ch == "\n": state = "code"
        elif state == "block":
            if ch == "*" and nxt == "/": state = "code"; i += 1
        i += 1
    raise RuntimeError(f"Unclosed method body: {name}")


def params_of(match):
    items = [x.strip() for x in match.group("params").split(",") if x.strip()]
    types, names = [], []
    for item in items:
        bits = re.sub(r"\s*=.*$", "", item).split()
        if len(bits) < 2: raise RuntimeError(f"Cannot parse parameter: {item}")
        names.append(bits[-1])
        types.append(" ".join(bits[:-1]))
    return types, names


def replace_body(source, name, body, prefix=""):
    match, opening, closing = method_span(source, name, prefix)
    return source[:opening + 1] + "\n" + body.strip("\n") + "\n" + source[closing:]


# Upgrade rounded UI surfaces while preserving each component's supplied opacity.
round_match, _, _ = method_span(ui, "roundRect", "static void")
_, rn = params_of(round_match)
round_body = r"""
        int width = __X2__ - __X1__;
        int height = __Y2__ - __Y1__;
        if (width <= 1 || height <= 1) return;
        int opacity = (__COLOR__ >>> 24) & 255;
        int radiusSafe = Math.max(1, Math.min(__RADIUS__, Math.min(width, height) / 2));

        int shadowAlpha = Math.min(54, Math.max(8, opacity / 6));
        roundRectShape(__CTX__, __X1__, __Y1__ + 2, __X2__, __Y2__ + 2, radiusSafe,
                (shadowAlpha << 24) | 0x020914);

        int rimAlpha = Math.min(92, Math.max(22, opacity / 2));
        roundRectShape(__CTX__, __X1__, __Y1__, __X2__, __Y2__, radiusSafe,
                (rimAlpha << 24) | 0xEAF8FF);

        int topColor = (opacity << 24) | (lerp(__COLOR__, 0xFFF8FDFF, 0.12f) & 0x00FFFFFF);
        int lowerColor = (opacity << 24) | (lerp(__COLOR__, 0xFF071A2A, 0.14f) & 0x00FFFFFF);
        roundRectGradient(__CTX__, __X1__ + 1, __Y1__ + 1, __X2__ - 1, __Y2__ - 1,
                Math.max(1, radiusSafe - 1), topColor, lowerColor);

        if (width >= 24 && height >= 12 && opacity >= 48) {
            int sheenAlpha = Math.min(74, Math.max(12, opacity / 4));
            int sheenHeight = Math.max(2, Math.min(5, height / 6));
            roundRectShape(__CTX__, __X1__ + Math.min(radiusSafe, 8), __Y1__ + 1,
                    __X2__ - Math.min(radiusSafe, 8), __Y1__ + 1 + sheenHeight,
                    Math.max(1, Math.min(3, radiusSafe / 3)), (sheenAlpha << 24) | 0xFFFFFF);
            int accent = __COLOR__ & 0x00FFFFFF;
            int lowerAlpha = Math.min(42, Math.max(8, opacity / 7));
            roundRectShape(__CTX__, __X1__ + radiusSafe, __Y2__ - 2, __X2__ - radiusSafe, __Y2__ - 1,
                    1, (lowerAlpha << 24) | accent);
        }

        if (width >= 96 && height >= 28 && opacity >= 80) {
            float sweep = (System.currentTimeMillis() % 11000L) / 11000.0f;
            int usable = Math.max(1, width - radiusSafe * 2 - 22);
            int shineX = __X1__ + radiusSafe + Math.round(usable * sweep);
            int shineWidth = Math.max(10, Math.min(24, width / 12));
            int shineAlpha = Math.min(48, Math.max(10, opacity / 5));
            roundRectShape(__CTX__, shineX, __Y1__ + 2,
                    Math.min(__X2__ - radiusSafe, shineX + shineWidth), __Y1__ + 4,
                    1, (shineAlpha << 24) | 0xFFFFFF);
        }
"""
for token, name in zip(
    ["__CTX__", "__X1__", "__Y1__", "__X2__", "__Y2__", "__RADIUS__", "__COLOR__"], rn
):
    round_body = round_body.replace(token, name)
ui = replace_body(ui, "roundRect", round_body, "static void")

# Reuse the richer, already-tested HUD glass material for large menu/settings panels.
flat_match, _, _ = method_span(ui, "flatPanel", "static void")
_, fn = params_of(flat_match)
flat_body = r"""
        if (__X2__ <= __X1__ || __Y2__ <= __Y1__) return;
        float phase = (System.currentTimeMillis() % 9000L) / 9000.0f;
        hudGlassPanel(__CTX__, __X1__, __Y1__, __X2__, __Y2__, __RADIUS__, __FILL__, __BORDER__, phase);
        glassFrame(__CTX__, __X1__, __Y1__, __X2__, __Y2__, __RADIUS__, __BORDER__, phase);
"""
for token, name in zip(
    ["__CTX__", "__X1__", "__Y1__", "__X2__", "__Y2__", "__RADIUS__", "__FILL__", "__BORDER__"], fn
):
    flat_body = flat_body.replace(token, name)
ui = replace_body(ui, "flatPanel", flat_body, "static void")

# This rim-only pass is safe to draw after the window body: it does not veil text.
if not re.search(r"public\s+static\s+void\s+glassFrame\s*\(", ui):
    match, _, _ = method_span(ui, "roundRect", "static void")
    types, _ = params_of(match)
    ctx_type = types[0]
    frame = f"""
    public static void glassFrame({ctx_type} ctx, int left, int top, int right, int bottom,
                                  int radius, int accent, float phase) {{
        int width = right - left;
        int height = bottom - top;
        if (width < 24 || height < 18) return;
        int r = Math.max(5, Math.min(radius, Math.min(width, height) / 2));
        float p = phase - (float) Math.floor(phase);
        int accentRgb = accent & 0x00FFFFFF;

        // Fresnel rim: cool white highlights on the upper/left edges, softer color below.
        roundRectShape(ctx, left + r, top + 1, right - r, top + 2, 1, 0x22F4FCFF);
        roundRectShape(ctx, left + 1, top + r, left + 2, bottom - r, 1, 0x19DDF5FF);
        roundRectShape(ctx, right - 2, top + r, right - 1, bottom - r, 1, 0x19FFFFFF | (accentRgb & 0));
        roundRectShape(ctx, right - 2, top + r, right - 1, bottom - r, 1, 0x19000000 | accentRgb);
        roundRectShape(ctx, left + r, bottom - 2, right - r, bottom - 1, 1, 0x12FFFFFF | accentRgb);

        // Slow specular sweep across the upper glass bevel.
        int span = Math.max(1, width - r * 2 - 28);
        int glintX = left + r + Math.round(span * p);
        int glintWidth = Math.max(14, Math.min(30, width / 8));
        roundRectGradient(ctx, glintX, top + 1, Math.min(right - r, glintX + glintWidth), top + 3,
                1, 0x38FFFFFF, 0x08FFFFFF);
    }}
"""
    ui = ui[:ui.rfind("}")] + frame + "\n" + ui[ui.rfind("}"):]

ui_path.write_text(ui, encoding="utf-8")

# The main-menu window gets a translucent cool film plus a moving Fresnel edge.
menu_path = gui / "BaroxMenuScreen.java"
if not menu_path.is_file(): raise SystemExit(f"Missing main menu source: {menu_path}")
menu = menu_path.read_text(encoding="utf-8")
m, _, closing = method_span(menu, "drawWindow")
_, mn = params_of(m)
ctx = mn[0]
rim = f"""
        Ui.roundRect({ctx}, this.frameX + 1, this.frameY + 1, this.frameX + this.frameW - 1,
                this.frameY + this.frameH - 1, 16, 0x18DDEEFF);
        Ui.glassFrame({ctx}, this.frameX, this.frameY, this.frameX + this.frameW,
                this.frameY + this.frameH, 16, 0xFFEAF8FF, this.animationTicks * 0.012f);
    """
menu = menu[:closing].rstrip() + rim + menu[closing:]
menu_path.write_text(menu, encoding="utf-8")

# ClickGUI has its own renderer, so it receives the same translucent film and themed rim.
click_path = gui / "ModuleClickGuiScreen.java"
if not click_path.is_file(): raise SystemExit(f"Missing ClickGUI source: {click_path}")
click = click_path.read_text(encoding="utf-8")
m, _, closing = method_span(click, "drawWindow")
_, cn = params_of(m)
ctx, theme = cn[0], cn[1]
rim = f"""
        Ui.roundRect({ctx}, this.panelX + 1, this.panelY + 1, this.panelX + this.panelW - 1,
                this.panelY + this.panelH - 1, this.s(14.0f), Ui.alpha({theme}.primary(), 22));
        Ui.glassFrame({ctx}, this.panelX, this.panelY, this.panelX + this.panelW,
                this.panelY + this.panelH, this.s(14.0f), {theme}.primary(), this.animationTime);
    """
click = click[:closing].rstrip() + rim + click[closing:]
click_path.write_text(click, encoding="utf-8")

# Bump only the JAR version; no sources or extra archives are released.
build = root / "build.gradle"
props = root / "gradle.properties"
if not all(p.is_file() for p in [build, props, root / "VERSION", root / "BUILD_VERSION.txt"]):
    raise SystemExit("Missing version metadata files")
build_text = build.read_text(encoding="utf-8")
if "BAROX-VS-v108.jar" not in build_text:
    raise SystemExit("Unexpected build.gradle baseline; v108 jar marker not found")
build.write_text(build_text.replace("BAROX-VS-v108.jar", "BAROX-VS-v109.jar"), encoding="utf-8")
prop_text = props.read_text(encoding="utf-8")
if "mod_version=1.08.0" not in prop_text:
    raise SystemExit("Unexpected Gradle version baseline")
props.write_text(prop_text.replace("mod_version=1.08.0", "mod_version=1.09.0"), encoding="utf-8")
(root / "VERSION").write_text("BAROX VS v109\n", encoding="utf-8")
(root / "BUILD_VERSION.txt").write_text("BAROX VS v109\n", encoding="utf-8")
print("v109 Liquid Glass surface and window treatments applied")
