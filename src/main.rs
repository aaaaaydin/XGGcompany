#![cfg_attr(windows, windows_subsystem = "windows")]

#[cfg(windows)]
mod win_pet;

use std::{fs, path::PathBuf};

#[derive(Debug, Clone)]
struct AppConfig {
    width: i32,
    fps: u32,
    topmost: bool,
    click_through: bool,
    start_x: i32,
    start_y: i32,
    frames_dir: PathBuf,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            width: 260,
            fps: 24,
            topmost: true,
            click_through: false,
            start_x: 1200,
            start_y: 620,
            frames_dir: PathBuf::from("assets/frames"),
        }
    }
}

fn load_config() -> AppConfig {
    let mut config = AppConfig::default();
    let Ok(text) = fs::read_to_string("config.toml") else {
        return config;
    };

    for raw_line in text.lines() {
        let line = raw_line.split('#').next().unwrap_or_default().trim();
        if line.is_empty() {
            continue;
        }
        let Some((key, value)) = line.split_once('=') else {
            continue;
        };
        let key = key.trim();
        let value = value.trim().trim_matches('"');
        match key {
            "width" => config.width = value.parse().unwrap_or(config.width),
            "fps" => config.fps = value.parse().unwrap_or(config.fps),
            "topmost" => config.topmost = parse_bool(value, config.topmost),
            "click_through" => config.click_through = parse_bool(value, config.click_through),
            "start_x" => config.start_x = value.parse().unwrap_or(config.start_x),
            "start_y" => config.start_y = value.parse().unwrap_or(config.start_y),
            "frames_dir" => config.frames_dir = PathBuf::from(value),
            _ => {}
        }
    }

    config
}

fn parse_bool(value: &str, fallback: bool) -> bool {
    match value.trim().to_ascii_lowercase().as_str() {
        "true" | "1" | "yes" | "on" => true,
        "false" | "0" | "no" | "off" => false,
        _ => fallback,
    }
}

#[cfg(windows)]
fn main() {
    if let Err(error) = win_pet::run(load_config()) {
        eprintln!("启动失败：{error}");
    }
}

#[cfg(not(windows))]
fn main() {
    let config = load_config();
    println!(
        "xgg-desktop-cat 是 Windows 桌面宠物程序；请在 Windows 11 上运行。当前配置：{config:#?}"
    );
}
