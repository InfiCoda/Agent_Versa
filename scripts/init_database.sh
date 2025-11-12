#!/bin/bash

echo "========================================"
echo "初始化数据库"
echo "========================================"
echo ""

cd ../backend

if [ ! -d "venv" ]; then
    echo "错误: 虚拟环境不存在，请先运行 ./scripts/setup.sh"
    exit 1
fi

echo "激活虚拟环境..."
source venv/bin/activate

echo "初始化数据库并创建内置指标..."
python -c "from app.models.database import init_db; from app.services.indicator_service import IndicatorService; from app.models.database import SessionLocal; init_db(); db = SessionLocal(); IndicatorService.init_builtin_indicators(db); print('数据库初始化完成！')"

echo ""
echo "========================================"
echo "数据库初始化完成！"
echo "========================================"

