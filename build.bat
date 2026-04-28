@echo off
chcp 65001 >nul 2>&1
echo === Building hanoi.exe ===

where uv >nul 2>&1
if %ERRORLEVEL%==0 (
    echo Using uv...
    uv run --with pyinstaller pyinstaller hanoi.spec --noconfirm --collect-all tkinter --collect-all tk
) else (
    echo uv not found, using pip...
    pip install pyinstaller
    pyinstaller hanoi.spec --noconfirm --collect-all tkinter --collect-all tk
)

if exist "dist\hanoi.exe" (
    echo.
    echo === Build successful! ===
    echo Output: dist\hanoi.exe
) else (
    echo.
    echo === Build FAILED ===
)

pause
