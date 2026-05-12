use crate::AppConfig;
use std::{
    ffi::{c_void, OsStr},
    iter::once,
    os::windows::ffi::OsStrExt,
    path::{Path, PathBuf},
    ptr::{null, null_mut},
};

type Result<T> = std::result::Result<T, String>;
type Hwnd = isize;
type Hdc = isize;
type Hbitmap = isize;
type Hinstance = isize;
type Hcursor = isize;
type Hmenu = isize;
type Hgdobj = isize;
type Wparam = usize;
type Lparam = isize;
type Lresult = isize;
type Uint = u32;
type Bool = i32;

const WS_POPUP: u32 = 0x8000_0000;
const WS_EX_LAYERED: u32 = 0x0008_0000;
const WS_EX_TRANSPARENT: u32 = 0x0000_0020;
const WS_EX_TOOLWINDOW: u32 = 0x0000_0080;
const WS_EX_TOPMOST: u32 = 0x0000_0008;
const WS_EX_NOACTIVATE: u32 = 0x0800_0000;
const SW_SHOW: i32 = 5;
const WM_NCCREATE: u32 = 0x0081;
const WM_DESTROY: u32 = 0x0002;
const WM_CLOSE: u32 = 0x0010;
const WM_TIMER: u32 = 0x0113;
const WM_LBUTTONDOWN: u32 = 0x0201;
const WM_NCLBUTTONDOWN: u32 = 0x00A1;
const WM_KEYDOWN: u32 = 0x0100;
const HTCAPTION: usize = 2;
const VK_ESCAPE: usize = 0x1B;
const GWLP_USERDATA: i32 = -21;
const TIMER_ID: usize = 1;
const ULW_ALPHA: u32 = 0x0000_0002;
const AC_SRC_OVER: u8 = 0;
const AC_SRC_ALPHA: u8 = 1;
const CS_VREDRAW: u32 = 0x0001;
const CS_HREDRAW: u32 = 0x0002;
const IDC_SIZEALL: *const u16 = 32646usize as *const u16;
const MB_ICONERROR: u32 = 0x0000_0010;

#[repr(C)]
#[derive(Default, Copy, Clone)]
struct Point {
    x: i32,
    y: i32,
}

#[repr(C)]
#[derive(Default, Copy, Clone)]
struct Size {
    cx: i32,
    cy: i32,
}

#[repr(C)]
#[derive(Default, Copy, Clone)]
struct Msg {
    hwnd: Hwnd,
    message: u32,
    w_param: Wparam,
    l_param: Lparam,
    time: u32,
    pt: Point,
}

#[repr(C)]
#[derive(Copy, Clone)]
struct WndClassW {
    style: u32,
    lpfn_wnd_proc: Option<unsafe extern "system" fn(Hwnd, Uint, Wparam, Lparam) -> Lresult>,
    cb_cls_extra: i32,
    cb_wnd_extra: i32,
    h_instance: Hinstance,
    h_icon: isize,
    h_cursor: Hcursor,
    hbr_background: isize,
    lpsz_menu_name: *const u16,
    lpsz_class_name: *const u16,
}

#[repr(C)]
struct CreateStructW {
    lp_create_params: *mut c_void,
    h_instance: Hinstance,
    h_menu: Hmenu,
    hwnd_parent: Hwnd,
    cy: i32,
    cx: i32,
    y: i32,
    x: i32,
    style: i32,
    lpsz_name: *const u16,
    lpsz_class: *const u16,
    dw_ex_style: u32,
}

#[repr(C)]
struct BlendFunction {
    blend_op: u8,
    blend_flags: u8,
    source_constant_alpha: u8,
    alpha_format: u8,
}

#[repr(C)]
#[derive(Default)]
struct GdiplusStartupInput {
    gdiplus_version: u32,
    debug_event_callback: *mut c_void,
    suppress_background_thread: Bool,
    suppress_external_codecs: Bool,
}

