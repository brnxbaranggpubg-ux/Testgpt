# BAROX VS — v007

**Minecraft Java 1.21.4 · Fabric · Java 21**

BAROX VS v007 reorganizes its client code into focused packages and corrects the custom cosmetic rendering path around water.

## v007 changes

- Packages split into `gui`, `hud`, `config`, `cosmetic`, `render`, `audio`, and `theme`.
- Cloth Config 17.0.144 powers the advanced settings screen.
- World cosmetics use the entity-translucent render layer, not `DEBUG_QUADS`.
- World cosmetics are skipped when the camera is submerged or the crosshair targets a water block.
- The sky renderer is skipped while the active camera is submerged.
- Existing Turkish, English and German language resources remain included.
- Fabric API events are preferred for client lifecycle, HUD, keys and world rendering. The remaining mixin is narrowly limited to the local skin texture override.

## Dependencies

- Minecraft Java 1.21.4, Fabric Loader 0.16.10+, Fabric API 0.119.2+1.21.4, Java 21.
- **Cloth Config 17.0.144 is required at runtime** for the advanced settings screen and must be installed separately.
- GeckoLib 4.8.5 is a compile-only optional model API. The current wings still use BAROX geometry and are not yet a GeckoLib GeoModel rig.
- EMF and ETF are optional companion mods, not required dependencies.

## Notes

The source-level water correction still needs in-game confirmation in first- and third-person views, including camera submersion and water surfaces. Sodium/Iris compatibility also requires live testing with the combinations being used.

Run `gradle clean build --no-daemon` with Java 21 to build. The release workflow builds and verifies `BAROX-VS-v007.jar`.
