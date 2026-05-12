"""Lightweight Windows desktop cat companion implemented with Python stdlib only.

Run on Windows 11 from the project root after generating PNG frames:
    py -3 desktop_cat.py

The app uses ctypes + native Win32/GDI+ layered windows. It does not require
Rust, Cargo, pywin32, Pillow, tkinter, or any third-party Python package.
"""

from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes
from pathlib import Path


class AppConfig:
    def __init__(self) -> None:
        self.width = 260
        self.fps = 24
        self.topmost = True
        self.click_through = False
        self.start_x = 1200
        self.start_y = 620
        self.frames_dir = Path("assets/frames")


def load_config(path: Path = Path("config.toml")) -> AppConfig:
    config = AppConfig()
    if not path.exists():
        return config

    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        key, value = [part.strip() for part in line.split("=", 1)]
        value = value.strip('"')
        if key == "width":
            config.width = _parse_int(value, config.width)
        elif key == "fps":
            config.fps = _parse_int(value, config.fps)
        elif key == "topmost":
            config.topmost = _parse_bool(value, config.topmost)
        elif key == "click_through":
            config.click_through = _parse_bool(value, config.click_through)
        elif key == "start_x":
            config.start_x = _parse_int(value, config.start_x)
        elif key == "start_y":
            config.start_y = _parse_int(value, config.start_y)
        elif key == "frames_dir":
            config.frames_dir = Path(value)
    return config


def _parse_int(value: str, fallback: int) -> int:
    try:
        return int(value)
    except ValueError:
        return fallback


def _parse_bool(value: str, fallback: bool) -> bool:
    lowered = value.lower()
    if lowered in {"true", "1", "yes", "on"}:
        return True
    if lowered in {"false", "0", "no", "off"}:
        return False
    return fallback


def main() -> int:
    if sys.platform != "win32":
        print("desktop_cat.py is a Windows desktop pet. Please run it on Windows 11.")
        return 1
    return run_windows(load_config())


