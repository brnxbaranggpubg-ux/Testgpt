# BAROX VS v066 — player cosmetics and trail repair

Minecraft Java 1.21.4 / Fabric / Java 21.

- Replaced high-tessellation aura discs with a dedicated 24-sector, two-band radial mesh.
- Replaced footprint ellipsoids with one oriented flat quad and shortened their lifetime.
- Replaced Prism Trail glass ellipsoids with narrow ribbon quads and reduced sampling density.
- Raised Jump Circle above the ground plane to reduce z-fighting and foot occlusion.
- Moved wing roots farther behind the player silhouette.
- Reduced pet orb tessellation and bloom layering.
- Reduced Player Glass/RGB Outline alpha and surface bias to preserve skin visibility.
- Removed detached held-item glint billboards; the existing baked-item surface glint remains.

No module IDs are added or removed. Static source checks and CI build/JAR validation are required; live Minecraft/ZalithLauncher2 visual and FPS QA remains unperformed.
