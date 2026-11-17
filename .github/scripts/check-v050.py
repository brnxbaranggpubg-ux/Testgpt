#!/usr/bin/env python3
from pathlib import Path
import re, sys
root=Path(sys.argv[1]).resolve()
engine=(root/"src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java").read_text(encoding="utf-8")
catalog=(root/"src/main/java/com/baroxvs/client/cosmetic/ModuleCatalog.java").read_text(encoding="utf-8")
settings=(root/"src/main/java/com/baroxvs/client/gui/ModuleSettingsScreen.java").read_text(encoding="utf-8")
config=(root/"src/main/java/com/baroxvs/client/config/BaroxConfig.java").read_text(encoding="utf-8")
expected=["aura","aura_pulse","glint","music_aura_sync","orbit_stars","halo","player_glass","hand_glow","arm_glow","held_item_glow"]
static=catalog[catalog.index("    static {"):catalog.index("    /** Returns structural errors")]
registered=re.findall(r'\b(?:toggle|styled|cycle)\("([a-z0-9_]+)"',static)
assert registered[:10]==expected,registered[:10]
assert len(registered)==99,len(registered)
assert 'group("aura", "aura_pulse", "music_aura_sync")' in catalog
assert 'group("player_glass", "hand_glow", "arm_glow", "held_item_glow", "self_glass")' in catalog
assert "FluidTags" not in engine and "cameraInWater" not in engine
assert "java.awt.Color" not in engine and "Color.HSBtoRGB" not in engine
assert "private static int hsbToRgb(" in engine and "GLINT_COLOURS" in engine
assert "int[] colours =" not in engine
assert engine.count("if (player.isInvisible() || player.isSpectator()) return;")>=5
assert "renderWings" in engine and 'config.isOn("aura")' in engine
for mid in expected: assert f'"{mid}"' in engine
assert 'MusicEngine.audioLevel()' in engine and 'config.moduleValue("music_aura_sync", "scale"' in engine
assert engine.count("player.getMainArm() == net.minecraft.util.Arm.RIGHT ? 1 : -1")>=3
assert "int offSide = -mainSide;" in engine
assert "Vec3d offWrist" in engine and "Vec3d offForearm" in engine
assert "boolean held = side == mainSide ? mainHeld : offHeld;" in engine
attached=engine[engine.index("private void renderAttachedGeometryEffects("):engine.index("private void renderAmbientGeometry(")]
assert "double phase = time * 0.032;" in attached and "drawGlassOrb(out, camera, centre" in attached
assert "Math.sin(angle) * 0.28" in attached
assert "drawGlassOrb(out, camera, head.add(0, 0.045 * scale, 0)" in attached
for k in ["musicAuraScale","handGlowScale","armGlowScale","heldGlowScale","selfGlassScale"]: assert f'case "{k}"' in settings
assert 'config.setModuleValue("hand_glow", "scale"' in settings
assert 'config.setModuleValue("arm_glow", "scale"' in settings
assert 'config.setModuleValue("held_item_glow", "scale"' in settings
assert 'case "moduleIntensity" -> config.setModuleValue(module.id(), "intensity"' in settings
assert "public boolean isOn(String id)" in config
assert "mod_version=0.50.0" in (root/"gradle.properties").read_text()
assert "BAROX-VS-v050.jar" in (root/"build.gradle").read_text()
assert (root/"VERSION").read_text().strip()=="BAROX VS v050"
assert "BAROX VS v050" in (root/"BUILD_VERSION.txt").read_text()
assert (root/"FIRST_TEN_MODULE_REVIEW_v050.md").is_file()
print("v050 static checks passed: first 10/99 modules audited; all IDs and parent groups preserved.")
