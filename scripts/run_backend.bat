@echo off
chcp 65001 >nul 2>&1
REM 切换到脚本所在目录的父目录（项目根目录）
cd /d "%~dp0.."
echo ========================================
echo 启动后端服务
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

echo 启动FastAPI服务...
echo 服务地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause

