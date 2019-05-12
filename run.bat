@echo off
python build_json.py
if errorlevel 1 (
   exit /b %errorlevel%
)
python write_to_plex.py