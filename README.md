# BAROX VS — v015

**Minecraft Java 1.21.4 · Fabric · Java 21**

BAROX VS is a client-side visual customization studio. The v015 pass expands the information HUD and procedural atmosphere while retaining the twelve wing silhouettes, cosmetics, skins, sky studio, audio player, HUD profiles and per-widget controls.

## v015 — World Monitor, Player Vitals and dynamic atmosphere

- **World Monitor:** optional dimension, biome, weather and in-game time rows. The card can move to the available side column, respects screen bounds and has independent width, scale and opacity controls.
- **Player Vitals:** a compact vector card for health, hunger and experience progress. Each metric can be hidden independently; colours follow the current value rather than relying on particles.
- **Dimension Coordinates:** the coordinate pill can show equivalent X/Z coordinates for Overworld ↔ Nether using the 8:1 conversion, while keeping the normal XYZ row intact. The End and custom dimensions do not display a misleading conversion.
- **Armor HUD:** each equipped armor item now has a readable durability percentage and a colour-coded durability bar.
- **Day / Night Sky:** procedural sky palettes smoothly shift in brightness and hue with world time; stars become clearer at night. The user-provided photo panorama is deliberately left unchanged.
- **Settings and profiles:** all new switches and per-card width/scale/opacity values use the existing JSON config and HUD profile persistence. Turkish, English and German translation keys are kept in parity.

The supplied 1,000-item report remains a staged backlog. Each visual must use its appropriate subsystem: vector UI, 3D geometry, model animation, camera, sky rendering, post-processing or audio. Particles remain limited to effects that genuinely need short-lived particle elements.

## Compatibility

- Minecraft Java **1.21.4**
- Fabric Loader **0.16.10 or newer**
- Java **21**
- Fabric API **0.119.2+1.21.4**
- Cloth Config Fabric **17.0.144** (required separately)
- GeckoLib **4.8.5** remains optional and compile-time only.

CI reconstructs the source, runs v013–v015 static checks, validates the three locale files, compiles the Java 21 Fabric mod and verifies JAR integrity. CI does not replace a live Minecraft session; Android/ZalithLauncher and Sodium/Iris behaviour still needs in-game testing.

## Previously shipped systems

- v014: Compass Bar and modern Fabric HUD layer registration.
- v013: HUD/profile persistence and module hardening.
- v012: UI transitions, HUD profiles, diagnostics and stable dim-only backdrops.
- v011: twelve distinct wing silhouettes.
- v010: butterfly wing redesign and additional cosmetics.

## Retained v012 UI and stability features

- Stable dim-only backdrops replace the vanilla blur framebuffer path on nested UI screens. The panels retain the layered glass visual, avoiding depth/pixelation glitches; this is not a true Gaussian framebuffer blur.
- Page navigation uses a short cubic-eased slide transition. HUD notifications ease into place rather than appearing abruptly.
- HUD Editor adds three persistent profile slots (PvP, Farm and Chill). Click loads a saved profile; Shift+Click saves the current theme, HUD layout, widget switches and widget styles.
- Optional BAROX Diagnostics shows local FPS, JVM memory usage and cosmetic particle count. It does not inspect remote players or send data to servers.
- Turkish, English and German translations include the new profile and diagnostics labels.

## Retained v011 wing collection

The wing wardrobe has been rebuilt around **12 distinct silhouettes**. The previous overlapping Crystal / Frost / Prism / Lunar / Aether-style variants that reused the same mesh are removed.

1. **Seraph Feathers** — individually tapered, layered feather fan.
2. **Thorned Demon** — skeletal bat membrane, long finger bones and sharp trailing notches.
3. **Dragon Armor** — overlapping armored plates, dorsal spikes and heavy lower hook.
4. **Butterfly** — four rounded lobes, veins and eye-spots.
5. **Moon Moth** — one broad scalloped shield with paired lunar markings.
6. **Phoenix Flame** — separated flame feathers and flowing ember tails.
7. **Frost Shards** — branching faceted crystal blades.
8. **Void Crescent** — open crescent arcs with a clear negative-space centre.
9. **Sakura Bloom** — petal clusters connected by fine stems.
10. **Astral Halo** — orbital rings, luminous nodes and narrow fins.
11. **Cyber Pulse** — hard-surface segmented panels and circuit traces.
12. **Wildvine** — branching stems, pointed leaves and thorns.

Every style uses a shoulder-hinge transform rather than a simple vertical offset, with separate geometry and a dedicated Wings Lab preview. The default is Seraph Feathers. Size, opacity, hue and motion settings remain available.

## Previous features retained

