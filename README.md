# BAROX VS — v010

**Minecraft Java 1.21.4 · Fabric · Java 21**

BAROX VS is a client-side visual customization studio. v010 focuses on a more expressive butterfly-wing design and additional ornamental cosmetics.

## v010 highlights

- **Butterfly wings by default:** layered upper/lower lobes, scalloped edges, translucent membranes, vein ribs, highlight spots and shoulder-rooted flap motion.
- **Chinese ceremonial headwear:** four independent Kasa styles, including Jade Festival with jade accents and tassel strands.
- **Hanfu hair ornaments:** Jade Tassel, Sakura Pin and Moon Halo.
- **Silk Ribbons:** two flowing translucent trails, with independent scale, opacity and frequency controls.
- **Butterfly Swarm:** drifting butterfly particles, independently switchable and configurable.
- Existing HUD editor, music player, audio visualizer, ambient orbs/cubes, dynamic module registry and per-module settings remain included.

## Dependencies

- Minecraft Java 1.21.4, Fabric Loader 0.16.10+, Fabric API 0.119.2+1.21.4, Java 21.
- **Cloth Config 17.0.144 is required separately** for the advanced settings screen.
- GeckoLib is optional and not required for the v010 additions. All new cosmetics use BAROX-owned geometry and the existing Fabric renderer.

## Build and testing

The workflow applies the v010 source patch to the verified v009 base, compiles with Java 21 / Gradle 8.12, and checks the remapped JAR entries and archive integrity. CI build validation is not the same as a live in-game test; Android/ZalithLauncher and Sodium/Iris appearance still need device testing.

See the [v010 release](https://github.com/brnxbaranggpubg-ux/Testgpt/releases/tag/v010) for the JAR and source archive.
