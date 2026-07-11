@echo off
REM ============================================================
REM  Build both versions of Operations Toolkit (onedir mode).
REM
REM  Both builds output to dist/ so PyInstaller can share
REM  identical binaries (pandas, numpy, openpyxl, etc.) between
REM  the two _internal folders.
REM
REM  Prerequisites: pip install pyinstaller
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   Building Operations Toolkit — both versions
echo ============================================================
echo.

REM --- Check pyinstaller is available ---
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pyinstaller not found.
    echo Install it with: pip install pyinstaller
    exit /b 1
)

REM --- Clean previous builds ---
if exist build_webview rmdir /s /q build_webview
if exist build_tkinter rmdir /s /q build_tkinter

echo.
echo [1/2] Building webview version...
echo.
pyinstaller build_webview.spec --clean --distpath dist --workpath build_webview
if errorlevel 1 (
    echo.
    echo ERROR: webview build failed.
    exit /b 1
)

echo.
echo [2/2] Building tkinter version...
echo.
pyinstaller build_tkinter.spec --clean --distpath dist --workpath build_tkinter
if errorlevel 1 (
    echo.
    echo ERROR: tkinter build failed.
    exit /b 1
)

echo.
echo ============================================================
echo   Done! EXEs are in:
echo     dist/OperationsToolkit_Webview/OperationsToolkit_Webview.exe
echo     dist/OperationsToolkit/OperationsToolkit.exe
echo ============================================================
echo.

REM --- Code-sign the webview exe if cert env vars are set ---
if defined SIGN_CERT_PFX (
    if exist "%SIGN_CERT_PFX%" (
        echo.
        echo Signing OperationsToolkit_Webview.exe...
        echo.
        signtool sign /fd SHA256 /td SHA256 /tr http://timestamp.digicert.com /f "%SIGN_CERT_PFX%" /p "%SIGN_CERT_PASSWORD%" "dist\OperationsToolkit_Webview.exe"
        if errorlevel 1 (
            echo WARNING: signing failed — continuing unsigned.
        )
    )
)

REM --- Build the installer (Inno Setup) if available ---
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist %ISCC% (
    echo.
    echo Building installer (OperationsToolkit_Setup.exe)...
    echo.
    if defined SIGN_CERT_PFX (
        if exist "%SIGN_CERT_PFX%" (
            %ISCC% /Sinnosetup_sign="signtool.exe sign /fd sha256 /tr http://timestamp.digicert.com /td sha256 /f \"%SIGN_CERT_PFX%\" /p \"%SIGN_CERT_PASSWORD%\" $f" installer.iss
        ) else (
            %ISCC% installer.iss
        )
    ) else (
        %ISCC% installer.iss
    )
    if errorlevel 1 (
        echo WARNING: installer build failed — skipping. The app EXE still works.
    ) else (
        echo Installer written to: Output/OperationsToolkit_Setup.exe
    )
) else (
    echo.
    echo NOTE: Inno Setup not found at %ISCC%.
    echo       Install it from https://jrsoftware.org/isdl.php to build the
    echo       OperationsToolkit_Setup.exe installer used by the in-app updater.
    echo.
)

endlocal
