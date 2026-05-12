# Win11 透明桌面小猫陪伴插件

这是一个轻量级 Windows 11 桌面宠物 EXE：把已抠除背景的小猫视频转换成透明 PNG 帧后，程序会在桌面上显示一个不挡视野、可随时拖动、低内存占用的小猫动画窗口。

## 为什么不用 Electron / WebView

为了尽量少占内存，本项目使用 Rust + Win32 原生透明分层窗口，不内置浏览器内核。运行时只加载当前帧 PNG，不一次性把整段视频读进内存。

## 准备素材

把你抠除背景后的视频转换成 PNG 序列，放到：

```text
assets/frames/frame_0001.png
assets/frames/frame_0002.png
assets/frames/frame_0003.png
...
```

推荐用 FFmpeg：

```powershell
mkdir assets\frames
ffmpeg -i cat_with_alpha.webm -vf "fps=24,scale=320:-1" assets\frames\frame_%04d.png
```

> 如果原视频没有透明通道，需要先用剪映、After Effects、Runway、CapCut 等工具抠除背景并导出带 alpha 的视频，或直接导出透明 PNG 序列。

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
