@echo off
REM Builds a single-file, windowless .exe using PyInstaller.
REM Run this from inside the project folder after installing requirements.txt.

pyinstaller --noconfirm --onefile --windowed ^
  --name "ImageToTextScanner" ^
  --icon "icon.ico" ^
  --add-data "icon.ico;." ^
  --add-data "icon_paused.ico;." ^
  main.py

echo.
echo Done. Find ImageToTextScanner.exe in the "dist" folder.
pause
