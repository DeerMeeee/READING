@echo off
chcp 65001 >nul
echo.
echo ================================
echo    txt转JPG一键转换工具
echo ================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查脚本文件是否存在
if not exist "txt_to_jpg.py" (
    echo 错误: 找不到 txt_to_jpg.py 文件
    pause
    exit /b 1
)

echo 正在运行txt转JPG转换脚本...
echo.

REM 运行Python脚本
python txt_to_jpg.py

echo.
echo 转换完成！按任意键退出...
pause >nul