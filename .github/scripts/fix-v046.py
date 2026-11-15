#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1])
path = root / "src/main/java/com/baroxvs/client/render/SkyboxEngine.java"
source = path.read_text(encoding="utf-8")
for channel in range(3):
    old = f"clamp255(lerp(c[{channel}], p[{channel}] * 255f, 0.24f))"
    new = f"clamp255(Math.round(lerp(c[{channel}], p[{channel}] * 255f, 0.24f)))"
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"v046 aurora channel {channel}: expected one float-to-int conversion, found {count}")
    source = source.replace(old, new, 1)
path.write_text(source, encoding="utf-8")
print("v046 aurora colour conversions fixed for Java integer vertex colours.")
