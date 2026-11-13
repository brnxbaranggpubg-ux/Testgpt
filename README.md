# BAROX VS — v006

**Minecraft Java 1.21.4 · Fabric · Java 21**

BAROX VS v006 is a client-side visual customization studio. The main window follows the six-column glass-panel layout in the supplied reference, while keeping the Minecraft world visible behind it.

## v006 highlights

- **Reference-style Click GUI:** six compact, semi-transparent columns for Combat FX, Movement, Player, HUD, Misc and Themes. The selected Violet Void theme is the fresh-install default.
- **T — HUD Studio:** move the HUD preview, resize the overall HUD, adjust transparency, switch Liquid Glass / Frosted / Solid / Neon Edge materials, toggle visibility and enable or disable individual HUD/Misc widgets. Changes are saved in `config/baroxvs.json`.
- **Automatic language:** the interface reads Minecraft's active language at runtime. Turkish (`tr_tr`), English (`en_us`) and German (`de_de`) translations are included; Minecraft's normal translation fallback is used for other locales.
- **Sky Studio:** 24 built-in procedural sky palettes. A custom equirectangular panorama can replace the sky by placing a PNG at `config/baroxvs/sky.png`, then pressing **Reload Sky**. A 2:1 panorama is recommended; supported image sizes are 64×32 through 8192×4096.
- **Skin Studio:** import a 64×64 Minecraft skin PNG to `config/baroxvs/skins/active.png`, press **Reload Skin**, then enable **Custom Skin**. This replaces the local player's skin texture; it does not generate a new 3D player model. Other players do not see the local replacement.
- **Player-attached wings:** the wing mesh is anchored to the player's shoulder area and rendered before the player model so the torso can cover the attachment roots. Wing size, membrane and harness can be adjusted independently. The wing geometry remains client-side cosmetics.
- **Ambient geometry:** choose mixed orbs, cubes, stars, rings, shards or hearts, and tune density and distance (Near / Around / Far / Wide). These elements are intentionally softer and distributed around the surrounding area instead of being concentrated on the player's body.
- **Custom effect renderer:** BAROX owns the visual geometry and spark simulation. It does not spawn vanilla Minecraft particles through `ParticleTypes`, `ParticleEffect` or `addParticle`.
- **Music player:** direct HTTP(S) MP3 URLs only; playback supports play, pause/resume, stop and volume. Closing the GUI does not stop playback.

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

The music player requires a direct MP3 stream URL. Video pages and playlist pages are not decoded as audio sources.

## Custom image files

Use your launcher or Android file manager to place files in the paths above. The custom sky is a wide panorama, not an ordinary square selfie/photo; convert or crop a picture to an equirectangular 2:1 PNG before loading it. The player appearance must be a standard 64×64 Minecraft skin layout.

## Build

```bash
gradle clean build --no-daemon
```

Output: `build/libs/BAROX-VS-v006.jar`. The release workflow uses Java 21 and Gradle 8.12, verifies the compiled JAR entries and publishes the release asset.

## Scope and test note

Features are local cosmetics, local audio playback and HUD/interface elements. The mod does not alter server state or automate combat/movement. CI compilation and JAR integrity checks are not a substitute for running Minecraft on each launcher/device; an actual in-game test on Android/ZalithLauncher remains to be completed.
