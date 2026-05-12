# Win11 透明桌面小猫陪伴插件

这是一个轻量级 Windows 11 桌面宠物 EXE：把已抠除背景的小猫视频转换成透明 PNG 帧后，程序会在桌面上显示一个不挡视野、可随时拖动、低内存占用的小猫动画窗口。

## 为什么不用 Electron / WebView

为了尽量少占内存，本项目使用 Rust + Win32 原生透明分层窗口，不内置浏览器内核。运行时只加载当前帧 PNG，不一次性把整段视频读进内存。

## 我只有视频，怎么转换成透明 PNG 序列？

先判断你的视频属于哪一种：

1. **视频本身已经有透明通道**：例如导出的 `.webm`、`.mov`、`.mkv` 带 alpha。这种最简单，直接转 PNG，透明会保留。
2. **视频背景是纯色**：例如绿幕、蓝幕、纯白、纯黑背景。可以用 FFmpeg 的 chroma key 抠掉这个颜色。
3. **普通视频，背景复杂**：FFmpeg 不能自动“智能抠猫”。需要先用剪映/CapCut、After Effects、DaVinci Resolve、Runway、Unscreen 等工具做背景移除，再导出带 alpha 的视频或 PNG 序列。

### 方法 A：用项目自带脚本（推荐，PowerShell 或 CMD 都行）

先准备 FFmpeg。**不需要 Chocolatey**，Chocolatey 只是其中一种安装方式；你也可以下载 FFmpeg 的 zip 免安装版，解压后直接用里面的 `ffmpeg.exe`。

如果你把 FFmpeg 加进了 PATH，可以在 PowerShell 或 CMD 里检查：

```powershell
ffmpeg -version
```

如果你不想配置 PATH，也可以把 `ffmpeg.exe` 放到项目里的 `tools\ffmpeg\bin\ffmpeg.exe`，然后用下面的 PowerShell `-FfmpegPath` 参数或 CMD 脚本传入这个 exe 路径。

> 如果你看到 `杈撳叆瑙嗛...` 这种乱码 ParserError，通常是 Windows PowerShell 5.1 按系统 ANSI 编码读取 UTF-8 脚本导致的。本项目的 `.ps1` 已改成 ASCII-only 提示文本，更新脚本后重新运行即可。

#### A1. 视频已经透明（你的透明通道 MP4 用这个）

在项目根目录打开 PowerShell，然后把 `-Input` 后面的路径换成你自己的透明 MP4 路径：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\convert-video-to-frames.ps1 `
  -Input "D:\cat\cat_alpha.mp4" `
  -Mode Alpha `
  -Fps 24 `
  -Width 260 `
  -Clean
```

一行版本：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\convert-video-to-frames.ps1 -Input "D:\cat\cat_alpha.mp4" -Mode Alpha -Fps 24 -Width 260 -Clean
```

如果你没有把 FFmpeg 加进 PATH，而是使用免安装版本：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\convert-video-to-frames.ps1 -Input "D:\cat\cat_alpha.mp4" -Mode Alpha -Fps 24 -Width 260 -Clean -FfmpegPath "tools\ffmpeg\bin\ffmpeg.exe"
```

##### 不想用 PowerShell：用 CMD 也可以

如果 `ffmpeg` 已经在 PATH 里，打开 `cmd.exe` 运行：

```bat
scripts\convert-video-to-frames.cmd "D:\cat\cat_alpha.mp4" 24 260 assets\frames
```

如果你用的是免安装 FFmpeg，例如放在 `tools\ffmpeg\bin\ffmpeg.exe`：

```bat
scripts\convert-video-to-frames.cmd "D:\cat\cat_alpha.mp4" 24 260 assets\frames tools\ffmpeg\bin\ffmpeg.exe
```

你也可以完全不用脚本，直接运行 FFmpeg：

```bat
mkdir assets\frames 2>NUL
tools\ffmpeg\bin\ffmpeg.exe -hide_banner -y -i "D:\cat\cat_alpha.mp4" -vf "fps=24,scale=260:-1:flags=lanczos,format=rgba" -start_number 1 "assets\frames\frame_%%04d.png"
```

> 在 PowerShell 里手写这条直接 FFmpeg 命令时，输出模板用 `frame_%04d.png`；在 CMD / `.cmd` 里要写成 `frame_%%04d.png`。

运行成功后会生成：

```text
assets/frames/frame_0001.png
assets/frames/frame_0002.png
assets/frames/frame_0003.png
...
```

然后运行桌面小猫：

```powershell
cargo run --release
```

如果生成出来的 PNG 仍然是黑底/白底/不透明，说明这个 MP4 可能只是“看起来透明”，但文件里没有真实 alpha；需要先用视频软件重新导出带 alpha 的视频，或导出透明 PNG 序列。

