@echo off
chcp 65001 >nul 2>&1
REM 切换到脚本所在目录的父目录（项目根目录）
cd /d "%~dp0.."
echo ========================================
echo 初始化数据库
echo ========================================
echo.

cd backend

if not exist "venv" (
    echo 错误: 虚拟环境不存在，请先运行 scripts\setup.bat
    pause
    exit /b 1
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 初始化数据库并创建内置指标...
python init_db.py

echo.
echo ========================================
echo 数据库初始化完成！
echo ========================================
pause

