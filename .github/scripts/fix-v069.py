from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
path = root / "src/main/java/com/baroxvs/client/cosmetic/CosmeticEngine.java"
source = path.read_text(encoding="utf-8")
old = "withAlpha(tint, Math.round(0x46 * opacity * weatherGain))"
new = "withAlpha(tint, (int) Math.round(0x46 * opacity * weatherGain))"
count = source.count(old)
if count != 1:
    raise SystemExit(f"Weather Aura alpha conversion: expected one match, found {count}")
path.write_text(source.replace(old, new, 1), encoding="utf-8")
print("v069 Weather Aura alpha conversion fixed")