if sys.platform == "win32":
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    gdiplus = ctypes.WinDLL("gdiplus", use_last_error=True)

    LRESULT = getattr(wintypes, "LRESULT", ctypes.c_ssize_t)
    UINT_PTR = getattr(wintypes, "UINT_PTR", wintypes.WPARAM)
    HICON = getattr(wintypes, "HICON", wintypes.HANDLE)
    HCURSOR = getattr(wintypes, "HCURSOR", wintypes.HANDLE)
    HBRUSH = getattr(wintypes, "HBRUSH", wintypes.HANDLE)
    HGDIOBJ = getattr(wintypes, "HGDIOBJ", wintypes.HANDLE)
    COLORREF = getattr(wintypes, "COLORREF", wintypes.DWORD)

    WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

    class POINT(ctypes.Structure):
        _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

    class SIZE(ctypes.Structure):
        _fields_ = [("cx", wintypes.LONG), ("cy", wintypes.LONG)]

    class MSG(ctypes.Structure):
        _fields_ = [
            ("hwnd", wintypes.HWND),
            ("message", wintypes.UINT),
            ("wParam", wintypes.WPARAM),
            ("lParam", wintypes.LPARAM),
            ("time", wintypes.DWORD),
            ("pt", POINT),
        ]

    class WNDCLASSW(ctypes.Structure):
        _fields_ = [
            ("style", wintypes.UINT),
            ("lpfnWndProc", WNDPROC),
            ("cbClsExtra", ctypes.c_int),
            ("cbWndExtra", ctypes.c_int),
            ("hInstance", wintypes.HINSTANCE),
            ("hIcon", HICON),
            ("hCursor", HCURSOR),
            ("hbrBackground", HBRUSH),
            ("lpszMenuName", wintypes.LPCWSTR),
            ("lpszClassName", wintypes.LPCWSTR),
        ]

    class BLENDFUNCTION(ctypes.Structure):
        _fields_ = [
            ("BlendOp", ctypes.c_byte),
            ("BlendFlags", ctypes.c_byte),
            ("SourceConstantAlpha", ctypes.c_byte),
            ("AlphaFormat", ctypes.c_byte),
        ]

    class GDIPLUS_STARTUP_INPUT(ctypes.Structure):
        _fields_ = [
            ("GdiplusVersion", wintypes.UINT),
            ("DebugEventCallback", ctypes.c_void_p),
            ("SuppressBackgroundThread", wintypes.BOOL),
            ("SuppressExternalCodecs", wintypes.BOOL),
        ]

    kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
    kernel32.GetModuleHandleW.restype = wintypes.HMODULE
    user32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASSW)]
    user32.RegisterClassW.restype = wintypes.ATOM
    user32.CreateWindowExW.argtypes = [
        wintypes.DWORD,
        wintypes.LPCWSTR,
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.HWND,
        wintypes.HMENU,
        wintypes.HINSTANCE,
        wintypes.LPVOID,
    ]
    user32.CreateWindowExW.restype = wintypes.HWND
    user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.DefWindowProcW.restype = LRESULT
    user32.LoadCursorW.argtypes = [wintypes.HINSTANCE, ctypes.c_void_p]
    user32.LoadCursorW.restype = HCURSOR
    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.SetTimer.argtypes = [wintypes.HWND, UINT_PTR, wintypes.UINT, ctypes.c_void_p]
    user32.KillTimer.argtypes = [wintypes.HWND, UINT_PTR]
    user32.GetMessageW.argtypes = [ctypes.POINTER(MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
    user32.TranslateMessage.argtypes = [ctypes.POINTER(MSG)]
    user32.DispatchMessageW.argtypes = [ctypes.POINTER(MSG)]
    user32.GetDC.argtypes = [wintypes.HWND]
    user32.GetDC.restype = wintypes.HDC
    user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
    user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.DestroyWindow.argtypes = [wintypes.HWND]
    user32.MessageBoxW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT]
    user32.UpdateLayeredWindow.argtypes = [
        wintypes.HWND,
        wintypes.HDC,
        ctypes.POINTER(POINT),
        ctypes.POINTER(SIZE),
        wintypes.HDC,
        ctypes.POINTER(POINT),
        COLORREF,
        ctypes.POINTER(BLENDFUNCTION),
        wintypes.DWORD,
    ]
    user32.UpdateLayeredWindow.restype = wintypes.BOOL

    gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
    gdi32.CreateCompatibleDC.restype = wintypes.HDC
    gdi32.SelectObject.argtypes = [wintypes.HDC, HGDIOBJ]
    gdi32.SelectObject.restype = HGDIOBJ
    gdi32.DeleteObject.argtypes = [HGDIOBJ]
    gdi32.DeleteDC.argtypes = [wintypes.HDC]

    gdiplus.GdiplusStartup.argtypes = [ctypes.POINTER(ctypes.c_ulonglong), ctypes.POINTER(GDIPLUS_STARTUP_INPUT), ctypes.c_void_p]
    gdiplus.GdiplusStartup.restype = ctypes.c_int
    gdiplus.GdiplusShutdown.argtypes = [ctypes.c_ulonglong]
    gdiplus.GdipCreateBitmapFromFile.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_void_p)]
    gdiplus.GdipCreateBitmapFromFile.restype = ctypes.c_int
    gdiplus.GdipGetImageWidth.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.UINT)]
    gdiplus.GdipGetImageHeight.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.UINT)]
    gdiplus.GdipGetImageThumbnail.argtypes = [
        ctypes.c_void_p,
        wintypes.UINT,
        wintypes.UINT,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    gdiplus.GdipCreateHBITMAPFromBitmap.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.HBITMAP), wintypes.DWORD]
    gdiplus.GdipDisposeImage.argtypes = [ctypes.c_void_p]

    WS_POPUP = 0x80000000
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020
    WS_EX_TOOLWINDOW = 0x00000080
    WS_EX_TOPMOST = 0x00000008
    WS_EX_NOACTIVATE = 0x08000000
    SW_SHOW = 5
    WM_DESTROY = 0x0002
    WM_CLOSE = 0x0010
    WM_TIMER = 0x0113
    WM_LBUTTONDOWN = 0x0201
    WM_NCLBUTTONDOWN = 0x00A1
    WM_KEYDOWN = 0x0100
    VK_ESCAPE = 0x1B
    HTCAPTION = 2
    TIMER_ID = 1
    ULW_ALPHA = 0x00000002
    AC_SRC_OVER = 0
    AC_SRC_ALPHA = 1
    CS_VREDRAW = 0x0001
    CS_HREDRAW = 0x0002
    IDC_SIZEALL = 32646
    MB_ICONERROR = 0x00000010

    _state = None
    _wndproc = None

    class WindowState:
        def __init__(self, config: AppConfig, frames: list[Path], token: ctypes.c_ulonglong) -> None:
            self.config = config
            self.frames = frames
            self.frame_index = 0
            self.hwnd = None
            self.gdiplus_token = token

        def next_frame(self) -> Path:
            frame = self.frames[self.frame_index]
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            return frame


