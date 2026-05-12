# Win11 透明桌面小猫陪伴插件（纯 Python 版）

这个项目现在已经清理成 **Python-only**：桌面小猫运行、视频转 PNG 帧、打包给别人电脑，全部用 Python 脚本完成。

不需要：

- Rust / Cargo
- Chocolatey
- Electron / WebView
- pywin32 / Pillow / tkinter

运行时只需要 Python 3 和透明 PNG 帧；如果要把视频转换成 PNG 帧，需要 FFmpeg（可以用免安装 zip 版）。

## 目录结构

```text
desktop_cat.py                       # 桌面小猫主程序
config.toml                          # 大小、帧率、位置等配置
assets/frames/                       # 透明 PNG 帧目录
scripts/convert_video_to_frames.py   # 视频转 PNG 帧
scripts/package_portable.py          # 打包给别的电脑
scripts/check_project.py             # 本地检查脚本
```

## 第 1 步：准备透明 PNG 帧

程序播放的是 PNG 序列，不是直接播放 MP4。把透明 PNG 放到：

```text
assets/frames/frame_0001.png
assets/frames/frame_0002.png
assets/frames/frame_0003.png
...
```

如果你已经有透明通道 MP4，可以用 Python 脚本调用 FFmpeg 转换：

```bat
py -3 scripts\convert_video_to_frames.py "D:\cat\cat_alpha.mp4" --mode alpha --fps 24 --width 260 --clean
```

如果 FFmpeg 没有加入 PATH，而是免安装解压到了项目里，例如 `tools\ffmpeg\bin\ffmpeg.exe`：

```bat
py -3 scripts\convert_video_to_frames.py "D:\cat\cat_alpha.mp4" --mode alpha --fps 24 --width 260 --clean --ffmpeg "tools\ffmpeg\bin\ffmpeg.exe"
```

如果是绿幕/纯色背景视频：

```bat
py -3 scripts\convert_video_to_frames.py "D:\cat\cat_green.mp4" --mode chroma --chroma-color 0x00FF00 --similarity 0.18 --blend 0.06 --fps 24 --width 260 --clean
```

> 普通复杂背景视频不能靠 FFmpeg 自动智能抠猫，需要先用剪映/CapCut、AE、Runway、Unscreen 等工具抠除背景，再导出透明视频或透明 PNG 序列。

## 第 2 步：运行桌面小猫

在项目根目录运行：

```bat
py -3 desktop_cat.py
```

运行后：

- 小猫窗口使用工具窗口样式，不会出现在下方任务栏。
- 直接用 `py -3 desktop_cat.py` 运行时可能会有命令行窗口；打包成 EXE 后不会显示命令行窗口。
- 右下角系统托盘会出现 `XGG Desktop Cat` 图标。
- 鼠标左键拖动小猫。
- 双击托盘图标可以显示/隐藏小猫。
- 右键托盘图标可以选择 `Show/Hide Cat` 或 `Exit`。
- 按 `Esc` 也可以退出。
- 如果 `click_through = true`，鼠标会穿透小猫，但也不能拖动。

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
tray_icon = true
start_hidden = false
```

说明：

- `width`：显示宽度；高度按 PNG 原比例计算。
- `fps`：动画帧率，建议 12～24，越低越省资源。
- `topmost`：是否置顶。
- `click_through`：是否鼠标穿透。
- `start_x` / `start_y`：启动位置。
- `frames_dir`：PNG 帧目录。
- `tray_icon`：是否显示系统托盘图标；建议保持 `true`，方便从托盘退出。
- `start_hidden`：是否启动后先隐藏小猫，只保留托盘图标；设为 `true` 后可双击托盘图标显示小猫。

## 打包给别的电脑

有两种方式。

### 方式 A：源码便携包（最轻）

目标电脑需要安装 Python 3，但不需要 Rust、FFmpeg、Chocolatey。

```bat
py -3 scripts\package_portable.py --mode source --zip
```

生成：

```text
dist/desktop-cat-portable.zip
```

发给别人后，对方解压，双击 `run_desktop_cat.bat` 或运行：

```bat
py -3 desktop_cat.py
```

### 方式 B：EXE 便携包（目标电脑不用装 Python）

如果你想发给完全没有 Python 的电脑，在你的打包电脑上安装 PyInstaller：

```bat
py -3 -m pip install pyinstaller
```

然后打包：

```bat
py -3 scripts\package_portable.py --mode exe --zip
```

生成：

```text
dist/desktop-cat-portable.zip
```

对方解压后双击 `desktop_cat.exe` 即可。EXE 使用 `--windowed` 打包，不会打开命令行窗口；程序图标会在系统托盘里，右键托盘图标点 `Exit` 可以关闭。

> PyInstaller 只需要装在你的打包电脑上；目标电脑不需要 Python、Rust、FFmpeg、Chocolatey。

## 本地检查

```bat
py -3 scripts\check_project.py
```

这个检查会编译 Python 文件并确认 `config.toml` 和 `assets/frames` 存在。
