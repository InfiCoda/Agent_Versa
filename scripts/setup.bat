@echo off
chcp 65001 >nul 2>&1
REM 切换到脚本所在目录的父目录（项目根目录）
cd /d "%~dp0.."
echo ========================================
echo 智能体评估工具 - 环境设置脚本
echo ========================================
echo.

echo [1/3] 检查Python环境...
set PYTHON_CMD=
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    python --version
) else (
    where python3 >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
        python3 --version
    ) else (
        where py >nul 2>&1
        if %errorlevel% equ 0 (
            set PYTHON_CMD=py
            py --version
        ) else (
            echo 错误: 未找到Python，请先安装Python 3.9或更高版本
            echo.
            echo 提示: 请确保Python已添加到系统PATH环境变量中
            echo       或者安装Python时选择"Add Python to PATH"选项
            pause
            exit /b 1
        )
    )
)

echo [2/3] 创建虚拟环境...
if not exist "backend\venv" (
    %PYTHON_CMD% -m venv backend\venv
    if %errorlevel% neq 0 (
        echo 错误: 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo 虚拟环境创建完成
) else (
    echo 虚拟环境已存在，跳过创建
)

echo [3/3] 安装Python依赖...
if not exist "backend\venv\Scripts\activate.bat" (
    echo 错误: 虚拟环境激活脚本不存在
    pause
    exit /b 1
)
call backend\venv\Scripts\activate.bat
%PYTHON_CMD% -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo 警告: 升级pip失败，继续安装依赖...
)
pip install -r backend\requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 安装依赖失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 环境设置完成！
echo ========================================
echo.
echo 下一步：
echo   1. 运行 scripts\run_backend.bat 启动后端服务
echo   2. 在浏览器中打开 frontend\index.html 或运行 scripts\run_frontend.bat
echo.
pause
