from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
path = root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java"
source = path.read_text(encoding="utf-8")
start = source.index("private void renderChineseHat(")
end = source.index("private void renderHanfuOrnament(", start)
segment = source[start:end]
replacements = [
    (".add(back.multiply(Math.cos(windPhase * 1.36 + side) * 0.009 * scale))",
     ".add(forward.multiply(Math.cos(windPhase * 1.36 + side) * 0.009 * scale))"),
    (".add(back.multiply(Math.sin(windPhase * 1.7 + side * 0.6) * 0.014 * scale))",
     ".add(forward.multiply(Math.sin(windPhase * 1.7 + side * 0.6) * 0.014 * scale))"),
    (".add(back.multiply(Math.cos(windPhase * 1.9 + side) * 0.008 * scale))",
     ".add(forward.multiply(Math.cos(windPhase * 1.9 + side) * 0.008 * scale))"),
]
for old, new in replacements:
    count = segment.count(old)
    if count != 1:
        raise SystemExit(f"expected one kasa tassel basis match, found {count}")
    segment = segment.replace(old, new, 1)
path.write_text(source[:start] + segment + source[end:], encoding="utf-8")
print("v068 kasa tassels: corrected to the local hat-forward basis")
