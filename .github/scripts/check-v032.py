#!/usr/bin/env python3
"""Validate BAROX VS v032 sky/ambience recode and v031 compatibility."""
from __future__ import annotations
import json
import pathlib
import re
import sys


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit("v032 check failed: " + message)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: check-v032.py <project-directory>")
    root = pathlib.Path(sys.argv[1])
    base = root / "src/main/java/com/baroxvs/client"
    catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
    sky = (base / "render/SkyboxEngine.java").read_text(encoding="utf-8")
    sky_mixin = (base / "mixin/SkyRenderingMixin.java").read_text(encoding="utf-8")
    fog_mixin = (base / "mixin/BackgroundRendererMixin.java").read_text(encoding="utf-8")
    menu = (base / "gui/BaroxMenuScreen.java").read_text(encoding="utf-8")
    settings = (base / "gui/ModuleSettingsScreen.java").read_text(encoding="utf-8")
    for helper in ("drawWindow(", "drawSidebar(", "drawHeader(", "drawPage(", "drawFooter(",
                   "drawMobileColorStudio(", "drawMobileSettings(", "openModuleSettings("):
        require(helper in menu, f"existing ClickGUI helper regressed: {helper}")
    require(".next()" not in sky, "VertexConsumer.next() is unsupported on the 1.21.4 target")

    ids = re.findall(r'(?:toggle|styled|cycle)\("([^\"]+)', catalog)
    require(len(ids) == 92, f"expected 92 module IDs, found {len(ids)}")
    require(len(ids) == len(set(ids)), "module IDs are not unique")
    for module_id in ("sky_studio", "custom_sky", "sky_time_cycle", "sky_aurora", "sky_stars",
                      "sky_fog", "sky_horizon_glow", "sky_nebula", "sky_meteors", "sky_constellations"):
        require(f'"{module_id}"' in catalog, f"sky module {module_id} missing")
    for method in ("drawPhotoPanorama", "drawAurora", "drawExtraStars", "drawNebula",
                   "drawMeteorTrails", "drawConstellations", "drawHorizonGlow", "tintSkyChannel", "tintFogColor"):
        require(f"{method}(" in sky, f"sky renderer missing {method}")
    for token in ("PHOTO_MESH = makePhotoMesh()", "makePhotoMesh()", "destroyTexture(PHOTO_SKY)",
                  "MAX_FILE_BYTES = 16L * 1024L * 1024L", "MIN_WIDTH = 256", "MIN_HEIGHT = 128",
                  "MAX_WIDTH = 4096", "MAX_HEIGHT = 2048", "Math.abs(ratio - 2.0d)",
                  'resolve("sky.png")', 'moduleValue("custom_sky", "yaw"',
                  'moduleValue("custom_sky", "brightness"', 'moduleValue("sky_studio", "saturation"'):
        require(token in sky, f"SkyboxEngine constraint/settings missing {token}")
    require("WorldRenderEvents.register" not in sky and "WorldRenderEvents.BEFORE_ENTITIES" not in sky,
            "late world-render sky hook must not be used")
    require("client.world.getTime(" in sky, "local visual timing should read world time only")
    require("setTimeOfDay" not in sky and "setWeather" not in sky and "sendPacket" not in sky,
            "sky visuals must not mutate world/server state")
    require("getFogColor" not in sky and "applyFog" not in sky,
            "fog hook belongs in the dedicated fog mixin")

    for token in ('@Mixin(SkyRendering.class)', 'renderSky(FFF)V', 'renderCelestialBodies',
                  'SkyboxEngine.tintSkyChannel', 'SkyboxEngine.renderCelestial'):
        require(token in sky_mixin, f"sky Mixin missing {token}")
    for token in ('@Mixin(BackgroundRenderer.class)', 'getFogColor', 'CameraSubmersionType.NONE',
                  'SkyboxEngine.tintFogColor'):
        require(token in fog_mixin, f"fog Mixin missing {token}")
    require("WorldRenderEvents" not in sky_mixin, "sky Mixin should use SkyRendering, not late world events")

    for module_id in ("sky_nebula", "sky_meteors", "sky_constellations"):
        require(f'"{module_id}"' in menu, f"Atmosphere page does not expose {module_id}")
    for control in ("photoYaw", "photoBrightness", "skySaturation", "nebulaOpacity", "nebulaSpeed",
                    "meteorRate", "constellationOpacity"):
        require(f'"{control}"' in settings, f"per-module settings missing {control}")
    for control in ("skyTint", "skyBrightness", "skySaturation", "photoYaw", "photoBrightness",
                    "nebulaOpacity", "nebulaSpeed", "meteorRate", "constellationOpacity"):
        require(f'case "{control}"' in settings, f"settings persistence missing {control}")

    mixin_json = json.loads((root / "src/main/resources/baroxvs.mixins.json").read_text(encoding="utf-8"))
    require("SkyRenderingMixin" in mixin_json["client"], "SkyRenderingMixin not registered")
    require("BackgroundRendererMixin" in mixin_json["client"], "BackgroundRendererMixin not registered")
    fabric = json.loads((root / "src/main/resources/fabric.mod.json").read_text(encoding="utf-8"))
    require("baroxvs.mixins.json" in fabric.get("mixins", []), "BAROX mixin config missing from Fabric metadata")

    lang_dir = root / "src/main/resources/assets/baroxvs/lang"
    names = ("en_us.json", "de_de.json", "tr_tr.json")
    languages = [json.loads((lang_dir / name).read_text(encoding="utf-8")) for name in names]
    keys = set(languages[0])
    require(all(set(doc) == keys for doc in languages[1:]), "locale key sets differ")
    expected = ("baroxvs.module.sky_nebula", "baroxvs.module.sky_nebula.description",
                "baroxvs.module.sky_meteors", "baroxvs.module.sky_meteors.description",
                "baroxvs.module.sky_constellations", "baroxvs.module.sky_constellations.description")
    for name, doc in zip(names, languages):
        for key in expected:
            require(key in doc and doc[key], f"{name} missing {key}")

    require((root / "SKY_STUDIO_v032.md").is_file(), "Sky Studio guide is missing")
    require((root / "KIMIKO_REFERENCE_AUDIT_v032.md").is_file(), "reference audit is missing")
    report = (root / "KIMIKO_REFERENCE_AUDIT_v032.md").read_text(encoding="utf-8")
    for term in ("Ambience", "FogBlur", "WorldBorderCustomSkyMixin", "aurora.fsh", "starfall.fsh",
                 "No Kimiko class bytecode", "1.21.11", "Sky Studio", "Meteor Trails", "Constellations"):
        require(term.lower() in report.lower(), f"reference audit omits {term}")

    build = (root / "build.gradle").read_text(encoding="utf-8")
    props = (root / "gradle.properties").read_text(encoding="utf-8")
    require("BAROX-VS-v032.jar" in build, "JAR filename is stale")
    require("mod_version=0.32.0" in props, "mod version is stale")
    require((root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v032", "VERSION marker is stale")
    require((root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v032", "BUILD_VERSION marker is stale")

    print("v032 checks passed: 92 modules, dedicated 1.21.4 sky/fog mixins, capped local panorama, seven animated sky layers, settings persistence, TR/DE/EN parity and v031 lineage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
