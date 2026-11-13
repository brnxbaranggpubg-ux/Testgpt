# BAROX VS — v013

**Minecraft Java 1.21.4 · Fabric · Java 21**

BAROX VS is a client-side visual customization studio focused on modular cosmetics, player-attached effects, responsive HUD widgets and local interface settings.

## v013 — module and HUD hardening

- Aura and Footsteps presets now select different particle silhouettes and colour palettes.
- All drawable HUD cards use their own scale and opacity controls. Info Panel sub-rows remain simple on/off options and no longer expose settings that cannot affect a separate widget.
- The Now Playing card reads the real music-engine state (playing, paused, loading, error or ready) and audio level; it does not display a fabricated playback progress bar.
- HUD profiles retain per-module tuning values in addition to module switches and style selections.
- Configuration saves use a temporary file and atomic replacement when supported. If a config cannot be parsed, BAROX attempts to preserve the damaged file before restoring defaults.
- The module registry validates module IDs, categories, cycle options and default style indices at startup.
- HUD direction names, toast states, target distance and music status are translated in Turkish, English and German.

## Compatibility

- Minecraft Java **1.21.4**
- Fabric Loader **0.16.10 or newer**
- Java **21**
- Fabric API **0.119.2+1.21.4**
- Cloth Config Fabric **17.0.144** (required separately)
- GeckoLib is optional.

The CI build checks source-patch reconstruction, module/HUD invariants, translation parity, Java compilation and JAR archive integrity. This is not a live in-game test: Android and ZalithLauncher runtime behaviour still needs to be checked on-device.

## Earlier releases

- v012: UI transitions, HUD profiles, diagnostics and stable dim-only backdrops.
- v011: twelve distinct wing silhouettes.
- v010: butterfly wing redesign and additional cosmetics.