#### A2. 绿幕/纯色背景视频

绿幕示例：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\convert-video-to-frames.ps1 `
  -Input "D:\cat\cat_green.mp4" `
  -Mode Chroma `
  -ChromaColor 0x00FF00 `
  -Similarity 0.18 `
  -Blend 0.06 `
  -Fps 24 `
  -Width 260 `
  -Clean
```

常用背景色：

- 绿幕：`0x00FF00`
- 蓝幕：`0x0000FF`
- 白底：`0xFFFFFF`
- 黑底：`0x000000`

如果边缘还有背景色残留，逐步调大 `-Similarity`，例如 `0.22`、`0.28`；如果边缘太硬，稍微调大 `-Blend`。

### 方法 B：直接用 FFmpeg 命令

视频已经有透明通道：

```powershell
mkdir assets\frames
ffmpeg -i cat_alpha.webm -vf "fps=24,scale=260:-1:flags=lanczos,format=rgba" assets\frames\frame_%04d.png
```

绿幕视频：

```powershell
mkdir assets\frames
ffmpeg -i cat_green.mp4 -vf "fps=24,scale=260:-1:flags=lanczos,chromakey=0x00FF00:0.18:0.06,format=rgba" assets\frames\frame_%04d.png
```

转换完成后目录应类似：

```text
assets/frames/frame_0001.png
assets/frames/frame_0002.png
assets/frames/frame_0003.png
...
```

> 注意：如果源视频没有透明通道、也不是纯色背景，直接转 PNG 只会得到“带原背景”的 PNG。必须先用抠像/背景移除工具处理。


## 发给别人电脑：免安装 / 不用配置环境

你只需要在**自己的电脑**上把 EXE 和透明 PNG 帧都准备好，然后打包成一个便携文件夹发给别人。别人电脑上不需要安装 Rust、Cargo、FFmpeg、Chocolatey，也不需要运行转换脚本。

PowerShell 不是运行桌面小猫的必要条件；它只是本项目提供的打包/转换辅助脚本。真正发给别人后，对方只需要双击 EXE。

目标电脑只需要收到这个结构：

```text
xgg-desktop-cat-portable\
├─ xgg-desktop-cat.exe
├─ config.toml
└─ assets\
   └─ frames\
      ├─ frame_0001.png
      ├─ frame_0002.png
      └─ ...
```

> 注意：不要只发 `xgg-desktop-cat.exe`。程序运行时还需要同级目录里的 `config.toml` 和 `assets\frames\*.png`。

### 一键打包便携版

在你自己的 Windows 开发电脑上，先确认已经生成透明 PNG 帧，然后运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\package-portable.ps1 -Build -Zip
```

脚本会：

1. 运行 `cargo build --release` 编译 EXE。
2. 复制 `xgg-desktop-cat.exe`、`config.toml`、`assets\frames\*.png`。
3. 生成 `dist\xgg-desktop-cat-portable` 文件夹。
4. 如果加了 `-Zip`，还会生成 `dist\xgg-desktop-cat-portable.zip`。

然后你把这个 zip 发给别人，对方解压后双击 `xgg-desktop-cat.exe` 就能运行。

如果你已经手动编译好了 EXE，也可以不加 `-Build`：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\package-portable.ps1 -Zip
```

### 最推荐的分工

- **你的电脑**：安装 Rust/FFmpeg，用来转换视频、编译、打包。
- **别人的电脑**：只解压 zip，双击 EXE。

这样别人完全不用配置开发环境。

## 配置

编辑 `config.toml`：

```toml
width = 260
fps = 24
topmost = true
click_through = false
start_x = 1200
start_y = 620
frames_dir = "assets/frames"
```

- `width`：桌面小猫显示宽度，高度会按 PNG 原比例自动计算。
- `fps`：动画帧率，建议 12～24，越低越省资源。
- `topmost`：是否置顶。
- `click_through`：是否鼠标穿透。设为 `true` 后不挡鼠标，但也不能拖动。
- `start_x` / `start_y`：启动位置。
- `frames_dir`：透明 PNG 帧目录；程序会按文件名排序循环播放里面所有 `.png` 文件。

## 运行与打包

开发运行：

```powershell
cargo run --release
```

生成 EXE：

```powershell
cargo build --release
```

输出文件：

```text
target\release\xgg-desktop-cat.exe
```

把以下内容放在同一个目录即可运行：

```text
xgg-desktop-cat.exe
config.toml
assets\frames\*.png
```

## 操作

- 鼠标左键拖动小猫移动位置。
- 按 `Esc` 退出。
- 关闭窗口也会退出。
