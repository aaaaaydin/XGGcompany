<#
.SYNOPSIS
Build a portable xgg-desktop-cat package for another Windows PC.

.DESCRIPTION
Run this on your own development/build machine after you have already generated
assets\frames\frame_*.png. The target user's computer does not need Rust, Cargo,
FFmpeg, Chocolatey, or any other development environment. They only need the
portable folder or zip created by this script.

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
        throw "未找到 cargo。请在你的开发电脑安装 Rust，或去掉 -Build 并手动提供已编译好的 exe。"
    }
    & cargo build --release
    if ($LASTEXITCODE -ne 0) {
        throw "cargo build --release 失败，退出码：$LASTEXITCODE"
    }
}

if (-not (Test-Path -LiteralPath $ExePath)) {
    throw "找不到 EXE：$ExePath。请先运行 cargo build --release，或用 -ExePath 指向已有 exe。"
}

if (-not (Test-Path -LiteralPath $ConfigPath)) {
    throw "找不到配置文件：$ConfigPath"
}

if (-not (Test-Path -LiteralPath $FramesDir)) {
    throw "找不到 PNG 帧目录：$FramesDir。请先把透明 PNG 序列放到 assets\frames。"
}

$pngFrames = Get-ChildItem -LiteralPath $FramesDir -Filter "*.png" -File -ErrorAction SilentlyContinue
if (-not $pngFrames) {
    throw "PNG 帧目录里没有 .png 文件：$FramesDir。请先运行 convert-video-to-frames.ps1。"
}

if (Test-Path -LiteralPath $OutputDir) {
    Remove-Item -LiteralPath $OutputDir -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $OutputDir "assets\frames") | Out-Null

Copy-Item -LiteralPath $ExePath -Destination (Join-Path $OutputDir "xgg-desktop-cat.exe") -Force
Copy-Item -LiteralPath $ConfigPath -Destination (Join-Path $OutputDir "config.toml") -Force
Copy-Item -Path (Join-Path $FramesDir "*.png") -Destination (Join-Path $OutputDir "assets\frames") -Force

$readmePath = Join-Path $OutputDir "使用说明.txt"
@"
XGG 桌面小猫 - 免安装版

使用方法：
1. 双击 xgg-desktop-cat.exe 启动。
2. 鼠标左键拖动小猫移动位置。
3. 按 Esc 退出。
4. 如果想改大小/帧率/位置，编辑 config.toml 后重新打开 exe。

这个文件夹已经包含运行需要的全部内容：
- xgg-desktop-cat.exe
- config.toml
- assets\frames\*.png

目标电脑不需要安装 Rust、Cargo、FFmpeg、Chocolatey。
请不要只复制 exe；必须把 config.toml 和 assets 文件夹放在 exe 同级目录。
"@ | Set-Content -LiteralPath $readmePath -Encoding UTF8

Write-Host "便携版已生成：$OutputDir"
Write-Host "包含 $($pngFrames.Count) 张 PNG 帧。"

if ($Zip) {
    $zipPath = "$OutputDir.zip"
    if (Test-Path -LiteralPath $zipPath) {
        Remove-Item -LiteralPath $zipPath -Force
    }
    Compress-Archive -Path (Join-Path $OutputDir "*") -DestinationPath $zipPath -Force
    Write-Host "ZIP 已生成：$zipPath"
}