def run_windows(config: AppConfig) -> int:
    global _state, _wndproc

    frames = sorted(config.frames_dir.glob("*.png"))
    if not frames:
        _message_box(f"No PNG frames found in: {config.frames_dir}")
        return 1

    token = ctypes.c_ulonglong(0)
    gdiplus_input = GDIPLUS_STARTUP_INPUT(1, None, False, False)
    status = gdiplus.GdiplusStartup(ctypes.byref(token), ctypes.byref(gdiplus_input), None)
    if status != 0:
        _message_box(f"GDI+ startup failed: {status}")
        return 1

    _state = WindowState(config, frames, token)
    _wndproc = WNDPROC(_window_proc)

    instance = kernel32.GetModuleHandleW(None)
    class_name = "XggPythonDesktopCatWindow"
    wc = WNDCLASSW()
    wc.style = CS_HREDRAW | CS_VREDRAW
    wc.lpfnWndProc = _wndproc
    wc.hInstance = instance
    wc.hCursor = user32.LoadCursorW(None, ctypes.c_void_p(IDC_SIZEALL))
    wc.lpszClassName = class_name
    user32.RegisterClassW(ctypes.byref(wc))

    ex_style = WS_EX_LAYERED | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
    if config.topmost:
        ex_style |= WS_EX_TOPMOST
    if config.click_through:
        ex_style |= WS_EX_TRANSPARENT

    hwnd = user32.CreateWindowExW(
        ex_style,
        class_name,
        "XGG Python Desktop Cat",
        WS_POPUP,
        config.start_x,
        config.start_y,
        config.width,
        config.width,
        None,
        None,
        instance,
        None,
    )
    if not hwnd:
        gdiplus.GdiplusShutdown(token)
        _message_box("Failed to create layered window.")
        return 1

    _state.hwnd = hwnd
    _render_next_frame(_state)
    user32.ShowWindow(hwnd, SW_SHOW)
    user32.SetTimer(hwnd, TIMER_ID, max(10, int(1000 / max(1, config.fps))), None)

    msg = MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

    gdiplus.GdiplusShutdown(token)
    return 0


def _window_proc(hwnd, msg, wparam, lparam):
    if msg == WM_TIMER and wparam == TIMER_ID and _state is not None:
        _render_next_frame(_state)
        return 0
    if msg == WM_LBUTTONDOWN:
        user32.ReleaseCapture()
        user32.SendMessageW(hwnd, WM_NCLBUTTONDOWN, HTCAPTION, 0)
        return 0
    if msg == WM_KEYDOWN and wparam == VK_ESCAPE:
        user32.DestroyWindow(hwnd)
        return 0
    if msg == WM_CLOSE:
        user32.DestroyWindow(hwnd)
        return 0
    if msg == WM_DESTROY:
        user32.KillTimer(hwnd, TIMER_ID)
        user32.PostQuitMessage(0)
        return 0
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)


def _render_next_frame(state: WindowState) -> None:
    _render_png_to_layered_window(state.hwnd, state.next_frame(), state.config.width)


def _render_png_to_layered_window(hwnd, path: Path, target_width: int) -> None:
    bitmap = ctypes.c_void_p()
    status = gdiplus.GdipCreateBitmapFromFile(str(path.resolve()), ctypes.byref(bitmap))
    if status != 0 or not bitmap:
        return

    width = wintypes.UINT(0)
    height = wintypes.UINT(0)
    gdiplus.GdipGetImageWidth(bitmap, ctypes.byref(width))
    gdiplus.GdipGetImageHeight(bitmap, ctypes.byref(height))

    draw_image = bitmap
    if target_width > 0 and width.value > 0 and target_width != width.value:
        target_height = max(1, round(target_width * (height.value / width.value)))
        thumbnail = ctypes.c_void_p()
        status = gdiplus.GdipGetImageThumbnail(bitmap, target_width, target_height, ctypes.byref(thumbnail), None, None)
        if status == 0 and thumbnail:
            draw_image = thumbnail
            width = wintypes.UINT(target_width)
            height = wintypes.UINT(target_height)

    hbitmap = wintypes.HBITMAP()
    status = gdiplus.GdipCreateHBITMAPFromBitmap(draw_image, ctypes.byref(hbitmap), 0)
    if draw_image.value != bitmap.value:
        gdiplus.GdipDisposeImage(draw_image)
    gdiplus.GdipDisposeImage(bitmap)
    if status != 0 or not hbitmap:
        return

    screen_dc = user32.GetDC(None)
    mem_dc = gdi32.CreateCompatibleDC(screen_dc)
    old = gdi32.SelectObject(mem_dc, hbitmap)
    size = SIZE(width.value, height.value)
    src = POINT(0, 0)
    blend = BLENDFUNCTION(AC_SRC_OVER, 0, 255, AC_SRC_ALPHA)
    user32.UpdateLayeredWindow(hwnd, screen_dc, None, ctypes.byref(size), mem_dc, ctypes.byref(src), 0, ctypes.byref(blend), ULW_ALPHA)
    gdi32.SelectObject(mem_dc, old)
    gdi32.DeleteObject(hbitmap)
    gdi32.DeleteDC(mem_dc)
    user32.ReleaseDC(None, screen_dc)


def _message_box(text: str) -> None:
    user32.MessageBoxW(None, text, "XGG Desktop Cat", MB_ICONERROR)


if __name__ == "__main__":
    raise SystemExit(main())
