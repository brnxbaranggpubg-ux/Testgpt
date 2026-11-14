#!/usr/bin/env python3
"""Apply the v030 original BAROX visual HUD patch after the v029 reconstruction."""
from __future__ import annotations
import base64
import gzip
import pathlib
import subprocess
import sys


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply-v030.py <project-directory>")
    project = pathlib.Path(sys.argv[1]).resolve()
    marker = project / "src/main/java/com/baroxvs/client/hud/HudRenderer.java"
    if not marker.is_file():
        raise SystemExit(f"not a BAROX project directory: {project}")
    patch_dir = pathlib.Path(__file__).resolve().parents[2] / "v030-patch"
    parts = sorted(patch_dir.glob("part-*.b64"))
    if not parts:
        raise SystemExit("v030 patch payload is missing")
    encoded = "".join(path.read_text(encoding="ascii").strip() for path in parts)
    try:
        patch_data = gzip.decompress(base64.b64decode(encoded, validate=True))
    except Exception as exc:
        raise SystemExit(f"invalid v030 patch payload: {exc}") from exc
    result = subprocess.run(
        ["patch", "--batch", "--forward", "--silent", "-p1", "-d", str(project)],
        input=patch_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode:
        sys.stdout.write(result.stdout.decode("utf-8", errors="replace"))
        raise SystemExit(f"v030 patch application failed ({result.returncode})")
    print(f"v030 source patch applied ({len(parts)} payload part(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
