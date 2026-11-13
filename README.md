# BAROX VS — v004

**Minecraft Java 1.21.4 · Fabric · Java 21**

BAROX VS v004 replaces the compact multi-column menu with a responsive Visual Studio: persistent sidebar, readable module cards, Wing Lab, vector preview, and an independent two-colour Color Studio.

## Visual Studio

- Pages: Overview, Wardrobe, Wings Lab, Effects, HUD, Color Studio, Settings.
- Matrix-inspired glass panels, restrained glow, readable typography, module search, and scalable layout.
- Vector wing preview with primary/secondary accent colors.
- Custom primary and secondary hue, saturation and brightness controls.
- 22 built-in palettes; custom color values persist in `config/baroxvs.json`.

## Cosmetics

- 18 wing styles: Crystal, Angel, Demon, Butterfly, Void, Dragon, Phoenix, Frost, Neon, Celestial, Spirit, Arcane, Storm, Sakura, Ember, Lunar, Prism, Aether.
- Four wing motion styles, layered feather fans, edge highlights, glints, shoulder arcs and optional runes.
- Cape shimmer, pet shimmer, orbit stars, halo, aura pulse, footsteps, jump crystal, landing burst, heart/bubble trails and movement afterglow.
- Color accents are driven by the active theme.

## Controls

| Key | Action |
|---|---|
| Right Shift | Open / close Visual Studio |
| Right Alt | Show / hide BAROX HUD |
| Z | Toggle wings |
| V | Toggle aura |
| B | Toggle hand glow |
| N | Toggle sky mood |

## Build and release

The exact source tree is stored as five Base64 text chunks under `source-v004-parts/`. GitHub Actions joins and decodes them into a TAR.XZ archive and verifies its SHA-256 (`1c78a3e37e68a17a6ce6ff69a7717ecb7c9d83c846d1b4dced1fa7b8d92a85e9`). It applies the tracked Java coordinate-rounding patch in `patches/`, builds with Gradle 8.12 and Java 21, validates the remapped Fabric JAR, uploads a build artifact, and publishes the `v004` GitHub Release.

## Scope

Client-side visual particles and HUD/interface only. No custom packets, server-state modification, combat or movement automation, through-wall entity reveal, or anti-cheat bypass. In-world wings are particle silhouettes, not imported 3D player models; the menu preview is a vector illustration.

See `RESEARCH_NOTES.md` inside the source archive for reviewed reference projects and licence notes. No third-party code or artwork was copied.
