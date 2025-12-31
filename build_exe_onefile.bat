@echo off
chcp 65001 >nul
echo ========================================
echo 工时统计程序打包工具（单文件模式）
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
echo 检查依赖包...
python -c "import pandas; import openpyxl; import matplotlib; import tkinter" 2>nul
if errorlevel 1 (
    echo 警告：某些依赖包可能未安装，正在安装...
    pip install pandas openpyxl matplotlib
)

echo.
echo 开始打包程序（单文件模式）...
echo 注意：单文件模式打包时间较长，请耐心等待...
echo.

REM 清理之前的构建文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist work_hours_analyzer.spec del /q work_hours_analyzer.spec 2>nul

echo 正在执行打包命令...
echo.

REM 使用单文件模式打包（使用spec文件）
python -m PyInstaller --clean work_hours_analyzer_onefile.spec

if errorlevel 1 (
    echo.
    echo ========================================
    echo 打包失败！
    echo ========================================
    echo.
    echo 请检查上面的错误信息，常见问题：
    echo 1. 确保已安装所有依赖: pip install -r requirements.txt
    echo 2. 检查是否有杀毒软件拦截
    echo 3. 尝试使用命令行模式查看详细错误
    echo.
    echo 可以尝试运行以下命令查看详细错误：
    echo pyinstaller --clean --onefile --windowed work_hours_analyzer.py
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo 打包成功！
    echo ========================================
    echo 可执行文件位置: dist\work_hours_analyzer.exe
    echo.
    echo 单文件模式：只需要分发 work_hours_analyzer.exe 一个文件即可
    echo 文件大小约为 50-100MB，首次运行可能需要几秒钟解压
    echo.
)

pause

