# BAROX VS — v014

**Minecraft Java 1.21.4 · Fabric · Java 21**

BAROX VS is a client-side visual customization studio focused on modular cosmetics, responsive HUD widgets, presentation effects and local interface settings.

## v014 — Compass Bar and HUD renderer update

- Optional vector Compass Bar with cardinal direction markers, live degree readout and moving 15-degree tick marks.
- Adjustable width, opacity and scale, saved through the existing module configuration and HUD profile system.
- Compact-width guard for mobile and narrow logical viewports.
- HUD registration migrated to Fabric's supported `HudLayerRegistrationCallback`, placed after `MISC_OVERLAYS`.
- Turkish, English and German labels.

The supplied 1,000-item report is treated as a staged design backlog. Items are implemented in phases, with each visual matched to its appropriate system: vector UI, 3D geometry, model animation, camera, sky rendering, post-processing or audio. Particles are used only for effects that genuinely need short-lived particles.

## Compatibility

- Minecraft Java **1.21.4**
- Fabric Loader **0.16.10 or newer**
- Java **21**
- Fabric API **0.119.2+1.21.4**
- Cloth Config Fabric **17.0.144** (required separately)
- GeckoLib is optional.

CI reconstructs the source, runs static module/HUD/localization checks, compiles the Java 21 Fabric mod and verifies JAR integrity. CI does not replace a live Minecraft session; Android/ZalithLauncher and Sodium/Iris behaviour still needs in-game testing.

## Earlier releases

- v013: HUD/profile persistence and module hardening.
- v012: UI transitions, HUD profiles, diagnostics and stable dim-only backdrops.
- v011: twelve distinct wing silhouettes.
- v010: butterfly wing redesign and additional cosmetics.