- **Layered butterfly wings:** Butterfly is now the default wing preset. Its upper and lower lobes have scalloped outlines, translucent membrane panels, individual vein ribs and small highlight spots. Wing motion now transforms the complete geometry around shoulder-rooted anchors.
- **Hanfu hair ornaments:** three independent styles — Jade Tassel, Sakura Pin and Moon Halo — can be enabled from the Cosmetics category and tuned from their own settings panel.
- **Silk Ribbons and Butterfly Swarm:** two new optional visual modules add flowing translucent ribbons and drifting butterfly particles. Both use BAROX-owned geometry and independent module settings.
- **Jade Festival Kasa:** the standalone Chinese Straw Kasa now includes a fourth style with jade accents and hanging tassel strands.
- **Wing controls retained:** span, colour hue, saturation, brightness, opacity and extra scale controls remain available across the redesigned wing catalogue.
- **Chinese Straw Kasa module:** the woven kasa is a standalone Cosmetics module, not buried inside the general Headwear selector. Its four styles, size, hue, saturation, brightness and opacity are configurable from its own settings panel.
- **Right-click module settings:** right-click a module card in the module gallery or module pages to open its own scrollable settings sheet. Left-click still toggles a module or advances a cycle option. Settings are saved in `config/baroxvs.json`.
- **Live module registry:** `ModuleCatalog.register(Module)` and `unregister(id)` update the module catalogue. Categories are derived from registered modules rather than a hard-coded category list, so newly registered modules appear in the gallery automatically.
- **Per-module tuning:** supported visual modules keep independent scale, opacity and frequency values. The module settings view also provides specialised controls where relevant, including wing colour/size, kasa appearance, ambient density/range/speed and music visualiser response.
- **Ambient orbs and cubes:** floating white pearl orbs and translucent cubes are independently switchable. Tune object count, size, spread, drift speed, colour, brightness and impact response. The view-direction interaction applies only a local visual response and does not change the normal game action.
- **Audio-reactive visuals:** the Audio Visualizer reads the MP3 decoder's smoothed RMS amplitude and uses it to modulate colour, rings and particles. Tune hue, sensitivity, pulse radius, particle rate, scale, opacity and response frequency.
- **URL music playback:** Paste starts playback automatically; pressing Enter in the URL field also starts it. A direct HTTP(S) MP3 stream or a simple M3U/PLS playlist that points to MP3 audio is supported. No local MP4 file is needed. Web pages, HLS `.m3u8`, and AAC/OGG/WAV streams are not decoded by this player.
- **Responsive module settings:** the settings panel uses a compact, scrollable layout for smaller game-window sizes.
- **Automatic language:** the interface reads Minecraft's active language at runtime. Turkish (`tr_tr`), English (`en_us`) and German (`de_de`) translations are included; Minecraft's normal translation fallback is used for other locales.
- **Sky Studio:** 24 built-in procedural sky palettes. A custom equirectangular panorama can replace the sky by placing a PNG at `config/baroxvs/sky.png`, then pressing **Reload Sky**. Independent top, horizon and lower-sky colour controls remain available.
- **Skin Studio:** three switchable local skin profiles: `active.png`, `slot-2.png` and `slot-3.png` in `config/baroxvs/skins/`. Each profile accepts a 64×64 PNG and can be reloaded in-game. This replaces the local player's skin texture; it does not generate an entirely new player model or replicate the change to other clients.
- **Water-safe cosmetic layer:** wings, cape and ambient geometry use Minecraft's entity-translucent render layer. BAROX world geometry is skipped while the camera is submerged or the crosshair targets a water block, preserving the normal vanilla water view.
- **Liquid rain and defeat dissolve:** optional custom glass-like droplets and a non-graphic shimmer dissolve effect. There is no gore or physical ragdoll simulation.
- **Rounder Liquid Glass:** rounded UI primitives use fractional edge coverage; HUD surfaces use nested translucent layers, subtle edge tint and a top highlight. This is a lightweight glass treatment, not a full framebuffer Gaussian blur.

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

Cloth Config API 17.0.144 is required for the advanced Settings screen. GeckoLib 4.8.5 is a compile-time optional model API; EMF/ETF are optional companion mods. All v011 wing geometry and retained v010 ornament, ribbon and butterfly geometry is authored by BAROX and does not require a GeckoLib GeoModel rig. Cloth Config must be installed in the mods folder; GeckoLib is not required at runtime.

## Custom image files

Use your launcher or Android file manager to place files in the paths above. The custom sky is a wide panorama, not an ordinary square photo; convert or crop a picture to an equirectangular 2:1 PNG before loading it. Player skins must use a standard 64×64 Minecraft skin layout.

## Build

```bash
gradle clean build --no-daemon
```

Output: `build/libs/BAROX-VS-v015.jar`. The release workflow uses Java 21 and Gradle 8.12, verifies the compiled JAR entries and publishes the v015 release asset.

## Render architecture

Most client rendering hooks use Fabric API events. BAROX deliberately keeps one narrowly scoped mixin for the local skin-texture override; adding more mixins without a specific vanilla hook would increase compatibility risk rather than improve it. The world-render path uses Fabric `BEFORE_ENTITIES` and the standard entity-translucent layer instead of `DEBUG_QUADS`.

See [`RENDER_COMPATIBILITY.md`](RENDER_COMPATIBILITY.md) for the render and Sodium compatibility notes.

## Scope and test note

Features are local cosmetics, local audio playback and HUD/interface elements. The project does not modify server state or automate gameplay. The music player is a direct MP3 stream decoder; it is not a general webpage/video downloader. CI compilation and JAR integrity checks are not a substitute for running Minecraft on each launcher/device; an actual in-game test on Android/ZalithLauncher remains to be completed.
