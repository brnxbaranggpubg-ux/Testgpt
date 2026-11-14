#!/usr/bin/env python3
"""Validate BAROX VS v028 local LRC playback synchronization and HUD wiring."""
from __future__ import annotations
import json
import pathlib
import re
import subprocess
import sys
import tempfile


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("v028 check failed: " + message)


def check_lrc_runtime(root: pathlib.Path) -> None:
    source = root / "src/main/java/com/baroxvs/client/hud/LyricFlowOverlay.java"
    with tempfile.TemporaryDirectory(prefix="barox-v028-lrc-") as temp:
        tmp = pathlib.Path(temp)
        stub = tmp / "stub/net/fabricmc/loader/api/FabricLoader.java"
        stub.parent.mkdir(parents=True)
        stub.write_text("""package net.fabricmc.loader.api;
import java.nio.file.Path;
public final class FabricLoader {
    private static final FabricLoader INSTANCE = new FabricLoader();
    public static FabricLoader getInstance() { return INSTANCE; }
    public Path getConfigDir() { return Path.of(System.getProperty("barox.test.config")); }
}
""", encoding="utf-8")
        runner = tmp / "LrcRuntimeCheck.java"
        runner.write_text("""import com.baroxvs.client.hud.LyricFlowOverlay;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.charset.StandardCharsets;
public final class LrcRuntimeCheck {
    public static void main(String[] args) throws Exception {
        Path config = Path.of(args[0]);
        System.setProperty("barox.test.config", config.toString());
        Path file = config.resolve("baran3120/captions.lrc");
        Files.createDirectories(file.getParent());
        Files.writeString(file, "[00:02.50]Own line A\\n[00:05.00][00:07.00]Own line B\\n[offset:-500]\\n", StandardCharsets.UTF_8);
        LyricFlowOverlay.tick();
        var early = LyricFlowOverlay.at(1000);
        var middle = LyricFlowOverlay.at(3000);
        var late = LyricFlowOverlay.at(5000);
        if (early.current() != null || early.next() == null || early.next().atMs() != 2000) throw new AssertionError("early/offset parse");
        if (middle.current() == null || !middle.current().text().equals("Own line A") || Math.abs(middle.progress() - 0.4f) > 0.001f) throw new AssertionError("middle timeline");
        if (late.current() == null || late.current().atMs() != 4500 || late.next() == null || late.next().atMs() != 6500) throw new AssertionError("multiple timestamp parse");
        System.out.println("LRC runtime tests passed");
    }
}
""", encoding="utf-8")
        classes = tmp / "classes"
        classes.mkdir()
        command = [
            "javac", "-encoding", "UTF-8", "-d", str(classes),
            str(stub), str(source), str(runner),
        ]
        compiled = subprocess.run(command, capture_output=True, text=True)
        require(compiled.returncode == 0, "LRC parser javac failed: " + compiled.stderr[-3000:])
        config = tmp / "config"
        executed = subprocess.run(
            ["java", "-cp", str(classes), "LrcRuntimeCheck", str(config)],
            capture_output=True, text=True,
        )
        require(executed.returncode == 0, "LRC runtime test failed: " + executed.stdout + executed.stderr)
        require("LRC runtime tests passed" in executed.stdout, "LRC runtime test confirmation missing")


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: check-v028.py <project-directory>")
    root = pathlib.Path(sys.argv[1])
    base = root / "src/main/java/com/baroxvs/client"
    catalog = (base / "cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
    music = (base / "audio/MusicEngine.java").read_text(encoding="utf-8")
    overlay = (base / "hud/LyricFlowOverlay.java").read_text(encoding="utf-8")
    hud = (base / "hud/HudRenderer.java").read_text(encoding="utf-8")

    ids = re.findall(r'(?:toggle|styled|cycle)\("([^\\"]+)"', catalog)
    require(len(ids) == 79, f"expected 79 modules after Lyric Flow, found {len(ids)}")
    require(len(ids) == len(set(ids)), "module IDs are not unique")
    require('toggle("lyric_flow", "Lyric Flow"' in catalog, "Lyric Flow HUD module is missing")
    require('resolve("baran3120").resolve("captions.lrc")' in overlay, "local captions path is incorrect")
    require("MAX_FILE_BYTES = 256 * 1024" in overlay and "MAX_CUES = 2500" in overlay,
            "local LRC resource limits missing")
    for token in ("TIMESTAMP", "OFFSET", "public static List<Cue> parse", "public static Snapshot at", "Comparator.comparingLong"):
        require(token in overlay, f"LRC parser feature missing: {token}")
    for token in ("playbackSampleFrames", "playbackSampleRate", "playbackPositionMs()", "decoded.getBufferLength() / channels"):
        require(token in music, f"PCM-based playhead feature missing: {token}")
    require("LyricFlowOverlay.tick()" in hud and 'cfg.isOn("lyric_flow")' in hud and "drawLyricFlow" in hud,
            "HUD render/tick wiring incomplete")
    require('"dev.lyricsflow' not in "".join(p.read_text(encoding="utf-8", errors="ignore")
            for p in (root / "src/main/java").rglob("*.java")), "third-party LyricsFlow package was copied")

    language_dir = root / "src/main/resources/assets/baroxvs/lang"
    langs = [json.loads((language_dir / name).read_text(encoding="utf-8"))
             for name in ("en_us.json", "de_de.json", "tr_tr.json")]
    require(set(langs[0]) == set(langs[1]) == set(langs[2]), "language key sets differ")
    for data in langs:
        for key in ("baroxvs.module.lyric_flow", "baroxvs.hud.lyric_flow.title",
                    "baroxvs.hud.lyric_flow.waiting", "baroxvs.hud.lyric_flow.empty"):
            require(key in data, f"missing translation {key}")

    require("mod_version=0.28.0" in (root / "gradle.properties").read_text(encoding="utf-8"),
            "gradle.properties version is stale")
    require("BAROX-VS-v028.jar" in (root / "build.gradle").read_text(encoding="utf-8"),
            "remapped JAR filename is stale")
    require((root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v028",
            "VERSION marker is stale")
    require((root / "LYRIC_FLOW_v028.md").is_file(), "Lyric Flow setup documentation is missing")
    check_lrc_runtime(root)
    print("v028 checks passed: 79 modules, PCM-synced local LRC overlay, parser runtime and TR/DE/EN translations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
