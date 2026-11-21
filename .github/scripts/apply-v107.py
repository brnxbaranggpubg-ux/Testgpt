from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
java = root / "src/main/java/com/baroxvs/client"


def read(rel: str) -> str:
    path = java / rel
    if not path.is_file():
        raise SystemExit(f"v107: required source file missing: {path}")
    return path.read_text(encoding="utf-8")


def write(rel: str, text: str) -> None:
    (java / rel).write_text(text, encoding="utf-8")


def replace_method(source: str, signature: str, replacement: str) -> str:
    start = source.find(signature)
    if start < 0:
        raise SystemExit(f"v107: method signature not found: {signature}")
    brace = source.find("{", start + len(signature))
    if brace < 0:
        raise SystemExit(f"v107: method body not found: {signature}")

    depth = 0
    i = brace
    in_string = False
    in_char = False
    in_line_comment = False
    in_block_comment = False
    escaped = False
    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""
        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
        elif in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
                i += 1
        elif in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        elif in_char:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == "'":
                in_char = False
        elif ch == "/" and nxt == "/":
            in_line_comment = True
            i += 1
        elif ch == "/" and nxt == "*":
            in_block_comment = True
            i += 1
        elif ch == '"':
            in_string = True
        elif ch == "'":
            in_char = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                return source[:start] + replacement + source[end:]
        i += 1
    raise SystemExit(f"v107: unterminated method body: {signature}")


# 1) Put every module switch behind one group-aware state transition.
client_path = java / "BaroxVsClient.java"
client = client_path.read_text(encoding="utf-8")
client = replace_method(
    client,
    "public static void setModuleEnabled(String id, boolean enabled)",
    '''public static void setModuleEnabled(String id, boolean enabled) {
        setModuleEnabled(CONFIG, id, enabled);
    }

    /**
     * The single module-state entry point for all menus, chat commands and keybinds.
     * Parent-off always clears children; enabling a child opens its parent; disabling
     * the final active child closes the parent. Re-enabling a parent restores catalog
     * defaults for its child controls so the group does not look mysteriously empty.
     */
    public static void setModuleEnabled(BaroxConfig config, String id, boolean enabled) {
        if (config == null || id == null || id.isBlank()) return;
        ModuleCatalog.Module module = ModuleCatalog.byId(id);
        if (module == null || module.kind() != ModuleCatalog.Kind.TOGGLE) return;

        List<ModuleCatalog.Module> children = ModuleCatalog.childrenOf(id);
        String parent = ModuleCatalog.parentOf(id);

        if (!enabled) {
            config.setOn(id, false);
            for (ModuleCatalog.Module child : children) config.setOn(child.id(), false);
            if (parent != null && ModuleCatalog.childrenOf(parent).stream()
                    .noneMatch(child -> config.isOn(child.id()))) {
                config.setOn(parent, false);
            }
            return;
        }

        if (parent != null) config.setOn(parent, true);

        // These two head models occupy the same attachment point.
        if ("headwear".equals(id)) config.setOn("chinese_hat", false);
        else if ("chinese_hat".equals(id)) config.setOn("headwear", false);

        config.setOn(id, true);

        if (!children.isEmpty()) {
            boolean hasActiveChild = children.stream().anyMatch(child -> config.isOn(child.id()));
            if (!hasActiveChild) {
                for (ModuleCatalog.Module child : children) {
                    if (child.defaultOn()) config.setOn(child.id(), true);
                }
                if ("player_glass".equals(id)) config.setOn("self_glass", true);
                else if ("head_accessories".equals(id)) config.setOn("headwear", true);
            }
        }
    }'''
)
client_path.write_text(client, encoding="utf-8")

