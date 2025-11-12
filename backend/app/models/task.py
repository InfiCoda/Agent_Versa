"""评估任务模型"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from .database import Base


class TaskStatus(str, enum.Enum):
    """任务状态枚举"""
    PENDING = "pending"           # 等待中
    RUNNING = "running"           # 执行中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败
    CANCELLED = "cancelled"       # 已取消


class EvaluationTask(Base):
    """评估任务模型"""
    __tablename__ = "evaluation_tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, index=True)
    
    # 智能体配置
    agent_api_endpoint = Column(String(500))
    agent_api_key = Column(String(255))
    agent_config = Column(JSON)  # 存储额外的智能体配置
    
    # 数据集配置
    dataset_type = Column(String(50))  # json, csv, api
    dataset_config = Column(JSON)     # 数据集路径、API地址等
    
    # 指标配置
    selected_indicators = Column(JSON)  # 选中的指标ID列表
    indicator_weights = Column(JSON)    # 指标权重配置
    
    # 任务进度
    total_samples = Column(Integer, default=0)
    processed_samples = Column(Integer, default=0)
    progress = Column(String(50), default="0%")
    
    # 用户关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    result = relationship("EvaluationResult", back_populates="task", uselist=False)
    user = relationship("User")

