"""评估结果模型"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class EvaluationResult(Base):
    """评估结果模型"""
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("evaluation_tasks.id"), unique=True)
    
    # 总体评分
    overall_score = Column(Float)  # 加权综合得分
    
    # 结果详情
    summary = Column(JSON)         # 结果摘要
    detailed_results = Column(JSON) # 详细结果数据
    
    # 分析报告
    analysis_report = Column(Text)  # 文本分析报告
    
    # 可视化数据
    radar_chart_data = Column(JSON) # 雷达图数据
    correlation_matrix = Column(JSON) # 指标关联矩阵
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    task = relationship("EvaluationTask", back_populates="result")
    result_items = relationship("ResultItem", back_populates="result", cascade="all, delete-orphan")


class ResultItem(Base):
    """评估结果项（每个指标的具体结果）"""
    __tablename__ = "result_items"

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("evaluation_results.id"), nullable=False)
    indicator_id = Column(Integer, ForeignKey("indicators.id"), nullable=False)
    
    # 指标得分
    score = Column(Float, nullable=False)
    weighted_score = Column(Float)  # 加权后的得分
    
    # 详细数据
    raw_data = Column(JSON)         # 原始计算结果
    extra_metadata = Column(JSON)   # 额外的元数据（避免与SQLAlchemy的metadata冲突）
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    result = relationship("EvaluationResult", back_populates="result_items")
    indicator = relationship("Indicator")

