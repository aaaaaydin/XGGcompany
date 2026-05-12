<#
.SYNOPSIS
Build a portable xgg-desktop-cat package for another Windows PC.

.DESCRIPTION
Run this on your own development/build machine after you have already generated
assets\frames\frame_*.png. The target user's computer does not need Rust, Cargo,
FFmpeg, Chocolatey, or any other development environment. They only need the
portable folder or zip created by this script.

This file intentionally uses ASCII-only messages so Windows PowerShell 5.1 can
parse it correctly even when the file is opened with the system ANSI code page.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File scripts\package-portable.ps1 -Build -Zip

Builds target\release\xgg-desktop-cat.exe, copies config.toml and assets\frames,
and creates dist\xgg-desktop-cat-portable.zip.
#>

param(
    # Build the release executable before packaging. Use this on your own PC.
    [switch]$Build,

    # Create a .zip next to the portable folder.
    [switch]$Zip,

    # Output folder for the portable package.
    [string]$OutputDir = "dist\xgg-desktop-cat-portable",

    # Path to the release executable if you built it elsewhere.
    [string]$ExePath = "target\release\xgg-desktop-cat.exe",

    # Path to the config file to include.
    [string]$ConfigPath = "config.toml",

    # Path to the prepared PNG frame directory.
    [string]$FramesDir = "assets\frames"
)

$ErrorActionPreference = "Stop"

if ($Build) {
    if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
        throw "cargo was not found. Install Rust on your build PC, or remove -Build and pass -ExePath to an existing exe."
    }
    & cargo build --release
    if ($LASTEXITCODE -ne 0) {
        throw "cargo build --release failed with exit code: $LASTEXITCODE"
    }
}

if (-not (Test-Path -LiteralPath $ExePath)) {
    throw "EXE was not found: $ExePath. Run cargo build --release first, or pass -ExePath."
}

if (-not (Test-Path -LiteralPath $ConfigPath)) {
    throw "Config file was not found: $ConfigPath"
}

if (-not (Test-Path -LiteralPath $FramesDir)) {
    throw "PNG frame directory was not found: $FramesDir. Generate frames first."
}

$pngFrames = Get-ChildItem -LiteralPath $FramesDir -Filter "*.png" -File -ErrorAction SilentlyContinue
if (-not $pngFrames) {
    throw "No .png frames were found in: $FramesDir. Run convert-video-to-frames first."
}

if (Test-Path -LiteralPath $OutputDir) {
    Remove-Item -LiteralPath $OutputDir -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $OutputDir "assets\frames") | Out-Null

Copy-Item -LiteralPath $ExePath -Destination (Join-Path $OutputDir "xgg-desktop-cat.exe") -Force
Copy-Item -LiteralPath $ConfigPath -Destination (Join-Path $OutputDir "config.toml") -Force
Copy-Item -Path (Join-Path $FramesDir "*.png") -Destination (Join-Path $OutputDir "assets\frames") -Force

$readmePath = Join-Path $OutputDir "README.txt"
@"
XGG Desktop Cat - portable build

How to use:
1. Double-click xgg-desktop-cat.exe to start.
2. Drag the cat with the left mouse button.
3. Press Esc to exit.
4. Edit config.toml and restart the exe if you want to change size, fps, or position.

This folder already contains everything needed at runtime:
- xgg-desktop-cat.exe
- config.toml
- assets\frames\*.png

The target PC does not need Rust, Cargo, FFmpeg, or Chocolatey.
Do not copy only the exe. Keep config.toml and the assets folder next to the exe.
"@ | Set-Content -LiteralPath $readmePath -Encoding UTF8

Write-Host "Portable folder created: $OutputDir"
Write-Host "Included PNG frames: $($pngFrames.Count)"

if ($Zip) {
    $zipPath = "$OutputDir.zip"
    if (Test-Path -LiteralPath $zipPath) {
        Remove-Item -LiteralPath $zipPath -Force
    }
    Compress-Archive -Path (Join-Path $OutputDir "*") -DestinationPath $zipPath -Force
    Write-Host "ZIP created: $zipPath"
}
