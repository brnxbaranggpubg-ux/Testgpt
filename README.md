# BAROX VS v005

**Minecraft Java 1.21.4 · Fabric · Java 21**

v005 is a visual-system rewrite, not a skin on the vanilla particle engine.

## Compact Visual Studio

- A centered 820×460 floating window scales down for small screens; the world remains visible around it.
- Close with the X or Right Shift. Closing the menu leaves music playback running.
- Dedicated Wings Lab, effects, HUD, music and colour pages.

## Independent visuals

- The mod owns its particle simulation and draws the effects through Fabric's world-render callback.
- There are no calls to vanilla `ParticleTypes`, `ParticleEffect` or `addParticle` in the source.
- 19 wing styles, layered feather fans, custom auras, trails, capes, pets, runes, and hand glows.
- Cyber wings have one continuous wing-shaped contour, a thin themed line, and a low-opacity theme-coloured membrane so the geometry remains airy instead of becoming a solid block.
- The theme's primary and secondary colours drive the wing outline, membrane and highlights.

## URL music player

- Accepts direct HTTP(S) MP3 streams, including MP3 URLs with query strings.
- Play/load, pause/resume, stop, volume, and a separate X close control.
- Closing the music page/menu does not stop playback. STOP explicitly stops the track.
- Android AudioTrack is accessed reflectively so no Android SDK is needed at compile time; desktop Java Sound is the fallback.
- This is a direct MP3 stream player, not a YouTube-page or general media-site downloader.

## Controls

| Key | Action |
|---|---|
| Right Shift | Open / close Visual Studio |
| Right Alt | Show / hide BAROX HUD |
| Z | Toggle wings |
| V | Toggle aura |
| B | Toggle hand glow |
| N | Toggle sky mood |

## Build

The exact source archive is stored as ordered binary chunks under `source-v005-parts/`. GitHub Actions reassembles the archive, checks SHA-256 `c47f213946070af99a403aca212de6c29fc6f59da97f4c70b6396b69ab43de19`, verifies that vanilla particle APIs are absent, builds with Gradle 8.12 and Java 21, verifies the remapped Fabric JAR and publishes release `v005`.

## Research and licensing

Fourteen relevant projects were reviewed as architecture references, not 10,000 repositories. See `RESEARCH_NOTES.md` and `THIRD_PARTY_NOTICES.md` in the source archive. No third-party code or artwork was copied. The optional JLayer MP3 decoder is covered by its LGPL-2.1 notice.

## Scope

Client-side visual effects and audio only. No combat automation, server-state mutation, ESP or anti-cheat bypass. Cyber wings are custom rendered wing silhouettes, not a player-skin or armor 3D model.
