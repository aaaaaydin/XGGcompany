<#
.SYNOPSIS
Convert a cat video into PNG frames for xgg-desktop-cat.

.DESCRIPTION
This script is intentionally FFmpeg-only so the desktop pet app stays tiny.
It supports three common cases:
  - Alpha: the input video already has transparency (for example MP4/WebM/ProRes with alpha).
  - Chroma: the input has a single-color background such as green screen.
  - None: export normal PNG frames without removing the background.

This file intentionally uses ASCII-only messages so Windows PowerShell 5.1 can
parse it correctly even when the file is opened with the system ANSI code page.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File scripts\convert-video-to-frames.ps1 -Input "D:\cat\cat_alpha.mp4" -Mode Alpha -Fps 24 -Width 260 -Clean

Converts a transparent-channel MP4 into assets\frames\frame_0001.png, frame_0002.png, and so on.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File scripts\convert-video-to-frames.ps1 -Input "D:\cat\cat_alpha.mp4" -Mode Alpha -Fps 24 -Width 260 -Clean -FfmpegPath "tools\ffmpeg\bin\ffmpeg.exe"

Uses a portable ffmpeg.exe without requiring Chocolatey or PATH changes.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File scripts\convert-video-to-frames.ps1 -Input "D:\cat\cat_green.mp4" -Mode Chroma -ChromaColor 0x00FF00 -Similarity 0.18 -Blend 0.06 -Fps 24 -Width 260 -Clean

Removes a green screen background and exports transparent PNG frames.
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$Input,

    [string]$OutputDir = "assets\frames",

    [ValidateSet("Alpha", "Chroma", "None")]
    [string]$Mode = "Alpha",

    [int]$Fps = 24,

    [int]$Width = 260,

    # Optional path to ffmpeg.exe. Use this for portable FFmpeg zip builds.
    [string]$FfmpegPath = "ffmpeg",

    # Chroma-key background color in FFmpeg hex form. Common values:
    # green: 0x00FF00, blue: 0x0000FF, white: 0xFFFFFF, black: 0x000000
    [string]$ChromaColor = "0x00FF00",

    # Larger similarity removes more colors around ChromaColor.
    [double]$Similarity = 0.18,

    # Larger blend softens the removed edge.
    [double]$Blend = 0.06,

    # Delete old frame_*.png files before exporting new frames.
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

if ($FfmpegPath -eq "ffmpeg") {
    if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
        throw "ffmpeg was not found. Install FFmpeg, add it to PATH, or pass -FfmpegPath path\to\ffmpeg.exe."
    }
} elseif (-not (Test-Path -LiteralPath $FfmpegPath)) {
    throw "ffmpeg.exe was not found at: $FfmpegPath"
}

if (-not (Test-Path -LiteralPath $Input)) {
    throw "Input video was not found: $Input"
}

if ($Fps -lt 1) {
    throw "Fps must be greater than 0."
}

if ($Width -lt 1) {
    throw "Width must be greater than 0."
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

if ($Clean) {
    Remove-Item -Path (Join-Path $OutputDir "frame_*.png") -Force -ErrorAction SilentlyContinue
}

$scale = "scale={0}:-1:flags=lanczos" -f $Width
switch ($Mode) {
    "Alpha"  { $filter = "fps={0},{1},format=rgba" -f $Fps, $scale }
    "Chroma" { $filter = "fps={0},{1},chromakey={2}:{3}:{4},format=rgba" -f $Fps, $scale, $ChromaColor, $Similarity, $Blend }
    "None"   { $filter = "fps={0},{1},format=rgba" -f $Fps, $scale }
}

$outputPattern = Join-Path $OutputDir "frame_%04d.png"

Write-Host "Input : $Input"
Write-Host "Output: $outputPattern"
Write-Host "Mode  : $Mode"
Write-Host "Filter: $filter"
Write-Host "FFmpeg: $FfmpegPath"

& $FfmpegPath -hide_banner -y -i $Input -vf $filter -start_number 1 $outputPattern

if ($LASTEXITCODE -ne 0) {
    throw "FFmpeg conversion failed with exit code: $LASTEXITCODE"
}

Write-Host "Done. PNG frames were written to: $OutputDir"
Write-Host "Next: run cargo run --release, or run xgg-desktop-cat.exe next to config.toml and assets\frames."
