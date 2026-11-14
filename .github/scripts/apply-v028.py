#!/usr/bin/env python3
"""Apply the v028 local Lyric Flow source patch after the v027 reconstruction/check."""
from __future__ import annotations
import base64
import gzip
import pathlib
import subprocess
import sys


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply-v028.py <project-directory>")
    project = pathlib.Path(sys.argv[1]).resolve()
    if not (project / "src/main/java/com/baroxvs/client/audio/MusicEngine.java").is_file():
        raise SystemExit(f"not a BAROX project directory: {project}")
    patch_dir = pathlib.Path(__file__).resolve().parents[2] / "v028-patch"
    parts = sorted(patch_dir.glob("part-*.b64"))
    if not parts:
        raise SystemExit("v028 patch payload is missing")
    encoded = "".join(path.read_text(encoding="ascii").strip() for path in parts)
    try:
        patch_data = gzip.decompress(base64.b64decode(encoded, validate=True))
    except Exception as exc:
        raise SystemExit(f"invalid v028 patch payload: {exc}") from exc
    patch = subprocess.run(
        ["patch", "--batch", "--forward", "--silent", "-p1", "-d", str(project)],
        input=patch_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if patch.returncode != 0:
        sys.stdout.write(patch.stdout.decode("utf-8", errors="replace"))
        raise SystemExit(f"v028 patch application failed ({patch.returncode})")
    print(f"v028 source patch applied ({len(parts)} payload part(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
