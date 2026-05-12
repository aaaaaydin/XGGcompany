"""Convert a video into PNG frames for desktop_cat.py using FFmpeg.

This script is Python stdlib only. It does not remove complex backgrounds by
itself; it wraps FFmpeg for videos that already have alpha or simple chroma-key
backgrounds.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert video to PNG frames for the desktop cat.")
    parser.add_argument("input", help="Input video path, for example D:\\cat\\cat_alpha.mp4")
    parser.add_argument("--output-dir", default="assets/frames", help="Output frame directory.")
    parser.add_argument("--mode", choices=("alpha", "chroma", "none"), default="alpha", help="Conversion mode.")
    parser.add_argument("--fps", type=int, default=24, help="Output frames per second.")
    parser.add_argument("--width", type=int, default=260, help="Output frame width; height keeps aspect ratio.")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="Path to ffmpeg.exe, or 'ffmpeg' if it is in PATH.")
    parser.add_argument("--chroma-color", default="0x00FF00", help="Chroma key color, e.g. 0x00FF00 for green.")
    parser.add_argument("--similarity", type=float, default=0.18, help="Chroma key similarity.")
    parser.add_argument("--blend", type=float, default=0.06, help="Chroma key edge blend.")
    parser.add_argument("--clean", action="store_true", help="Delete old frame_*.png files first.")
    return parser


def resolve_ffmpeg(ffmpeg: str) -> str:
    if ffmpeg.lower() == "ffmpeg":
        found = shutil.which("ffmpeg")
        if found:
            return found
        raise SystemExit("ffmpeg was not found. Pass --ffmpeg path\\to\\ffmpeg.exe or add FFmpeg to PATH.")
    path = Path(ffmpeg)
    if not path.exists():
        raise SystemExit(f"ffmpeg.exe was not found: {path}")
    return str(path)


def make_filter(args: argparse.Namespace) -> str:
    base = f"fps={args.fps},scale={args.width}:-1:flags=lanczos"
    if args.mode == "chroma":
        return f"{base},chromakey={args.chroma_color}:{args.similarity}:{args.blend},format=rgba"
    return f"{base},format=rgba"


def main() -> int:
    args = build_parser().parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input video was not found: {input_path}")
    if args.fps < 1:
        raise SystemExit("--fps must be greater than 0.")
    if args.width < 1:
        raise SystemExit("--width must be greater than 0.")

    ffmpeg = resolve_ffmpeg(args.ffmpeg)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.clean:
        for old_frame in output_dir.glob("frame_*.png"):
            old_frame.unlink()

    output_pattern = output_dir / "frame_%04d.png"
    command = [
        ffmpeg,
        "-hide_banner",
        "-y",
        "-i",
        str(input_path),
        "-vf",
        make_filter(args),
        "-start_number",
        "1",
        str(output_pattern),
    ]
    print("Running:", " ".join(f'"{part}"' if " " in part else part for part in command))
    subprocess.run(command, check=True)
    print(f"Done. PNG frames were written to: {output_dir}")
    print("Next: run `py -3 desktop_cat.py` from the project root.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
