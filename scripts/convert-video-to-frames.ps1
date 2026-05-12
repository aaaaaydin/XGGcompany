<#
.SYNOPSIS
Convert a cat video into PNG frames for xgg-desktop-cat.

.DESCRIPTION
This script is intentionally FFmpeg-only so the desktop pet app stays tiny.
It supports three common cases:
  - Alpha: the input video already has transparency (for example MP4/WebM/ProRes with alpha).
  - Chroma: the input has a single-color background such as green screen.
  - None: export normal PNG frames without removing the background.

If your video is a normal camera/video clip with a complex background, remove the
background first in a video editor/AI matting tool, export a video with alpha or a
PNG sequence, then use Mode Alpha if needed.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File scripts\convert-video-to-frames.ps1 -Input "D:\cat\cat_alpha.mp4" -Mode Alpha -Fps 24 -Width 260 -Clean

Converts a transparent-channel MP4 into assets\frames\frame_0001.png, frame_0002.png, and so on.

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

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    throw "未找到 ffmpeg。请先安装 FFmpeg，并确认 ffmpeg.exe 已加入 PATH。"
}

if (-not (Test-Path -LiteralPath $Input)) {
    throw "输入视频不存在：$Input"
}

if ($Fps -lt 1) {
    throw "Fps 必须大于 0。"
}

if ($Width -lt 1) {
    throw "Width 必须大于 0。"
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

if ($Clean) {
    Remove-Item -Path (Join-Path $OutputDir "frame_*.png") -Force -ErrorAction SilentlyContinue
}

$scale = "scale=$($Width):-1:flags=lanczos"
$filter = switch ($Mode) {
    "Alpha"  { "fps=$Fps,$scale,format=rgba" }
    "Chroma" { "fps=$Fps,$scale,chromakey=$($ChromaColor):$($Similarity):$($Blend),format=rgba" }
    "None"   { "fps=$Fps,$scale,format=rgba" }
}

$outputPattern = Join-Path $OutputDir "frame_%04d.png"

Write-Host "Input : $Input"
Write-Host "Output: $outputPattern"
Write-Host "Mode  : $Mode"
Write-Host "Filter: $filter"

& ffmpeg -hide_banner -y -i $Input -vf $filter -start_number 1 $outputPattern

if ($LASTEXITCODE -ne 0) {
    throw "FFmpeg 转换失败，退出码：$LASTEXITCODE"
}

Write-Host "完成：PNG 帧已输出到 $OutputDir"
Write-Host "下一步：运行 cargo run --release，或把 exe、config.toml、assets\frames 放在一起运行。"
