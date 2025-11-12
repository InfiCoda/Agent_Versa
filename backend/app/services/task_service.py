"""任务服务"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.task import EvaluationTask, TaskStatus
from ..models.result import EvaluationResult


class TaskService:
    """评估任务服务"""
    
    @staticmethod
    def create_task(
        db: Session,
        name: str,
        description: str = None,
        agent_config: Dict[str, Any] = None,
        dataset_config: Dict[str, Any] = None,
        selected_indicators: List[int] = None,
        indicator_weights: Dict[int, float] = None,
        user_id: int = None
    ) -> EvaluationTask:
        """创建评估任务"""
        # 处理数据集配置：如果路径为空，使用默认路径
        if dataset_config:
            file_path = dataset_config.get("file_path", "").strip()
            if not file_path:
                dataset_config = dataset_config.copy()
                dataset_config["file_path"] = "app/data/samples.json"  # 默认数据集路径
        
        task = EvaluationTask(
            name=name,
            description=description,
            agent_api_endpoint=agent_config.get("api_endpoint") if agent_config else None,
            agent_api_key=agent_config.get("api_key") if agent_config else None,
            agent_config=agent_config,
            dataset_type=dataset_config.get("type") if dataset_config else None,
            dataset_config=dataset_config,
            selected_indicators=selected_indicators or [],
            indicator_weights=indicator_weights or {},
            user_id=user_id,
            status=TaskStatus.PENDING
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[EvaluationTask]:
        """获取任务"""
        return db.query(EvaluationTask).filter(EvaluationTask.id == task_id).first()
    
    @staticmethod
    def get_tasks(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: TaskStatus = None,
        user_id: int = None
    ) -> List[EvaluationTask]:
        """获取任务列表"""
        query = db.query(EvaluationTask)
        if status:
            query = query.filter(EvaluationTask.status == status)
        if user_id:
            query = query.filter(EvaluationTask.user_id == user_id)
        return query.order_by(EvaluationTask.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_task_status(
        db: Session,
        task_id: int,
        status: TaskStatus,
        progress: str = None
    ) -> Optional[EvaluationTask]:
        """更新任务状态"""
        task = TaskService.get_task(db, task_id)
        if not task:
            return None
        
        task.status = status
        if progress:
            task.progress = progress
        
        if status == TaskStatus.RUNNING and not task.started_at:
            task.started_at = datetime.utcnow()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            task.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def update_task_progress(
        db: Session,
        task_id: int,
        processed_samples: int,
        total_samples: int
    ) -> Optional[EvaluationTask]:
        """更新任务进度"""
        task = TaskService.get_task(db, task_id)
        if not task:
            return None
        
        task.processed_samples = processed_samples
        task.total_samples = total_samples
        if total_samples > 0:
            progress_percent = int((processed_samples / total_samples) * 100)
            task.progress = f"{progress_percent}%"
        
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def update_task(
        db: Session,
        task_id: int,
        name: str = None,
        description: str = None,
        agent_config: Dict[str, Any] = None,
        dataset_config: Dict[str, Any] = None,
        selected_indicators: List[int] = None,
        indicator_weights: Dict[int, float] = None
    ) -> Optional[EvaluationTask]:
        """更新任务配置"""
        task = TaskService.get_task(db, task_id)
        if not task:
            return None
        
        # 只允许更新待执行或失败的任务
        if task.status not in [TaskStatus.PENDING, TaskStatus.FAILED]:
            raise ValueError(f"只能编辑待执行或失败的任务，当前状态: {task.status.value}")
        
        # 更新字段
        if name is not None:
            task.name = name
        if description is not None:
            task.description = description
        if agent_config is not None:
            task.agent_api_endpoint = agent_config.get("api_endpoint")
            # API密钥：如果提供了新值，则更新；如果为空字符串，保持原值
            new_api_key = agent_config.get("api_key")
            if new_api_key is not None and new_api_key != "":
                task.agent_api_key = new_api_key
            # 更新agent_config，但保留原有的api_key（如果新值未提供）
            updated_config = agent_config.copy()
            if new_api_key is None or new_api_key == "":
                updated_config["api_key"] = task.agent_api_key  # 保持原值
            task.agent_config = updated_config
        if dataset_config is not None:
            task.dataset_type = dataset_config.get("type")
            # 处理数据集路径：如果为空，使用默认路径
            file_path = dataset_config.get("file_path", "").strip()
            if not file_path:
                dataset_config = dataset_config.copy()
                dataset_config["file_path"] = "app/data/samples.json"  # 默认数据集路径
            task.dataset_config = dataset_config
        if selected_indicators is not None:
            task.selected_indicators = selected_indicators
        if indicator_weights is not None:
            task.indicator_weights = indicator_weights
        
        # 如果任务之前失败，重置状态
        if task.status == TaskStatus.FAILED:
            task.status = TaskStatus.PENDING
            task.progress = "0%"
            task.processed_samples = 0
            task.total_samples = 0
            task.started_at = None
            task.completed_at = None
            # 清除之前的错误描述（如果是以"执行失败:"开头的）
            if task.description and task.description.startswith("执行失败:"):
                task.description = description if description else task.description
        
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        """删除任务"""
        task = TaskService.get_task(db, task_id)
        if not task:
            return False
        
        db.delete(task)
        db.commit()
        return True

