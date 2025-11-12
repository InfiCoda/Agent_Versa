"""评估指标模型"""

from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from .database import Base


class IndicatorCategory(str, enum.Enum):
    """指标类别枚举"""
    BASIC_PERFORMANCE = "basic_performance"    # 基础性能指标
    GENERATION_TASK = "generation_task"       # 生成任务指标
    GENERALIZATION = "generalization"         # 通用化特征指标
    CUSTOM = "custom"                         # 自定义指标


class Indicator(Base):
    """评估指标模型"""
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(SQLEnum(IndicatorCategory), nullable=False, index=True)
    
    # 指标配置
    config_schema = Column(JSON)  # 指标配置的JSON Schema
    default_config = Column(JSON) # 默认配置
    
    # 计算函数信息（存储函数名或脚本）
    calculation_function = Column(String(255))  # 计算函数名称或脚本路径
    
    # 元数据
    is_builtin = Column(Boolean, default=True)  # 是否为内置指标
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

