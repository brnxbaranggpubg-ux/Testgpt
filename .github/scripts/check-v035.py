#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path
root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
java = root / "src/main/java/com/baroxvs/client"
catalog = (java / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
hud = (java / "hud/HudRenderer.java").read_text(encoding="utf-8")
editor = (java / "gui/HudEditorScreen.java").read_text(encoding="utf-8")
ids = re.findall(r'\\b(?:toggle|styled|cycle)\\("([a-z0-9_]+)"', catalog)
assert len(ids) == 97, f"expected 97 modules, got {len(ids)}"
assert len(ids) == len(set(ids)), "module ids must be unique"
assert 'styled("biome_toast", "Biome Discovery"' in catalog
for marker in ("updateBiomeDiscovery(p)", "private void updateBiomeDiscovery(PlayerEntity player)",
    "private void drawBiomeToast(", 'cfg.isOn("biome_toast")', "biomeToastCooldowns",
    "Text.translatable(translationKey)", "20_000L", "3_800L", "Ui.easeInOutCubic"):
    assert marker in hud, f"missing Biome Discovery marker: {marker}"
assert '"biome_toast" -> true' in editor
lang = root / "src/main/resources/assets/baroxvs/lang"
locales = {name: json.loads((lang / f"{name}.json").read_text(encoding="utf-8")) for name in ("en_us", "de_de", "tr_tr")}
keys = set(locales["en_us"])
assert all(set(data) == keys for data in locales.values()), "locale keys differ"
for key in ("baroxvs.module.biome_toast", "baroxvs.module.biome_toast.description", "baroxvs.hud.biome_discovered"):
    assert key in keys, f"missing locale key {key}"
assert locales["tr_tr"]["baroxvs.module.biome_toast"] == "Yeni Biyom"
assert "BAROX-VS-v035.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=0.35.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v035"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v035"
assert "# BAROX VS — v035" in (root / "README.md").read_text(encoding="utf-8")
assert (root / "BIOME_DISCOVERY_v035.md").is_file()
print("v035 checks passed: 97 modules, Biome Discovery update/cooldown/animation, HUD Studio selection and TR/DE/EN locale parity")
