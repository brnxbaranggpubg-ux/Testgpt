#!/usr/bin/env python3
"""Validate the v029 sky-render stability fallback and release metadata."""
from __future__ import annotations
import json, pathlib, sys

def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit("v029 check failed: " + message)

def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: check-v029.py <project-directory>")
    root = pathlib.Path(sys.argv[1])
    src = root / "src/main/java/com/baroxvs/client"
    sky = (src / "render/SkyboxEngine.java").read_text(encoding="utf-8")
    require("WorldRenderEvents" not in sky, "SkyboxEngine still registers a world-render event")
    require("WorldRenderEvents.BEFORE_ENTITIES" not in sky, "late terrain render hook still exists")
    for unsafe_api in ("VertexConsumer", "RenderLayer", "renderPhoto(", "renderPreset(", "NativeImageBackedTexture"):
        require(unsafe_api not in sky, f"custom world geometry path remains: {unsafe_api}")
    require("Vanilla sky protected" in sky, "safe vanilla fallback status missing")
    require("MAX_FILE_BYTES = 32L * 1024L * 1024L" in sky, "sky image size bound missing")
    require("try (NativeImage image" in sky, "NativeImage is not closed after validation")
    require("image.getWidth()" in sky and "image.getHeight()" in sky, "image dimensions are not validated")

    catalog = (src / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
    require("vanilla sky rendering untouched for stability" in catalog, "module description does not explain safe sky mode")
    menu = (src / "gui/BaroxMenuScreen.java").read_text(encoding="utf-8")
    require("AMBIENT FX: ACTIVE (VANILLA SKY SAFE)" in menu, "mobile atmosphere label is misleading")
    require("AMBIENT PRESETS · VANILLA SKY SAFE" in menu, "atmosphere preset label is misleading")

    lang_dir = root / "src/main/resources/assets/baroxvs/lang"
    lang = [json.loads((lang_dir / name).read_text(encoding="utf-8")) for name in ("en_us.json", "de_de.json", "tr_tr.json")]
    keys = set(lang[0])
    require(set(lang[1]) == keys and set(lang[2]) == keys, "language key sets differ")
    for values in lang:
        require("baroxvs.module.sky_mood.description" in values, "localized safe-mode description missing")

    build = (root / "build.gradle").read_text(encoding="utf-8")
    props = (root / "gradle.properties").read_text(encoding="utf-8")
    require("BAROX-VS-v029.jar" in build, "JAR filename is stale")
    require("mod_version=0.29.0" in props, "mod version is stale")
    require((root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v029", "VERSION marker is stale")
    print("v029 checks passed: sky world-render geometry removed, vanilla fallback protected, image validation bounded, TR/DE/EN descriptions and release metadata valid")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
