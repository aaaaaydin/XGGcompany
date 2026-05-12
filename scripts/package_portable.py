"""Create a portable package for the Python desktop cat.

Modes:
  source: copies .py files/config/assets. Target PC needs Python 3 installed.
  exe:    uses PyInstaller on the build PC. Target PC does not need Python.

Everything in this script uses Python stdlib except the optional PyInstaller
command, which is only needed for --mode exe.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package desktop_cat.py for another Windows PC.")
    parser.add_argument("--mode", choices=("source", "exe"), default="source", help="Package mode.")
    parser.add_argument("--output-dir", default="dist/desktop-cat-portable", help="Output folder.")
    parser.add_argument("--zip", action="store_true", help="Also create a .zip next to the output folder.")
    parser.add_argument("--frames-dir", default="assets/frames", help="PNG frame directory to include.")
    parser.add_argument("--skip-frame-check", action="store_true", help="Allow packaging without PNG frames.")
    return parser


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def ensure_frames(frames_dir: Path, skip: bool) -> None:
    if skip:
        return
    if not frames_dir.exists() or not any(frames_dir.glob("*.png")):
        raise SystemExit(f"No PNG frames found in {frames_dir}. Convert your video first or use --skip-frame-check.")


def write_launcher(output_dir: Path, exe_mode: bool) -> None:
    if exe_mode:
        launcher = "@echo off\r\nstart \"\" \"%~dp0desktop_cat.exe\"\r\n"
    else:
        launcher = (
            "@echo off\r\n"
            "cd /d \"%~dp0\"\r\n"
            "py -3 desktop_cat.py\r\n"
            "if errorlevel 1 python desktop_cat.py\r\n"
            "pause\r\n"
        )
    (output_dir / "run_desktop_cat.bat").write_text(launcher, encoding="ascii")


def write_readme(output_dir: Path, exe_mode: bool) -> None:
    if exe_mode:
        text = """XGG Desktop Cat - portable EXE build

How to run:
1. Double-click desktop_cat.exe.
2. The app uses --windowed packaging, so no console window should open.
3. The cat window is not shown as a normal taskbar window; use the system tray icon.
4. Drag the cat with the left mouse button.
5. Double-click the tray icon to show/hide the cat.
6. Right-click the tray icon and choose Exit to close.
7. Edit config.toml to change size/fps/position/tray settings.

The target PC does not need Python, Rust, Cargo, FFmpeg, or Chocolatey.
Keep config.toml and assets\\frames next to desktop_cat.exe.
"""
    else:
        text = """XGG Desktop Cat - Python source build

How to run:
1. Install Python 3 on the target PC if it is not already installed.
2. Double-click run_desktop_cat.bat, or run: py -3 desktop_cat.py
3. The cat window appears in the system tray and not as a normal taskbar window.
4. A console window may be visible in source mode; use EXE mode if you want no console.
5. Drag the cat with the left mouse button.
6. Double-click the tray icon to show/hide the cat.
7. Right-click the tray icon and choose Exit to close.

The target PC does not need Rust, Cargo, FFmpeg, or Chocolatey for runtime.
FFmpeg is only needed if you want to convert a new video into PNG frames.
"""
    (output_dir / "README.txt").write_text(text, encoding="utf-8")


def package_source(output_dir: Path, frames_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "desktop_cat.py", output_dir / "desktop_cat.py")
    shutil.copy2(ROOT / "config.toml", output_dir / "config.toml")
    (output_dir / "scripts").mkdir(exist_ok=True)
    shutil.copy2(ROOT / "scripts" / "convert_video_to_frames.py", output_dir / "scripts" / "convert_video_to_frames.py")
    copy_tree(frames_dir, output_dir / "assets" / "frames")
    write_launcher(output_dir, exe_mode=False)
    write_readme(output_dir, exe_mode=False)


def package_exe(output_dir: Path, frames_dir: Path) -> None:
    pyinstaller = shutil.which("pyinstaller")
    command_prefix: list[str]
    if pyinstaller:
        command_prefix = [pyinstaller]
    else:
        command_prefix = [sys.executable, "-m", "PyInstaller"]

    build_dir = ROOT / "build" / "pyinstaller"
    dist_dir = ROOT / "build" / "pyinstaller-dist"
    command = [
        *command_prefix,
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        "desktop_cat",
        "--distpath",
        str(dist_dir),
        "--workpath",
        str(build_dir),
        str(ROOT / "desktop_cat.py"),
    ]
    print("Running PyInstaller. If this fails, install it on the build PC with: py -m pip install pyinstaller")
    subprocess.run(command, cwd=ROOT, check=True)

    output_dir.mkdir(parents=True, exist_ok=True)
    built_folder = dist_dir / "desktop_cat"
    built_exe = dist_dir / "desktop_cat.exe"
    if built_folder.exists():
        copy_tree(built_folder, output_dir)
    elif built_exe.exists():
        shutil.copy2(built_exe, output_dir / "desktop_cat.exe")
    else:
        raise SystemExit("PyInstaller finished, but desktop_cat output was not found.")

    shutil.copy2(ROOT / "config.toml", output_dir / "config.toml")
    copy_tree(frames_dir, output_dir / "assets" / "frames")
    write_launcher(output_dir, exe_mode=True)
    write_readme(output_dir, exe_mode=True)


def zip_folder(output_dir: Path) -> Path:
    zip_path = output_dir.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in output_dir.rglob("*"):
            if file.is_file():
                archive.write(file, file.relative_to(output_dir.parent))
    return zip_path


def main() -> int:
    args = build_parser().parse_args()
    output_dir = (ROOT / args.output_dir).resolve()
    frames_dir = (ROOT / args.frames_dir).resolve()
    ensure_frames(frames_dir, args.skip_frame_check)

    if output_dir.exists():
        shutil.rmtree(output_dir)

    if args.mode == "source":
        package_source(output_dir, frames_dir)
    else:
        package_exe(output_dir, frames_dir)

    print(f"Portable package created: {output_dir}")
    if args.zip:
        print(f"ZIP created: {zip_folder(output_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