#[link(name = "user32")]
extern "system" {
    fn RegisterClassW(lp_wnd_class: *const WndClassW) -> u16;
    fn CreateWindowExW(
        dw_ex_style: u32,
        lp_class_name: *const u16,
        lp_window_name: *const u16,
        dw_style: u32,
        x: i32,
        y: i32,
        n_width: i32,
        n_height: i32,
        hwnd_parent: Hwnd,
        hmenu: Hmenu,
        hinstance: Hinstance,
        lp_param: *mut c_void,
    ) -> Hwnd;
    fn DefWindowProcW(hwnd: Hwnd, msg: Uint, wparam: Wparam, lparam: Lparam) -> Lresult;
    fn DestroyWindow(hwnd: Hwnd) -> Bool;
    fn DispatchMessageW(lpmsg: *const Msg) -> Lresult;
    fn GetDC(hwnd: Hwnd) -> Hdc;
    fn GetMessageW(lpmsg: *mut Msg, hwnd: Hwnd, msg_filter_min: u32, msg_filter_max: u32) -> Bool;
    fn KillTimer(hwnd: Hwnd, id_event: usize) -> Bool;
    fn LoadCursorW(hinstance: Hinstance, cursor_name: *const u16) -> Hcursor;
    fn MessageBoxW(hwnd: Hwnd, text: *const u16, caption: *const u16, kind: u32) -> i32;
    fn PostQuitMessage(exit_code: i32);
    fn ReleaseCapture() -> Bool;
    fn ReleaseDC(hwnd: Hwnd, hdc: Hdc) -> i32;
    fn SendMessageW(hwnd: Hwnd, msg: Uint, wparam: Wparam, lparam: Lparam) -> Lresult;
    fn SetProcessDPIAware() -> Bool;
    fn SetTimer(hwnd: Hwnd, id_event: usize, elapse: u32, timer_func: *const c_void) -> usize;
    fn SetWindowLongPtrW(hwnd: Hwnd, index: i32, new_long: isize) -> isize;
    fn ShowWindow(hwnd: Hwnd, cmd_show: i32) -> Bool;
    fn TranslateMessage(lpmsg: *const Msg) -> Bool;
    fn UpdateLayeredWindow(
        hwnd: Hwnd,
        hdc_dst: Hdc,
        ppt_dst: *const Point,
        psize: *const Size,
        hdc_src: Hdc,
        ppt_src: *const Point,
        cr_key: u32,
        pblend: *const BlendFunction,
        flags: u32,
    ) -> Bool;
}

#[link(name = "kernel32")]
extern "system" {
    fn GetModuleHandleW(module_name: *const u16) -> Hinstance;
}

#[link(name = "gdi32")]
extern "system" {
    fn CreateCompatibleDC(hdc: Hdc) -> Hdc;
    fn DeleteDC(hdc: Hdc) -> Bool;
    fn DeleteObject(object: Hgdobj) -> Bool;
    fn SelectObject(hdc: Hdc, object: Hgdobj) -> Hgdobj;
}

#[link(name = "gdiplus")]
extern "system" {
    fn GdiplusStartup(
        token: *mut usize,
        input: *const GdiplusStartupInput,
        output: *mut c_void,
    ) -> i32;
    fn GdiplusShutdown(token: usize);
    fn GdipCreateBitmapFromFile(filename: *const u16, bitmap: *mut *mut c_void) -> i32;
    fn GdipCreateHBITMAPFromBitmap(
        bitmap: *mut c_void,
        hbm_return: *mut Hbitmap,
        background: u32,
    ) -> i32;
    fn GdipDisposeImage(image: *mut c_void) -> i32;
    fn GdipGetImageWidth(image: *mut c_void, width: *mut u32) -> i32;
    fn GdipGetImageHeight(image: *mut c_void, height: *mut u32) -> i32;
    fn GdipGetImageThumbnail(
        image: *mut c_void,
        thumb_width: u32,
        thumb_height: u32,
        thumb_image: *mut *mut c_void,
        callback: *mut c_void,
        callback_data: *mut c_void,
    ) -> i32;
}

