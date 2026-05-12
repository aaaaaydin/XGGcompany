@echo off
setlocal enabledelayedexpansion

REM Convert a video with an existing alpha channel into PNG frames without PowerShell.
REM Usage:
REM   scripts\convert-video-to-frames.cmd "D:\cat\cat_alpha.mp4" [fps] [width] [output_dir] [ffmpeg_exe]
REM Example with ffmpeg in PATH:
REM   scripts\convert-video-to-frames.cmd "D:\cat\cat_alpha.mp4" 24 260 assets\frames
REM Example with portable ffmpeg next to the project:
REM   scripts\convert-video-to-frames.cmd "D:\cat\cat_alpha.mp4" 24 260 assets\frames tools\ffmpeg\bin\ffmpeg.exe

if "%~1"=="" (
  echo Usage: %~nx0 INPUT_VIDEO [FPS] [WIDTH] [OUTPUT_DIR] [FFMPEG_EXE]
  echo Example: %~nx0 "D:\cat\cat_alpha.mp4" 24 260 assets\frames
  exit /b 2
)

set "INPUT=%~1"
set "FPS=%~2"
set "WIDTH=%~3"
set "OUTPUT_DIR=%~4"
set "FFMPEG=%~5"

if "%FPS%"=="" set "FPS=24"
if "%WIDTH%"=="" set "WIDTH=260"
if "%OUTPUT_DIR%"=="" set "OUTPUT_DIR=assets\frames"
if "%FFMPEG%"=="" set "FFMPEG=ffmpeg"

if not exist "%INPUT%" (
  echo Input video not found: %INPUT%
  exit /b 1
)

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

"%FFMPEG%" -hide_banner -y -i "%INPUT%" -vf "fps=%FPS%,scale=%WIDTH%:-1:flags=lanczos,format=rgba" -start_number 1 "%OUTPUT_DIR%\frame_%%04d.png"
if errorlevel 1 (
  echo FFmpeg conversion failed.
  exit /b 1
)

echo Done. PNG frames were written to %OUTPUT_DIR%.
echo Next: run xgg-desktop-cat.exe or cargo run --release.
