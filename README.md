# BAROX VS v003

Minecraft Java 1.21.4 · Fabric · Java 21

This repository is the build target for the uploaded BAROX VS v003 source package. The source ZIP is preserved byte-for-byte as Base64 parts under `source-archive/`; GitHub Actions reassembles it, verifies the ZIP, builds it with Gradle 8.12, checks the remapped Fabric JAR, and publishes the v003 release.

## Build output

`BAROX-VS-v003.jar`

## Open the release

After the GitHub Actions build succeeds, download the JAR from the Releases page.

## Visual modules included in the source

The source package contains the Matrix color theme, glass-style ClickGUI, HUD widgets, particle wings, cape trails, companion effects, aura, halo, hand glow, sword sparkle, footsteps, jump and landing effects, and multiple cosmetic styles.

All included effects are client-side presentation features. The archive's Java source is not edited by the workflow.
