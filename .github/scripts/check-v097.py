#!/usr/bin/env python3
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
base = root / "src/main/java/com/baroxvs/client"
engine = (base / "cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
cloth = (base / "cosmetic/CapeClothSimulation.java").read_text(encoding="utf-8")
catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
config = (base / "config/BaroxConfig.java").read_text(encoding="utf-8")
sky = (base / "render/SkyboxEngine.java").read_text(encoding="utf-8")
skin_mixin = (base / "mixin/LocalSkinMixin.java").read_text(encoding="utf-8")

ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(ids) == len(set(ids)) == 99, f"module declarations changed: {len(ids)} / {len(set(ids))} unique"
for module_id in ("cape", "sky_studio", "custom_sky", "sky_time_cycle", "sky_aurora", "sky_stars",
                  "sky_fog", "sky_horizon_glow", "sky_nebula", "sky_meteors", "sky_constellations"):
    assert ids.count(module_id) == 1, f"module ID {module_id} must remain unique"
    assert f'"{module_id}"' in config, f"configuration key {module_id} was lost"

assert "public static final int COLUMNS = 10;" in cloth
assert "public static final int ROWS = 16;" in cloth
assert "0.625 * clothScale" in cloth and "1.00 * clothScale" in cloth
assert "-0.0058" in cloth and "vanillaCapeOffset" in cloth
assert "prevBodyYaw" in engine and "player.bodyYaw" in engine
assert "player.capeX - player.getX()" in engine
assert "capeBack.multiply(0.14)" in engine
assert "CAPE_LOGO_TEXTURE" in engine and "renderCapeSponsorLogo" in engine
assert "getEntityTranslucent(CAPE_LOGO_TEXTURE)" in engine
assert "cape_logo.png" in engine
assert "original.capeTexture()" in skin_mixin and "customCape ? null" in skin_mixin
assert "Fifteen classic rectangular capes" in catalog

logo_start = engine.index("private static void renderCapeSponsorLogo(")
logo_end = engine.index("private static int capeMotifColor(", logo_start)
logo_code = engine[logo_start:logo_end]
for token in ("grid[row][col]", "normal.multiply(0.0045)", "u0", "v0", "OverlayTexture.DEFAULT_UV",
              "LightmapTextureManager.MAX_LIGHT_COORDINATE"):
    assert token in logo_code, f"cape sponsor mapping missing {token}"
assert (root / "src/main/resources/assets/baroxvs/textures/misc/cape_logo.png").is_file(), "sponsor logo texture missing"

assert "getDebugQuads()" not in sky
assert "RenderLayer.getEntityTranslucent(SKY_WHITE_TEXTURE)" in sky
emit = sky[sky.index("private static void emitColorVertex("):sky.index("private static float[][] makePhotoMesh(")]
for token in (".texture(0.5f, 0.5f)", ".overlay(OverlayTexture.DEFAULT_UV)",
              ".light(LightmapTextureManager.MAX_LIGHT_COORDINATE)", ".normal(matrix"):
    assert token in emit, f"Sky vertex format missing {token}"
assert "boolean presetActive = cfg.isOn(\"sky_studio\")" in sky
assert "drawPresetAtmosphere(matrices, consumers, cfg, dayTime, worldTime, night)" in sky
assert "boolean anyLayer = presetActive || customActive || cfg.isOn(\"sky_aurora\")" in sky
assert "if (cfg == null || (!cfg.isOn(\"sky_studio\") && !cfg.isOn(\"sky_time_cycle\"))) return vanilla;" in sky
assert 'client.world == null || !cfg.isOn("sky_fog")' in sky
assert "Eight visible sky presets" in catalog

assert "BAROX-VS-v097.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=0.97.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v097"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v097"
assert (root / "RENDER_REPAIR_v097.md").is_file()
print("v097 checks passed: classic cape physics, sponsor decal, working Sky Studio render pipeline and 99 unique module IDs")
