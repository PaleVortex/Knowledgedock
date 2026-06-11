@echo off
REM Knowledgedock Application Launcher
REM This script launches the Knowledgedock application

echo.
echo ========================================
echo  Knowledgedock Application Launcher
echo ========================================
echo.

REM Get the directory of this script
set SCRIPT_DIR=%~dp0

REM Change to dist directory
cd /d "%SCRIPT_DIR%dist"

REM Check if executable exists
if not exist Knowledgedock.exe (
    echo.
    echo ERROR: Knowledgedock.exe not found!
    echo Please ensure the application has been built.
    echo Run: python build_app.py
    echo.
    pause
    exit /b 1
)

REM Launch the application
echo Launching Knowledgedock...
start Knowledgedock.exe

echo Application started successfully!
echo.
