@echo off
rem This warpper is required on Windows so we don't get OEM encoding instead of UTF-8.
rem The chcp 65001 switches the code page before redirecting the output
chcp 65001 >nul
run-on-windows.cmd > run.console.log 2>&1
