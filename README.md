# Win11 透明桌面小猫陪伴插件

这是一个轻量级 Windows 11 桌面宠物 EXE：把已抠除背景的小猫视频转换成透明 PNG 帧后，程序会在桌面上显示一个不挡视野、可随时拖动、低内存占用的小猫动画窗口。

## 为什么不用 Electron / WebView

为了尽量少占内存，本项目使用 Rust + Win32 原生透明分层窗口，不内置浏览器内核。运行时只加载当前帧 PNG，不一次性把整段视频读进内存。

## 我只有视频，怎么转换成透明 PNG 序列？

先判断你的视频属于哪一种：

1. **视频本身已经有透明通道**：例如导出的 `.webm`、`.mov`、`.mkv` 带 alpha。这种最简单，直接转 PNG，透明会保留。
2. **视频背景是纯色**：例如绿幕、蓝幕、纯白、纯黑背景。可以用 FFmpeg 的 chroma key 抠掉这个颜色。
3. **普通视频，背景复杂**：FFmpeg 不能自动“智能抠猫”。需要先用剪映/CapCut、After Effects、DaVinci Resolve、Runway、Unscreen 等工具做背景移除，再导出带 alpha 的视频或 PNG 序列。

### 方法 A：用项目自带 PowerShell 脚本（推荐）

先安装 FFmpeg，并确认 PowerShell 里能运行：

```powershell
ffmpeg -version
```

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
