#!/bin/bash

echo "========================================"
echo "启动后端服务"
echo "========================================"
echo ""

cd ../backend

if [ ! -d "venv" ]; then
    echo "错误: 虚拟环境不存在，请先运行 ./scripts/setup.sh"
    exit 1
fi

echo "激活虚拟环境..."
source venv/bin/activate

echo "启动FastAPI服务..."
echo "服务地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