# 2) Repair group ownership in persisted configs and named HUD profiles.
config_path = java / "config/BaroxConfig.java"
config = config_path.read_text(encoding="utf-8")
if "private static void normalizeModuleGroups(" not in config:
    helper = '''    /** Repairs saved child switches whose parent was left off by an older menu path. */
    private static void normalizeModuleGroups(Map<String, Boolean> moduleStates) {
        if (moduleStates == null) return;

        // Preserve an explicitly enabled child by opening its owning parent.
        for (ModuleCatalog.Module module : ModuleCatalog.all()) {
            String parent = ModuleCatalog.parentOf(module.id());
            if (parent != null && Boolean.TRUE.equals(moduleStates.get(module.id()))) {
                moduleStates.put(parent, true);
            }
        }

        // An explicitly disabled parent is authoritative when no enabled child asked
        // to keep the group alive. Clear stale child states so no screen shows orphans.
        for (ModuleCatalog.Module parent : ModuleCatalog.all()) {
            if (ModuleCatalog.childrenOf(parent.id()).isEmpty()) continue;
            if (Boolean.FALSE.equals(moduleStates.get(parent.id()))) {
                for (ModuleCatalog.Module child : ModuleCatalog.childrenOf(parent.id())) {
                    moduleStates.put(child.id(), false);
                }
            }
        }
    }

'''
    anchor = "    public void sanitize() {"
    if anchor not in config:
        raise SystemExit("v107: BaroxConfig.sanitize anchor missing")
    config = config.replace(anchor, helper + anchor, 1)

# Retire the old performance migration's mass-disable list; its marker is still advanced
# so old files are saved, but missing module keys continue to use ModuleCatalog defaults.
start = config.find("        if (performanceVersion < 1) {")
if start < 0:
    raise SystemExit("v107: performanceVersion migration block missing")
brace = config.find("{", start)
depth = 0
end = None
for i in range(brace, len(config)):
    if config[i] == "{": depth += 1
    elif config[i] == "}":
        depth -= 1
        if depth == 0:
            end = i + 1
            break
if end is None:
    raise SystemExit("v107: unterminated performanceVersion migration")
new_migration = '''        if (performanceVersion < 1) {
            // v107: preserve existing selections. Missing config keys fall back to
            // ModuleCatalog defaults; a performance migration must never mass-disable them.
            performanceVersion = 1;
        }'''
config = config[:start] + new_migration + config[end:]

# Run the normalizer after migrations have completed, for both the active config and profiles.
normalize_marker = "        if (tickerText == null) tickerText = \"\";"
normalization = '''        normalizeModuleGroups(modules);
        for (HudProfile profile : hudProfiles.values()) {
            if (profile != null) {
                if (profile.modules == null) profile.modules = new HashMap<>();
                normalizeModuleGroups(profile.modules);
            }
        }
'''
if normalize_marker not in config:
    raise SystemExit("v107: final sanitize anchor missing")
if "normalizeModuleGroups(modules);" not in config:
    config = config.replace(normalize_marker, normalization + normalize_marker, 1)
config_path.write_text(config, encoding="utf-8")

# 3) Update the Visual Studio, HUD editor and in-game chat command paths.
menu_path = java / "gui/BaroxMenuScreen.java"
menu = menu_path.read_text(encoding="utf-8")
menu = menu.replace('cfg.setOn("wings", true)', 'BaroxVsClient.setModuleEnabled(cfg, "wings", true)')
menu = menu.replace('cfg.setOn("sky_studio", true)', 'BaroxVsClient.setModuleEnabled(cfg, "sky_studio", true)')
menu = menu.replace('cfg.setOn(id, !cfg.isOn(id))', 'BaroxVsClient.setModuleEnabled(cfg, id, !cfg.isOn(id))')
menu_path.write_text(menu, encoding="utf-8")

hud_path = java / "gui/HudEditorScreen.java"
hud = hud_path.read_text(encoding="utf-8")
if "import com.baroxvs.client.BaroxVsClient;" not in hud:
    hud = hud.replace("package com.baroxvs.client.gui;\n", "package com.baroxvs.client.gui;\n\nimport com.baroxvs.client.BaroxVsClient;\n", 1)
