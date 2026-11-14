#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")
rel = "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java"
path = root / rel
src = path.read_text(encoding="utf-8")
old = '''        // Celestial Wings: decorative light-feather geometry on the back.
        if (config.isOn("celestial_wings")) {
            int color = withAlpha(v022WingColor(), 0xD8);
            for (int side : new int[]{-1, 1}) {
                Vec3d root = pos.add(back.multiply(0.25)).add(0, 1.23, 0);
                for (int i = 0; i < 7; i++) {
                    double spread = 0.24 + i * 0.075;
                    Vec3d tip = root.add(back.multiply(0.18 + i * 0.045))
                            .add(right.multiply(side * spread))
                            .add(0, 0.13 + Math.sin(i * 0.48 + time * 0.025) * 0.07, 0);
                    ribbon(out, camera, root, tip, up, 0.025 - i * 0.001, color);
                    drawStar(out, camera, tip, 0.026, withAlpha(color, 0xD0), time * 0.02 + i, right, up);
                }
            }
        }
'''
new = '''        // Wings are anchored behind the torso, with independent shoulder and waist layers.
        // Back-offset keeps the feather geometry outside the player silhouette during yaw turns.
        if (config.isOn("celestial_wings") || config.isOn("wings")) {
            int color = withAlpha(config.isOn("celestial_wings") ? v022WingColor() : 0xFF9EDFFF, 0xD8);
            for (int side : new int[]{-1, 1}) {
                Vec3d shoulderRoot = pos.add(back.multiply(0.43)).add(0, 1.30, 0);
                Vec3d waistRoot = pos.add(back.multiply(0.46)).add(0, 0.94, 0);
                for (int i = 0; i < 8; i++) {
                    double spread = 0.28 + i * 0.078;
                    double rear = 0.34 + i * 0.055;
                    double flutter = Math.sin(i * 0.42 + time * 0.025) * 0.035;
                    Vec3d shoulderTip = shoulderRoot.add(back.multiply(rear))
                            .add(right.multiply(side * spread))
                            .add(0, 0.10 + flutter, 0);
                    ribbon(out, camera, shoulderRoot, shoulderTip, up, 0.030 - i * 0.0014, color);
                    drawStar(out, camera, shoulderTip, 0.026,
                            withAlpha(color, 0xD0), time * 0.02 + i, right, up);

                    // Lower feather fan sits at the waist/hip line rather than clipping through the torso.
                    double lowerSpread = 0.22 + i * 0.062;
                    Vec3d waistTip = waistRoot.add(back.multiply(0.40 + i * 0.045))
                            .add(right.multiply(side * lowerSpread))
                            .add(0, -0.12 + flutter * 0.7, 0);
                    ribbon(out, camera, waistRoot, waistTip, up, 0.026 - i * 0.0012,
                            withAlpha(color, 0xC8));
                }
                drawRing(out, camera, waistRoot, 0.13, withAlpha(color, 0x9A),
                        time * 0.012, right, forward);
            }
        }
'''
if src.count(old)!=1: raise SystemExit(f"Expected one wing render block, got {src.count(old)}")
src=src.replace(old,new,1)
path.write_text(src,encoding="utf-8")
print("v023 wing anchors applied")