pub fn run(config: AppConfig) -> Result<()> {
    let frames = discover_frames(&config)?;
    let gdiplus = GdiPlusSession::start()?;
    let mut state = Box::new(WindowState::new(config, frames, gdiplus));
    let raw_state = state.as_mut() as *mut WindowState;
    std::mem::forget(state);

    unsafe {
        SetProcessDPIAware();
        let instance = GetModuleHandleW(null());
        let class_name = wide("XggDesktopCatWindow");
        let cursor = LoadCursorW(0, IDC_SIZEALL);
        let window_class = WndClassW {
            style: CS_HREDRAW | CS_VREDRAW,
            lpfn_wnd_proc: Some(window_proc),
            cb_cls_extra: 0,
            cb_wnd_extra: 0,
            h_instance: instance,
            h_icon: 0,
            h_cursor: cursor,
            hbr_background: 0,
            lpsz_menu_name: null(),
            lpsz_class_name: class_name.as_ptr(),
        };
        RegisterClassW(&window_class);

        let state = &mut *raw_state;
        let mut ex_style = WS_EX_LAYERED | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE;
        if state.config.topmost {
            ex_style |= WS_EX_TOPMOST;
        }
        if state.config.click_through {
            ex_style |= WS_EX_TRANSPARENT;
        }

        let hwnd = CreateWindowExW(
            ex_style,
            class_name.as_ptr(),
            wide("XGG Desktop Cat").as_ptr(),
            WS_POPUP,
            state.config.start_x,
            state.config.start_y,
            state.config.width,
            state.config.width,
            0,
            0,
            instance,
            raw_state.cast(),
        );
        if hwnd == 0 {
            drop(Box::from_raw(raw_state));
            return Err("创建透明窗口失败".to_string());
        }

        state.hwnd = hwnd;
        render_next_frame(state)?;
        ShowWindow(hwnd, SW_SHOW);
        SetTimer(
            hwnd,
            TIMER_ID,
            (1000 / state.config.fps.max(1)).max(10),
            null(),
        );

        let mut msg = Msg::default();
        while GetMessageW(&mut msg, 0, 0, 0) > 0 {
            TranslateMessage(&msg);
            DispatchMessageW(&msg);
        }
    }

    Ok(())
}

struct GdiPlusSession {
    token: usize,
}

impl GdiPlusSession {
    fn start() -> Result<Self> {
        unsafe {
            let mut token = 0;
            let input = GdiplusStartupInput {
                gdiplus_version: 1,
                ..Default::default()
            };
            let status = GdiplusStartup(&mut token, &input, null_mut());
            if status == 0 {
                Ok(Self { token })
            } else {
                Err(format!("GDI+ 初始化失败：{status}"))
            }
        }
    }
}

impl Drop for GdiPlusSession {
    fn drop(&mut self) {
        unsafe { GdiplusShutdown(self.token) }
    }
}

struct WindowState {
    hwnd: Hwnd,
    config: AppConfig,
    frames: Vec<PathBuf>,
    frame_index: usize,
    _gdiplus: GdiPlusSession,
}

impl WindowState {
    fn new(config: AppConfig, frames: Vec<PathBuf>, gdiplus: GdiPlusSession) -> Self {
        Self {
            hwnd: 0,
            config,
            frames,
            frame_index: 0,
            _gdiplus: gdiplus,
        }
    }
}

unsafe extern "system" fn window_proc(
    hwnd: Hwnd,
    msg: Uint,
    wparam: Wparam,
    lparam: Lparam,
) -> Lresult {
    if msg == WM_NCCREATE {
        let create = lparam as *const CreateStructW;
        SetWindowLongPtrW(hwnd, GWLP_USERDATA, (*create).lp_create_params as isize);
        return DefWindowProcW(hwnd, msg, wparam, lparam);
    }

    let state_ptr = SetWindowLongPtrW(hwnd, GWLP_USERDATA, 0) as *mut WindowState;
    SetWindowLongPtrW(hwnd, GWLP_USERDATA, state_ptr as isize);

    if !state_ptr.is_null() {
        let state = &mut *state_ptr;
        match msg {
            WM_TIMER if wparam == TIMER_ID => {
                let _ = render_next_frame(state);
                return 0;
            }
            WM_LBUTTONDOWN => {
                ReleaseCapture();
                SendMessageW(hwnd, WM_NCLBUTTONDOWN, HTCAPTION, 0);
                return 0;
            }
            WM_KEYDOWN if wparam == VK_ESCAPE => {
                DestroyWindow(hwnd);
                return 0;
            }
            WM_CLOSE => {
                DestroyWindow(hwnd);
                return 0;
            }
            WM_DESTROY => {
                KillTimer(hwnd, TIMER_ID);
                let _owned = Box::from_raw(state_ptr);
                SetWindowLongPtrW(hwnd, GWLP_USERDATA, 0);
                PostQuitMessage(0);
                return 0;
            }
            _ => {}
        }
    }

    DefWindowProcW(hwnd, msg, wparam, lparam)
}

