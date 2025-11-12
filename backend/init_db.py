#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""初始化数据库脚本"""

from app.models.database import init_db
from app.services.indicator_service import IndicatorService
from app.models.database import SessionLocal

if __name__ == "__main__":
    print("初始化数据库...")
    init_db()
    print("创建内置指标...")
    db = SessionLocal()
    try:
        IndicatorService.init_builtin_indicators(db)
        print("数据库初始化完成！")
    except Exception as e:
        print(f"错误: {e}")
        raise
    finally:
        db.close()

