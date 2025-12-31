@echo off
chcp 65001 >nul
echo ========================================
echo 工时统计程序打包工具
echo ========================================
echo.

REM 检查是否安装了PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo 安装PyInstaller失败，请检查网络连接或手动安装: pip install pyinstaller
        pause
        exit /b 1
    )
    echo 验证PyInstaller安装...
    python -c "import PyInstaller; print('PyInstaller安装成功')" 2>nul
    if errorlevel 1 (
        echo 警告：PyInstaller可能未正确安装，请手动运行: pip install pyinstaller
    )
)

echo.
echo 开始打包程序...
echo.

REM 使用spec文件打包
python -m PyInstaller work_hours_analyzer.spec

if errorlevel 1 (
    echo.
    echo 打包失败！
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo 打包成功！
    echo ========================================
    echo 可执行文件位置: dist\work_hours_analyzer.exe
    echo.
    echo 您可以将 dist 文件夹中的 work_hours_analyzer.exe 分发给其他用户
    echo 注意：需要将整个 dist 文件夹一起分发，或者只分发 .exe 文件（如果使用 --onefile 模式）
    echo.
)

pause