fn discover_frames(config: &AppConfig) -> Result<Vec<PathBuf>> {
    let mut frames: Vec<PathBuf> = std::fs::read_dir(&config.frames_dir)
        .map_err(|error| {
            format!(
                "读取素材目录失败：{} ({error})",
                config.frames_dir.display()
            )
        })?
        .filter_map(|entry| entry.ok().map(|entry| entry.path()))
        .filter(|path| {
            path.extension()
                .and_then(|ext| ext.to_str())
                .map(|ext| ext.eq_ignore_ascii_case("png"))
                .unwrap_or(false)
        })
        .collect();
    frames.sort();

    if frames.is_empty() {
        message_box_error(&format!(
            "没有找到 PNG 帧。请把透明小猫帧放到 {}",
            config.frames_dir.display()
        ));
        return Err("没有找到 PNG 帧".to_string());
    }

    Ok(frames)
}

fn render_next_frame(state: &mut WindowState) -> Result<()> {
    let frame = &state.frames[state.frame_index];
    state.frame_index = (state.frame_index + 1) % state.frames.len();
    render_png_to_layered_window(state.hwnd, frame, state.config.width)
}

fn render_png_to_layered_window(hwnd: Hwnd, path: &Path, target_width: i32) -> Result<()> {
    unsafe {
        let mut bitmap = null_mut();
        let wide_path = wide(path.as_os_str());
        let status = GdipCreateBitmapFromFile(wide_path.as_ptr(), &mut bitmap);
        if status != 0 || bitmap.is_null() {
            return Err(format!("加载图片失败：{}", path.display()));
        }

        let mut width = 0;
        let mut height = 0;
        GdipGetImageWidth(bitmap, &mut width);
        GdipGetImageHeight(bitmap, &mut height);

        let draw_image = if target_width > 0 && width > 0 && target_width as u32 != width {
            let target_height = ((target_width as f32) * (height as f32 / width as f32))
                .round()
                .max(1.0) as u32;
            let mut thumbnail = null_mut();
            let status = GdipGetImageThumbnail(
                bitmap,
                target_width as u32,
                target_height,
                &mut thumbnail,
                null_mut(),
                null_mut(),
            );
            if status == 0 && !thumbnail.is_null() {
                width = target_width as u32;
                height = target_height;
                thumbnail
            } else {
                bitmap
            }
        } else {
            bitmap
        };

        let mut hbitmap = 0;
        let status = GdipCreateHBITMAPFromBitmap(draw_image, &mut hbitmap, 0);
        if draw_image != bitmap {
            GdipDisposeImage(draw_image);
        }
        GdipDisposeImage(bitmap);
        if status != 0 || hbitmap == 0 {
            return Err(format!("创建位图失败：{}", path.display()));
        }

        let screen_dc = GetDC(0);
        let mem_dc = CreateCompatibleDC(screen_dc);
        let old = SelectObject(mem_dc, hbitmap);
        let dst = Point { x: 0, y: 0 };
        let size = Size {
            cx: width as i32,
            cy: height as i32,
        };
        let src = Point { x: 0, y: 0 };
        let blend = BlendFunction {
            blend_op: AC_SRC_OVER,
            blend_flags: 0,
            source_constant_alpha: 255,
            alpha_format: AC_SRC_ALPHA,
        };
        let ok = UpdateLayeredWindow(
            hwnd, screen_dc, &dst, &size, mem_dc, &src, 0, &blend, ULW_ALPHA,
        );
        SelectObject(mem_dc, old);
        DeleteObject(hbitmap);
        DeleteDC(mem_dc);
        ReleaseDC(0, screen_dc);

        if ok == 0 {
            return Err("刷新透明窗口失败".to_string());
        }
    }

    Ok(())
}

fn wide<S: AsRef<OsStr>>(value: S) -> Vec<u16> {
    value.as_ref().encode_wide().chain(once(0)).collect()
}

fn message_box_error(text: &str) {
    unsafe {
        MessageBoxW(
            0,
            wide(text).as_ptr(),
            wide("XGG Desktop Cat").as_ptr(),
            MB_ICONERROR,
        );
    }
}
