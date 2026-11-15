#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("project")
java_root = root / "src/main/java"
java_files = list(java_root.rglob("*.java"))
sources = {p: p.read_text(encoding="utf-8") for p in java_files}
all_java = "\n".join(sources.values())
engine = sources[root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java"]
catalog = sources[root / "src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java"]
settings = sources[root / "src/main/java/com/baroxvs/client/gui/ModuleSettingsScreen.java"]
config = sources[root / "src/main/java/com/baroxvs/client/config/BaroxConfig.java"]

for forbidden in (
    "class Spark", "class Particle", "List<Spark>", "new Spark(",
    "ParticleTypes", "ParticleEffect", "addParticle(", "spawnParticle(",
    "emitCosmetics(", "emitAudioVisuals(", "renderSparks(",
    "updateAmbientBodies(", "repelAmbientBodies(", "particleCount()",
    "particleFrequency", "musicParticleRate", "ambientBodies",
):
    assert forbidden not in all_java, f"forbidden particle path remains: {forbidden}"

assert "drawButterflyMesh(" in engine
assert "renderMusicVisualizerGeometry(" in engine
assert "renderAttachedGeometryEffects(" in engine
assert "renderAmbientGeometry(" in engine
assert "renderJumpRipples(" in engine
assert "private static void ribbon(" in engine
assert "private static void drawRing(" in engine
assert "drawButterflyParticle(" not in engine
assert "supportsParticleTuning" not in settings
assert "Particle" not in settings and "particle" not in settings
assert "ambient_forms" in catalog and "sky_mood" in catalog
assert "geometry renderer status" in catalog
assert not (java_root / "com/baroxvs/client/cosmetic/CosmeticEngine.java.orig").exists()

lang = root / "src/main/resources/assets/baroxvs/lang"
locales = {name: json.loads((lang / f"{name}.json").read_text(encoding="utf-8"))
           for name in ("en_us", "de_de", "tr_tr")}
keys = set(locales["en_us"])
assert all(set(data) == keys for data in locales.values()), "locale keys differ"

module_ids = re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"', catalog)
assert len(module_ids) == len(set(module_ids)), "duplicate module id"
assert len(module_ids) == 97, f"expected 97 modules, got {len(module_ids)}"

assert "BAROX-VS-v036.jar" in (root / "build.gradle").read_text(encoding="utf-8")
assert "mod_version=0.36.0" in (root / "gradle.properties").read_text(encoding="utf-8")
assert (root / "VERSION").read_text(encoding="utf-8").strip() == "BAROX VS v036"
assert (root / "BUILD_VERSION.txt").read_text(encoding="utf-8").strip() == "BAROX VS v036"
assert "# BAROX VS — v036" in (root / "README.md").read_text(encoding="utf-8")
assert (root / "PARTICLELESS_RENDERER_v036.md").is_file()
print("v036 checks passed: no particle classes, emitters, API calls or particle settings; 97 modules; mesh-only replacements; TR/DE/EN locale parity")
