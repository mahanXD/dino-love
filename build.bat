@echo off
title Build DinoLove Game (Embedded)
color 0A

echo ========================================
echo    Building DinoLove Game with Assets
echo ========================================
echo.

echo [1/4] Cleaning old files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec
echo Done.
echo.

echo [2/4] Building new EXE with embedded assets...
python -m PyInstaller --onefile --noconsole --name "DinoLove" --hidden-import=pygame --collect-all pygame --add-data "pic;pic" --add-data "sound;sound" dino_game.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b
)
echo Done.
echo.

echo [3/4] Copying DinoLove.exe to main folder...
if exist dist\DinoLove.exe (
    copy /y dist\DinoLove.exe DinoLove.exe >nul
    echo   - Copied DinoLove.exe to main folder
) else (
    echo   - ERROR: DinoLove.exe not found!
    pause
    exit /b
)
echo Done.
echo.

echo [4/4] Cleaning temporary files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
del /q *.spec 2>nul
echo Done.
echo.

echo ========================================
echo    ✅ Build Complete!
echo    🎮 DinoLove.exe is ready to use.
echo    📦 All assets are embedded inside EXE.
echo ========================================
echo.
pause