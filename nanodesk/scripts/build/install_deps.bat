@echo off
chcp 65001 >nul
echo ========================================
echo    Nanodesk 依赖安装
echo ========================================
echo.

echo 正在安装依赖...
pip install typer pydantic pydantic-settings loguru websockets httpx

echo.
echo 安装完成！
echo 现在可以运行 Nanodesk.exe 了
echo.
pause
