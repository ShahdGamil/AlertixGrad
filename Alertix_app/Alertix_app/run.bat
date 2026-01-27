@echo off
echo Starting Alertix App...
echo.

:: Check if Flutter is available
where flutter >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Flutter not found! Please run setup.bat first.
    pause
    exit /b 1
)

:: Run the app
echo Running Flutter app...
flutter run

pause
