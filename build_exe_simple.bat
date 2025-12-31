@echo off
chcp 65001 >nul
echo ========================================
echo 工时统计程序打包工具（简化版）
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
    echo 正在安装依赖包...
    pip install pandas openpyxl matplotlib
)

echo.
echo 开始打包程序（单文件模式，简化配置）...
echo 注意：打包时间较长，请耐心等待...
echo.

REM 清理之前的构建文件
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul

echo 正在执行打包命令...
echo.

REM 使用最简单的命令行方式打包
python -m PyInstaller --clean --onefile --windowed ^
    --name=work_hours_analyzer ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=matplotlib ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.filedialog ^
    --hidden-import=tkinter.messagebox ^
    --hidden-import=tkinter.simpledialog ^
    --hidden-import=numpy ^
    --hidden-import=matplotlib.backends.backend_tkagg ^
    --hidden-import=matplotlib.backends.backend_agg ^
    --hidden-import=pandas._libs.tslibs.timedeltas ^
    --hidden-import=pandas._libs.tslibs.nattype ^
    --collect-all pandas ^
    --collect-all matplotlib ^
    work_hours_analyzer.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo 打包失败！
    echo ========================================
    echo.
    echo 请查看上面的详细错误信息
    echo.
    echo 常见解决方案：
    echo 1. 确保已安装所有依赖: pip install -r requirements.txt
    echo 2. 尝试更新PyInstaller: pip install --upgrade pyinstaller
    echo 3. 检查Python版本（建议3.8-3.11）
    echo 4. 临时禁用杀毒软件
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

