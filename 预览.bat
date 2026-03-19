@echo off
chcp 65001 >nul
cd /d "%~dp0"
python 视频分类脚本.py "."
pause
