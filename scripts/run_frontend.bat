@echo off
chcp 65001 >nul 2>&1
REM 切换到脚本所在目录的父目录（项目根目录）
cd /d "%~dp0.."
echo ========================================
echo 启动前端服务
echo ========================================
echo.

cd frontend

echo 启动HTTP服务器...
echo 前端地址: http://localhost:8080
echo.
echo 按 Ctrl+C 停止服务
echo.

set PYTHON_CMD=
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where python3 >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
    ) else (
        where py >nul 2>&1
        if %errorlevel% equ 0 (
            set PYTHON_CMD=py
        ) else (
            echo 错误: 未找到Python
            pause
            exit /b 1
        )
    )
)

%PYTHON_CMD% -m http.server 8080

