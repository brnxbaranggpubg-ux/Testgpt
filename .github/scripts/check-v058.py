#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

root = Path(sys.argv[1])
catalog = (root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
ids = re.findall(r'(?:toggle|styled|cycle)\\("([a-z0-9_]+)"', catalog)
expected = ["dynamic_island", "ticker", "music_card", "lyric_flow", "target_card",
            "crosshair_ring", "crosshair_studio", "compass_bar", "toasts", "geometry_quality"]
assert len(ids) == len(set(ids)) == 99, f"expected 99 unique modules, got {len(ids)} declarations / {len(set(ids))} unique"
assert ids[70:80] == expected, f"registrations 71-80 changed: {ids[70:80]}"

hud = (root / "src/main/java/com/baroxvs/client/hud/HudRenderer.java").read_text(encoding="utf-8")
engine = (root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
assert "refreshPresentationSnapshots(mc)" in hud and "cachedTickerWords" in hud
assert "cachedLyricSnapshot = LyricFlowOverlay.at(MusicEngine.playbackPositionMs())" in hud
lyric_draw = hud[hud.find("private void drawLyricFlow"):hud.find("private void drawCoords")]
assert "LyricFlowOverlay.at(MusicEngine.playbackPositionMs())" not in lyric_draw
assert "new ArrayList<>(toasts)" not in hud and "cachedToasts" in hud
assert "cachedCompassBearing" in hud and "cachedTargetDistance" in hud
assert "private int qualitySegments(int base)" in engine
assert "private int qualityLayers(int base)" in engine
assert "qualitySegments(36)" in engine and "qualitySegments(64)" in engine and "globalDetail" in engine

lang = root / "src/main/resources/assets/baroxvs/lang"
data = {n: json.loads((lang / n).read_text(encoding="utf-8"))
        for n in ("en_us.json", "de_de.json", "tr_tr.json")}
keys = set(data["en_us.json"])
assert all(set(values) == keys for values in data.values()), "TR/DE/EN locale keys differ"
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v058"
assert "BAROX-VS-v058.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=0.58.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert (root / "HUD_PRESENTATION_GEOMETRY_REVIEW_v058.md").is_file()
print("v058 checks passed: registrations 71-80, 99 IDs, tick snapshots, bounded toasts, lyric lookup and global Geometry Detail wiring")
