@echo off
setlocal

REM Run the Python stdlib-only desktop pet. No Rust is required.
REM Usage from project root:
REM   scripts\run-python-cat.cmd

py -3 desktop_cat.py
if errorlevel 1 (
  echo.
  echo Failed to run with the Python launcher. Trying python.exe...
  python desktop_cat.py
)
