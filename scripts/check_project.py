"""Small validation checks for the Python-only desktop cat project."""

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY_FILES = [
    ROOT / "desktop_cat.py",
    ROOT / "scripts" / "convert_video_to_frames.py",
    ROOT / "scripts" / "package_portable.py",
    ROOT / "scripts" / "check_project.py",
]


def main() -> int:
    for path in PY_FILES:
        py_compile.compile(str(path), doraise=True)
        print(f"OK py_compile: {path.relative_to(ROOT)}")
    required = [ROOT / "config.toml", ROOT / "assets" / "frames"]
    for path in required:
        if not path.exists():
            raise SystemExit(f"Missing required path: {path.relative_to(ROOT)}")
        print(f"OK exists: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
