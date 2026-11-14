@echo off
cd /d "%~dp0"
set PYTHONPATH=src
python src\preview_ui.py