hud = hud.replace('config.setOn(module.id(), !config.isOn(module.id()))',
                  'BaroxVsClient.setModuleEnabled(config, module.id(), !config.isOn(module.id()))')
hud_path.write_text(hud, encoding="utf-8")

commands_path = java / "HudChatCommands.java"
commands = commands_path.read_text(encoding="utf-8")
commands = commands.replace("config.setOn(id, enabled);", "BaroxVsClient.setModuleEnabled(config, id, enabled);")
commands_path.write_text(commands, encoding="utf-8")

# 4) Keep Cloth Config's Reset values sourced from the same module catalogue.
cloth_path = java / "gui/BaroxClothConfigScreen.java"
cloth = cloth_path.read_text(encoding="utf-8")
if "import com.baroxvs.client.BaroxVsClient;" not in cloth:
    cloth = cloth.replace("package com.baroxvs.client.gui;\n", "package com.baroxvs.client.gui;\n\nimport com.baroxvs.client.BaroxVsClient;\n", 1)
if "import com.baroxvs.client.cosmetic.ModuleCatalog;" not in cloth:
    cloth = cloth.replace("import com.baroxvs.client.config.BaroxConfig;\n",
                          "import com.baroxvs.client.config.BaroxConfig;\nimport com.baroxvs.client.cosmetic.ModuleCatalog;\n", 1)
helper = '''    private static boolean catalogDefault(String id) {
        ModuleCatalog.Module module = ModuleCatalog.byId(id);
        return module != null && module.defaultOn();
    }

    private static int catalogStyleDefault(String id) {
        ModuleCatalog.Module module = ModuleCatalog.byId(id);
        return module == null ? 0 : module.defaultStyle();
    }

'''
if "private static boolean catalogDefault(" not in cloth:
    anchor = "    public static Screen create(Screen parent, BaroxConfig config) {"
    if anchor not in cloth:
        raise SystemExit("v107: Cloth Config create anchor missing")
    cloth = cloth.replace(anchor, helper + anchor, 1)

for module_id in ("wings", "head_accessories", "cape", "pet", "aura", "ambient_forms", "liquid_rain", "sky_studio"):
    cloth = re.sub(
        r'\.setDefaultValue\((?:true|false)\)\.setSaveConsumer\(v -> config\.setOn\("'
        + re.escape(module_id) + r'", v\)\)',
        '.setDefaultValue(catalogDefault("' + module_id + '")).setSaveConsumer(v -> BaroxVsClient.setModuleEnabled(config, "'
        + module_id + '", v))',
        cloth,
    )
cloth = cloth.replace('.setDefaultValue(1).setTextGetter(v -> Text.translatable(switch (v)',
                      '.setDefaultValue(catalogStyleDefault("geometry_quality")).setTextGetter(v -> Text.translatable(switch (v)')
cloth_path.write_text(cloth, encoding="utf-8")

print("v107 applied: group-aware module setter, group-state migration, non-destructive performance migration, catalogue-driven Cloth defaults")

# Version the reconstructed project itself; the workflow builds this tree, not the repository root.
build_path = root / "build.gradle"
build = build_path.read_text(encoding="utf-8")
if "BAROX-VS-v106.jar" in build:
    build = build.replace("BAROX-VS-v106.jar", "BAROX-VS-v107.jar")
elif "BAROX-VS-v107.jar" not in build:
    raise SystemExit("v107: expected v106 or v107 archive name in build.gradle")
build_path.write_text(build, encoding="utf-8")

gradle_path = root / "gradle.properties"
gradle = gradle_path.read_text(encoding="utf-8")
gradle = gradle.replace("mod_version=1.06.0", "mod_version=1.07.0")
if "mod_version=1.07.0" not in gradle:
    raise SystemExit("v107: could not set Gradle mod_version")
gradle_path.write_text(gradle, encoding="utf-8")
(root / "VERSION").write_text("BAROX VS v107\n", encoding="utf-8")
(root / "BUILD_VERSION.txt").write_text("BAROX VS v107\n", encoding="utf-8")