@echo off
echo ============================================
echo    Alertix App - Setup Script
echo ============================================
echo.

:: Check if Flutter is installed
where flutter >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Flutter is not installed or not in PATH!
    echo.
    echo Please install Flutter first:
    echo 1. Download from: https://flutter.dev/docs/get-started/install/windows
    echo 2. Extract to C:\flutter
    echo 3. Add C:\flutter\bin to your PATH
    echo 4. Restart your terminal and run this script again
    echo.
    pause
    exit /b 1
)

echo [OK] Flutter found!
flutter --version
echo.

:: Check Flutter doctor
echo [INFO] Running Flutter Doctor...
flutter doctor
echo.

:: Get dependencies
echo [INFO] Installing dependencies...
flutter pub get
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)
echo [OK] Dependencies installed!
echo.

:: Check for devices
echo [INFO] Checking for available devices...
flutter devices
echo.

echo ============================================
echo    Setup Complete!
echo ============================================
echo.
echo To run the app:
echo   flutter run
echo.
echo To run on a specific device:
echo   flutter run -d [device_id]
echo.
echo To run in Chrome (web):
echo   flutter run -d chrome
echo.
pause
