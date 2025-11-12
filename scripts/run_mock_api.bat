@echo off
chcp 65001 >nul 2>&1
REM 切换到脚本所在目录的父目录（项目根目录）
cd /d "%~dp0.."
echo ========================================
echo 启动模拟API服务器
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

echo.
echo ========================================
echo 模拟API服务启动中...
echo ========================================
echo.
echo API端点: http://localhost:9000/api/chat
echo.
echo 在评估任务中，使用以下配置：
echo   智能体API端点: http://localhost:9000/api/chat
echo   API密钥: 留空
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python mock_api.py

pause

