#!/bin/bash

echo "========================================"
echo "智能体评估工具 - 环境设置脚本"
echo "========================================"
echo ""

echo "[1/3] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.9或更高版本"
    exit 1
fi
python3 --version

echo "[2/3] 创建虚拟环境..."
if [ ! -d "../backend/venv" ]; then
    python3 -m venv ../backend/venv
    echo "虚拟环境创建完成"
else
    echo "虚拟环境已存在，跳过创建"
fi

echo "[3/3] 安装Python依赖..."
source ../backend/venv/bin/activate
pip install --upgrade pip
pip install -r ../backend/requirements.txt

echo ""
echo "========================================"
echo "环境设置完成！"
echo "========================================"
echo ""
echo "下一步："
echo "  1. 运行 ./scripts/run_backend.sh 启动后端服务"
echo "  2. 在浏览器中打开 frontend/index.html 或使用简单的HTTP服务器"
echo ""

