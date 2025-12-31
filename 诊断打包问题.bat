@echo off
chcp 65001 >nul
echo ========================================
echo 打包问题诊断工具
echo ========================================
echo.

echo 1. 检查Python版本...
python --version
echo.

echo 2. 检查PyInstaller是否安装...
python -c "import PyInstaller; print('PyInstaller版本:', PyInstaller.__version__)" 2>nul
if errorlevel 1 (
    echo [错误] PyInstaller未安装
    echo 正在安装...
    pip install pyinstaller
) else (
    echo [通过] PyInstaller已安装
)
echo.

echo 3. 检查依赖包...
python -c "import pandas; print('[通过] pandas版本:', pandas.__version__)" 2>nul || echo [错误] pandas未安装
python -c "import openpyxl; print('[通过] openpyxl已安装')" 2>nul || echo [错误] openpyxl未安装
python -c "import matplotlib; print('[通过] matplotlib版本:', matplotlib.__version__)" 2>nul || echo [错误] matplotlib未安装
python -c "import tkinter; print('[通过] tkinter已安装')" 2>nul || echo [错误] tkinter未安装
python -c "import numpy; print('[通过] numpy已安装')" 2>nul || echo [警告] numpy未安装（可选）
echo.

echo 4. 检查源文件是否存在...
if exist work_hours_analyzer.py (
    echo [通过] work_hours_analyzer.py 存在
) else (
    echo [错误] work_hours_analyzer.py 不存在
)
echo.

echo 5. 测试程序是否可以运行...
python work_hours_analyzer.py --help 2>nul
if errorlevel 1 (
    echo [警告] 程序可能无法正常运行，请先测试源程序
) else (
    echo [通过] 程序可以运行
)
echo.

echo ========================================
echo 诊断完成
echo ========================================
echo.
echo 如果发现问题，请：
echo 1. 安装缺失的依赖: pip install -r requirements.txt
echo 2. 更新PyInstaller: pip install --upgrade pyinstaller
echo 3. 尝试使用 build_exe_simple.bat 进行打包
echo.
pause

