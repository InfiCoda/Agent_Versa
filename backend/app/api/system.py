"""系统管理API"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import psutil
import os
from ..models.database import get_db
from ..services.indicator_service import IndicatorService

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/health", response_model=dict)
def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "message": "系统运行正常"
    }


@router.get("/stats", response_model=dict)
def get_system_stats():
    """获取系统统计信息"""
    # CPU和内存使用情况
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    return {
        "cpu": {
            "percent": cpu_percent,
            "count": psutil.cpu_count()
        },
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent
        },
        "disk": {
            "total": psutil.disk_usage('/').total if os.name != 'nt' else psutil.disk_usage('C:\\').total,
            "used": psutil.disk_usage('/').used if os.name != 'nt' else psutil.disk_usage('C:\\').used,
            "free": psutil.disk_usage('/').free if os.name != 'nt' else psutil.disk_usage('C:\\').free
        }
    }


@router.post("/init", response_model=dict)
def init_system(db: Session = Depends(get_db)):
    """初始化系统（创建内置指标等）"""
    try:
        IndicatorService.init_builtin_indicators(db)
        return {"message": "系统初始化成功"}
    except Exception as e:
        return {"message": f"系统初始化失败: {str(e)}"}

