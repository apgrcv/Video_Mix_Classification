@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -3 "%~dp0video_classifier_gui.py"
if errorlevel 1 python "%~dp0video_classifier_gui.py"
pause
