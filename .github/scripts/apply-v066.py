from pathlib import Path
import sys
r=Path(sys.argv[1])
def edit(path, pairs):
 p=r/path; s=p.read_text()
 for old,new in pairs:
  if old not in s: raise SystemExit(f"v066 patch anchor missing in {path}: {old[:80]!r}")
  s=s.replace(old,new,1)
 p.write_text(s)
e="src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java"
edit(e,[
('''        drawSoftDisc(out, camera, pos, radius, primary, renderAnimationTime * 0.012, xAxis, zAxis);
        drawSoftDisc(out, camera, pos.add(0.0, 0.009, 0.0), radius * 0.76, secondary,
                -renderAnimationTime * 0.009, xAxis, zAxis);
        drawSoftDisc(out, camera, pos.add(0.0, 0.016, 0.0), radius * 0.58,
                scaleAlpha(secondary, opacity * 0.46f), renderAnimationTime * 0.006, xAxis, zAxis);''',
'''        drawAuraDisc(out, camera, pos, radius, primary, renderAnimationTime * 0.012, xAxis, zAxis);
        drawAuraDisc(out, camera, pos.add(0.0, 0.012, 0.0), radius * 0.70, secondary,
                -renderAnimationTime * 0.009, xAxis, zAxis);'''),
('''    /** Broad specular blooms follow actual cosmetic and hand locations in both camera modes. */''',
'''    /** Low-overdraw aura mesh: 24 sectors and two radial bands. */
    private static void drawAuraDisc(VertexConsumer out, Vec3d camera, Vec3d centre, double radius,
                                     int color, double angle, Vec3d right, Vec3d up) {
        if (radius <= 0.001 || ((color >>> 24) & 255) <= 1) return;
        double c = Math.cos(angle), sn = Math.sin(angle);
        Vec3d a = right.multiply(c).add(up.multiply(sn)).normalize();
        Vec3d b = up.multiply(c).subtract(right.multiply(sn)).normalize();
        for (int band = 0; band < 2; band++) {
            double inner = band * 0.5, outer = (band + 1) * 0.5;
            int tint = scaleAlpha(color, band == 0 ? 0.44f : 0.20f);
            for (int i = 0; i < 24; i++) {
                double t0 = Math.PI * 2.0 * i / 24.0, t1 = Math.PI * 2.0 * (i + 1) / 24.0;
                Vec3d p0 = centre.add(a.multiply(Math.cos(t0) * radius * inner)).add(b.multiply(Math.sin(t0) * radius * inner));
                Vec3d p1 = centre.add(a.multiply(Math.cos(t1) * radius * inner)).add(b.multiply(Math.sin(t1) * radius * inner));
                Vec3d p2 = centre.add(a.multiply(Math.cos(t1) * radius * outer)).add(b.multiply(Math.sin(t1) * radius * outer));
                Vec3d p3 = centre.add(a.multiply(Math.cos(t0) * radius * outer)).add(b.multiply(Math.sin(t0) * radius * outer));
                emitQuad(out, camera, p0, p3, p2, p1, tint);
            }
        }
    }

    /** Broad specular blooms follow actual cosmetic and hand locations in both camera modes. */'''),
('''        if (mainHeld) {
            Vec3d item = pos.add(right.multiply(mainSide * 0.39)).add(back.multiply(0.12)).add(0, 0.91, 0);
            drawBillboard(out, camera, item, 0.22 * scale, 0.30 * scale, scaleAlpha(highlight, 0.88f),
                    renderAnimationTime * 0.007, right, new Vec3d(0, 1, 0));
        }
        if (offHeld) {
            Vec3d item = pos.add(right.multiply(offSide * 0.39)).add(back.multiply(0.12)).add(0, 0.91, 0);
            drawBillboard(out, camera, item, 0.20 * scale, 0.27 * scale, scaleAlpha(highlight, 0.78f),
                    -renderAnimationTime * 0.006, right, new Vec3d(0, 1, 0));
        }''',
'''        // Held-item glint is emitted on the actual baked item model by HeldItemGlassRenderer.'''),
('''        int mainSide = player.getMainArm() == net.minecraft.util.Arm.RIGHT ? 1 : -1;
        int offSide = -mainSide;
        boolean mainHeld = !player.getMainHandStack().isEmpty();
        boolean offHeld = !player.getOffHandStack().isEmpty();
''',''),
('''            if (age < 0 || age > 100) continue;
            float fade = (float)Math.max(0.06, 1.0 - age / 100.0);''',
'''            if (age < 0 || age > 64) continue;
            float fade = (float)Math.max(0.0, 1.0 - age / 64.0);'''),
('''            drawGlassEllipsoid(out, camera, point, side, WORLD_UP, forward,
                    0.085 * scale, 0.012 * scale, 0.155 * scale, color, 0.78f, age, 6, 10);
            drawGlassEllipsoid(out, camera, point.add(0, 0.010 * scale, 0), side, WORLD_UP, forward,
                    0.044 * scale, 0.008 * scale, 0.095 * scale,
                    withAlpha(0xFFFFFFFF, Math.round(0x58 * opacity * fade)), 0.34f, age, 5, 8);''',
'''            Vec3d heel = point.subtract(forward.multiply(0.105 * scale));
            Vec3d toe = point.add(forward.multiply(0.125 * scale));
            Vec3d half = side.multiply(0.070 * scale);
            emitQuad(out, camera, heel.subtract(half), heel.add(half), toe.add(half.multiply(0.82)),
                    toe.subtract(half.multiply(0.82)), color);'''),
('''            drawGlassEllipsoid(out, camera, centre, side, WORLD_UP, tangent,
                    0.055 * scale * length, 0.022 * scale, Math.max(0.075, segmentLength * 0.72),
                    tint, 0.78f, time * 0.04 + i, 6, 10);''',
'''            double width = 0.030 * scale * length * fade;
            Vec3d half = side.multiply(width);
            Vec3d along = tangent.multiply(Math.max(0.035, segmentLength * 0.52));
            emitQuad(out, camera, centre.subtract(along).subtract(half), centre.add(along).subtract(half),
                    centre.add(along).add(half), centre.subtract(along).add(half), tint);'''),
('position.squaredDistanceTo(lastPrismTrailPos) >= 0.0016','position.squaredDistanceTo(lastPrismTrailPos) >= 0.0064'),
('double fade = Math.max(0.0, 1.0 - age / 20.0);','double fade = Math.max(0.0, 1.0 - age / 16.0);'),
('Vec3d centre = jumpPulseOrigin.add(0, 0.018, 0);','Vec3d centre = jumpPulseOrigin.add(0, 0.055, 0);'),
('Vec3d root = playerPos.add(0, shoulderHeight, 0).add(back.multiply(0.24));','Vec3d root = playerPos.add(0, shoulderHeight, 0).add(back.multiply(0.36));'),
('''        int points = switch (activeRenderQuality) { case 0 -> 6; case 1 -> 8; default -> 10; };
        int layers = activeRenderQuality == 0 ? 1 : activeRenderQuality == 1 ? 2 : 3;''',
'''        int points = switch (activeRenderQuality) { case 0 -> 6; case 1 -> 7; default -> 8; };
        int layers = activeRenderQuality == 0 ? 1 : 2;'''),
('''        int latitudes = switch (activeRenderQuality) { case 0 -> 3; case 1 -> 4; default -> 6; };
        int longitudes = switch (activeRenderQuality) { case 0 -> 5; case 1 -> 6; default -> 8; };''',
'''        int latitudes = switch (activeRenderQuality) { case 0 -> 3; case 1 -> 4; default -> 5; };
        int longitudes = switch (activeRenderQuality) { case 0 -> 5; case 1 -> 6; default -> 7; };'''),
('drawSoftDisc(out, camera, centre, radius, primary,\n                        renderAnimationTime * 0.006, right, forward);','drawAuraDisc(out, camera, centre, radius, primary,\n                        renderAnimationTime * 0.006, right, forward);'),
('drawSoftDisc(out, camera, centre, radius * 0.56, secondary, 0, right, forward);','drawAuraDisc(out, camera, centre, radius * 0.56, secondary, 0, right, forward);'),
('drawSoftDisc(out, camera, petal, radius * 0.29, primary, angle, right, forward);','drawAuraDisc(out, camera, petal, radius * 0.29, primary, angle, right, forward);'),
('drawSoftDisc(out, camera, centre.add(0, 0.012, 0), radius * 0.24, pearl, 0, right, forward);','drawAuraDisc(out, camera, centre.add(0, 0.012, 0), radius * 0.24, pearl, 0, right, forward);'),
('drawSoftDisc(out, camera, centre, radius, primary, rotation, right, forward);','drawAuraDisc(out, camera, centre, radius, primary, rotation, right, forward);'),
('drawSoftDisc(out, camera, centre.add(0, 0.010, 0), radius * 0.72, secondary,','drawAuraDisc(out, camera, centre.add(0, 0.010, 0), radius * 0.72, secondary,'),
('drawSoftDisc(out, camera, centre.add(0, 0.020, 0), radius * 0.40, pearl,','drawAuraDisc(out, camera, centre.add(0, 0.020, 0), radius * 0.40, pearl,'),
('drawSoftDisc(out, camera, centre, radius * 0.66, primary, 0, right, forward);','drawAuraDisc(out, camera, centre, radius * 0.66, primary, 0, right, forward);'),
('drawSoftDisc(out, camera, satellite, radius * 0.19, pearl, angle, right, forward);','drawAuraDisc(out, camera, satellite, radius * 0.19, pearl, angle, right, forward);'),
('drawSoftDisc(out, camera, centre, radius, secondary, 0, right, forward);','drawAuraDisc(out, camera, centre, radius, secondary, 0, right, forward);'),
('drawSoftDisc(out, camera, centre.add(0, 0.012, 0), radius * 0.78, pearl,','drawAuraDisc(out, camera, centre.add(0, 0.012, 0), radius * 0.78, pearl,'),
('drawSoftDisc(out, camera, centre.add(0, 0.022, 0), radius * 0.48, primary,','drawAuraDisc(out, camera, centre.add(0, 0.022, 0), radius * 0.48, primary,'),
('drawSoftDisc(out, camera, centre.add(0, 0.010, 0), radius * 0.68, secondary,','drawAuraDisc(out, camera, centre.add(0, 0.010, 0), radius * 0.68, secondary,')
])
g="src/main/java/com/baroxvs/client/render/SelfGlassRenderer.java"
edit(g,[
('float alpha = opacity * (0.025f + fresnel * 0.62f + sweep * 0.10f);\n            alpha = Math.max(0.0f, Math.min(0.68f, alpha));','float alpha = opacity * (0.006f + fresnel * 0.34f + sweep * 0.045f);\n            alpha = Math.max(0.0f, Math.min(0.34f, alpha));'),
('float bias = 0.0015f + 0.0035f * scale + fresnel * 0.0035f;','float bias = 0.0006f + 0.0012f * scale + fresnel * 0.0008f;'),
('float transmissionScale = 1.0f - transmission * 0.42f;','float transmissionScale = 1.0f - transmission * 0.56f;'),
('(0.055f + fresnel * 0.78f * edge + sweep * 0.40f + specular * 0.28f);\n            alpha = Math.max(0.018f, Math.min(0.62f, alpha));','(0.025f + fresnel * 0.62f * edge + sweep * 0.28f + specular * 0.20f);\n            alpha = Math.max(0.010f, Math.min(0.44f, alpha));')
])
edit("build.gradle",[("BAROX-VS-v065.jar","BAROX-VS-v066.jar")])
edit("gradle.properties",[("mod_version=0.65.0","mod_version=0.66.0")])
(r/"VERSION").write_text("BAROX VS v066\n")
(r/"BUILD_VERSION.txt").write_text("BAROX VS v066\n")
