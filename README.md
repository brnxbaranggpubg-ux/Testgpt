# BAROX VS — v007

**Minecraft Java 1.21.4 · Fabric · Java 21**

BAROX VS is a client-side visual customization studio with a compact six-column GUI, HUD Studio, sky and skin customization, wings, ambient geometry and direct-URL MP3 playback.

## v007 — water and depth fix

- Wings and ambient effects now use a depth-tested render layer instead of the depth-ignoring debug-quad layer.
- The cosmetic renderer now runs after entity rendering, so the player model is already in the depth buffer and can naturally hide the wing attachment roots.
- The cosmetic renderer no longer uses `RenderLayer.getDebugQuads()`. Geometry should no longer draw through water or solid world surfaces.

## Existing features

- **Reference-style Click GUI:** six compact, semi-transparent columns for Combat FX, Movement, Player, HUD, Misc and Themes.
- **T — HUD Studio:** move, resize, adjust transparency and switch Liquid Glass / Frosted / Solid / Neon Edge materials.
- **Automatic language:** reads Minecraft's active language; Turkish, English and German translations are included.
- **Sky Studio:** 24 built-in procedural sky palettes and a custom panorama at `config/baroxvs/sky.png`.
- **Skin Studio:** local 64×64 Minecraft skin at `config/baroxvs/skins/active.png`.
- **Player cosmetics:** wings, cape, companion shapes, runes, aura and ambient geometry.
- **Music player:** direct HTTP(S) MP3 stream URL only, with play, pause/resume, stop and volume.

## Controls

| Key | Action |
|---|---|
| Right Shift | Open / close Visual Studio |
| T | Open / close HUD Studio |
| Right Alt | Show / hide BAROX HUD |
| Z | Toggle wings |
| V | Toggle aura |
| B | Toggle hand glow |
| N | Toggle sky mood |

## API dependencies

Fabric API is already integrated in the Gradle build. The current GUI is custom-drawn and the cosmetic renderer uses BAROX-owned geometry, so Cloth Config, LibGui and GeckoLib are not runtime requirements and are not bundled just to increase the mod size. EMF and ETF are separate client-side OptiFine-format model/texture mods rather than general-purpose APIs needed by this renderer.

No extra API JAR needs to be sent for v007.

## Build

The reproducible source is attached to the GitHub Release.

```bash
gradle clean build --no-daemon
```

Output: `build/libs/BAROX-VS-v007.jar`. The release pipeline uses Java 21 and Gradle 8.12, checks the source patch, compiles the Fabric mod and validates the remapped JAR.

## Test status

The CI build checks compilation and JAR integrity. It does not simulate Minecraft's full water-rendering pipeline or replace an in-game test. A real F5 / underwater test on Android/ZalithLauncher is still required before claiming the visual bug is fully confirmed fixed.
