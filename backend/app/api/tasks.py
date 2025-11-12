"""任务管理API"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..models.database import get_db
from ..models.task import TaskStatus
from ..services.task_service import TaskService
from ..services.evaluation_service import EvaluationService

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    name: str
    description: Optional[str] = None
    agent_config: Optional[dict] = None
    dataset_config: Optional[dict] = None
    selected_indicators: Optional[List[int]] = None
    indicator_weights: Optional[dict] = None


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    agent_config: Optional[dict] = None
    dataset_config: Optional[dict] = None
    selected_indicators: Optional[List[int]] = None
    indicator_weights: Optional[dict] = None


@router.post("", response_model=dict)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """创建评估任务"""
    try:
        new_task = TaskService.create_task(
            db=db,
            name=task.name,
            description=task.description,
            agent_config=task.agent_config,
            dataset_config=task.dataset_config,
            selected_indicators=task.selected_indicators,
            indicator_weights=task.indicator_weights
        )
        return {
            "id": new_task.id,
            "name": new_task.name,
            "status": new_task.status.value,
            "created_at": new_task.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[dict])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    task_status = None
    if status:
        try:
            task_status = TaskStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的状态: {status}")
    
    tasks = TaskService.get_tasks(db, skip=skip, limit=limit, status=task_status)
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "status": t.status.value,
            "progress": t.progress,
            "total_samples": t.total_samples,
            "processed_samples": t.processed_samples,
            "created_at": t.created_at.isoformat(),
            "updated_at": t.updated_at.isoformat() if t.updated_at else None
        }
        for t in tasks
    ]


@router.get("/{task_id}", response_model=dict)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """获取任务详情"""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return {
        "id": task.id,
        "name": task.name,
        "description": task.description,
        "status": task.status.value,
        "progress": task.progress,
        "agent_config": task.agent_config or {"api_endpoint": "", "api_key": ""},
        "dataset_config": task.dataset_config or {"type": "json", "file_path": ""},
        "selected_indicators": task.selected_indicators or [],
        "indicator_weights": task.indicator_weights or {},
        "total_samples": task.total_samples,
        "processed_samples": task.processed_samples,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "result_id": task.result.id if task.result else None
    }


@router.put("/{task_id}", response_model=dict)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """更新任务配置"""
    try:
        # 处理API密钥：如果为null，则不更新agent_config中的api_key字段
        agent_config = task_update.agent_config
        if agent_config and agent_config.get("api_key") is None:
            # 获取原任务的api_key，保持原值
            task = TaskService.get_task(db, task_id)
            if task and task.agent_config:
                agent_config = agent_config.copy()
                agent_config["api_key"] = task.agent_config.get("api_key")
        
        updated_task = TaskService.update_task(
            db=db,
            task_id=task_id,
            name=task_update.name,
            description=task_update.description,
            agent_config=agent_config,
            dataset_config=task_update.dataset_config,
            selected_indicators=task_update.selected_indicators,
            indicator_weights=task_update.indicator_weights
        )
        if not updated_task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return {
            "id": updated_task.id,
            "name": updated_task.name,
            "status": updated_task.status.value,
            "message": "任务配置已更新"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{task_id}/start", response_model=dict)
def start_task(task_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """启动任务执行"""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 允许重新启动失败的任务
    if task.status not in [TaskStatus.PENDING, TaskStatus.FAILED]:
        raise HTTPException(status_code=400, detail=f"任务状态不允许启动: {task.status.value}")
    
    # 在后台执行任务（使用新的数据库会话）
    from ..models.database import SessionLocal
    def run_evaluation():
        db_session = SessionLocal()
        try:
            import asyncio
            asyncio.run(EvaluationService.execute_task(db_session, task_id))
        finally:
            db_session.close()
    
    background_tasks.add_task(run_evaluation)
    
    return {"message": "任务已启动", "task_id": task_id}


@router.delete("/{task_id}", response_model=dict)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """删除任务"""
    success = TaskService.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"message": "任务已删除", "task_id": task_id}

