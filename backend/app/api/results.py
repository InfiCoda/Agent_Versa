"""评估结果API"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models.database import get_db
from ..models.result import EvaluationResult
from ..models.task import EvaluationTask

router = APIRouter(prefix="/api/results", tags=["results"])


@router.get("/task/{task_id}", response_model=dict)
def get_task_result(task_id: int, db: Session = Depends(get_db)):
    """获取任务的评估结果"""
    task = db.query(EvaluationTask).filter(EvaluationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if not task.result:
        raise HTTPException(status_code=404, detail="任务尚未完成，暂无结果")
    
    result = task.result
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")
    
    # 获取结果项
    result_items = [
        {
            "indicator_id": item.indicator_id,
            "indicator_name": item.indicator.name if item.indicator else "",
            "score": item.score,
            "weighted_score": item.weighted_score,
            "raw_data": item.raw_data
        }
        for item in result.result_items
    ]
    
    return {
        "id": result.id,
        "task_id": result.task_id,
        "overall_score": result.overall_score,
        "summary": result.summary,
        "detailed_results": result.detailed_results,
        "analysis_report": result.analysis_report,
        "radar_chart_data": result.radar_chart_data,
        "correlation_matrix": result.correlation_matrix,
        "result_items": result_items,
        "created_at": result.created_at.isoformat()
    }


@router.get("/{result_id}", response_model=dict)
def get_result(result_id: int, db: Session = Depends(get_db)):
    """获取评估结果"""
    result = db.query(EvaluationResult).filter(EvaluationResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")
    
    result_items = [
        {
            "indicator_id": item.indicator_id,
            "indicator_name": item.indicator.name if item.indicator else "",
            "score": item.score,
            "weighted_score": item.weighted_score,
            "raw_data": item.raw_data
        }
        for item in result.result_items
    ]
    
    return {
        "id": result.id,
        "task_id": result.task_id,
        "overall_score": result.overall_score,
        "summary": result.summary,
        "detailed_results": result.detailed_results,
        "analysis_report": result.analysis_report,
        "radar_chart_data": result.radar_chart_data,
        "correlation_matrix": result.correlation_matrix,
        "result_items": result_items,
        "created_at": result.created_at.isoformat()
    }

