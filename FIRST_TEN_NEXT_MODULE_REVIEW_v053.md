# BAROX VS v053 — next ten visual modules review

Scope: registrations 21–30, traced through tick/render flow, parent-child gating, settings, saved config and per-frame allocation.

21 Companion Glow (pet_glow): verified correctly gated by Companion parent; its own opacity/radius controls compose with parent opacity.
22 Jump Circle (jump_circle): connected the previously-unused Speed slider, captures takeoff world-position, persists after landing, clears on disable/expiry/world change, and now renders five distinct filled styles.
23 Wing Motion (wing_motion): Still now zeros flap, spring velocity and flex immediately.
24 Wing Sheen (wing_glints): highlights sweep along articulated wing span with a softer secondary sheen.
25 Wing Surface (wing_outline): both lobe and moth highlight paths fully respect the switch.
26–29 Wing Relief, Harness, Membrane and Size: audited parent-child gating and settings keys; preserved.
30 Cape: applies global FX opacity, skips hidden/spectator models and simulation, and reuses vertex colour/position grids and seam index arrays rather than allocating on each frame.

All 99 module IDs, parent groups, option IDs and saved settings remain unchanged. TR/DE/EN locale keys remain aligned. No combat, movement or server features were added. Live Minecraft/ZalithLauncher2 QA has not yet been performed.
