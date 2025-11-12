"""评估指标API"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..models.database import get_db
from ..models.indicator import IndicatorCategory
from ..services.indicator_service import IndicatorService

router = APIRouter(prefix="/api/indicators", tags=["indicators"])


class IndicatorCreate(BaseModel):
    name: str
    display_name: str
    description: str
    calculation_function: str
    config_schema: Optional[dict] = None
    default_config: Optional[dict] = None


@router.get("", response_model=List[dict])
def get_indicators(
    category: Optional[str] = None,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """获取指标列表"""
    ind_category = None
    if category:
        try:
            ind_category = IndicatorCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的类别: {category}")
    
    indicators = IndicatorService.get_indicators(db, category=ind_category, is_active=is_active)
    return [
        {
            "id": ind.id,
            "name": ind.name,
            "display_name": ind.display_name,
            "description": ind.description,
            "category": ind.category.value,
            "calculation_function": ind.calculation_function,
            "is_builtin": ind.is_builtin,
            "created_at": ind.created_at.isoformat()
        }
        for ind in indicators
    ]


@router.get("/{indicator_id}", response_model=dict)
def get_indicator(indicator_id: int, db: Session = Depends(get_db)):
    """获取指标详情"""
    indicator = IndicatorService.get_indicator(db, indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")
    
    return {
        "id": indicator.id,
        "name": indicator.name,
        "display_name": indicator.display_name,
        "description": indicator.description,
        "category": indicator.category.value,
        "calculation_function": indicator.calculation_function,
        "config_schema": indicator.config_schema,
        "default_config": indicator.default_config,
        "is_builtin": indicator.is_builtin,
        "is_active": indicator.is_active,
        "created_at": indicator.created_at.isoformat()
    }


@router.post("", response_model=dict)
def create_indicator(indicator: IndicatorCreate, db: Session = Depends(get_db)):
    """创建自定义指标"""
    try:
        new_indicator = IndicatorService.create_custom_indicator(
            db=db,
            name=indicator.name,
            display_name=indicator.display_name,
            description=indicator.description,
            calculation_function=indicator.calculation_function,
            config_schema=indicator.config_schema,
            default_config=indicator.default_config
        )
        return {
            "id": new_indicator.id,
            "name": new_indicator.name,
            "display_name": new_indicator.display_name,
            "category": new_indicator.category.value
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

