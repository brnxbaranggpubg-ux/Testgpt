#!/usr/bin/env python3
"""Apply the original v031 visual HUD patch after the v030 reconstruction."""
from __future__ import annotations
import base64
import gzip
import pathlib
import subprocess
import sys


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply-v031.py <project-directory>")
    project = pathlib.Path(sys.argv[1]).resolve()
    marker = project / "src/main/java/com/baroxvs/client/hud/HudRenderer.java"
    if not marker.is_file():
        raise SystemExit(f"not a BAROX project directory: {project}")
    patch_dir = pathlib.Path(__file__).resolve().parents[2] / "v031-patch"
    parts = sorted(patch_dir.glob("part-*.b64"))
    if not parts:
        raise SystemExit("v031 patch payload is missing")
    encoded = "".join(path.read_text(encoding="ascii").strip() for path in parts)
    try:
        patch_data = gzip.decompress(base64.b64decode(encoded, validate=True))
    except Exception as original_error:
        # Recover only if one deletion produces a gzip stream whose CRC and
        # uncompressed-size checks pass. Otherwise fail closed.
        recovered: set[bytes] = set()
        first = parts[0].read_text(encoding="ascii").strip()
        if len(encoded) % 4 == 1:
            tail = "".join(part.read_text(encoding="ascii").strip() for part in parts[1:])
            for index in range(len(first)):
                repaired = first[:index] + first[index + 1:] + tail
                try:
                    recovered.add(gzip.decompress(base64.b64decode(repaired, validate=True)))
                except Exception:
                    continue
                if len(recovered) > 1:
                    break
        if len(recovered) != 1:
            raise SystemExit(f"invalid v031 patch payload: {original_error}") from original_error
        patch_data = recovered.pop()
        print("v031 payload: recovered one stray base64 character using gzip CRC/size validation")
    result = subprocess.run(
        ["patch", "--batch", "--forward", "--silent", "-p1", "-d", str(project)],
        input=patch_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode:
        sys.stdout.write(result.stdout.decode("utf-8", errors="replace"))
        raise SystemExit(f"v031 source patch application failed ({result.returncode})")
    print(f"v031 source patch applied ({len(parts)} payload part(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
