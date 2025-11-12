"""指标服务"""

from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.indicator import Indicator, IndicatorCategory


class IndicatorService:
    """评估指标服务"""
    
    @staticmethod
    def init_builtin_indicators(db: Session):
        """初始化内置指标"""
        builtin_indicators = [
            {
                "name": "accuracy",
                "display_name": "准确率",
                "description": "模型预测正确的样本数占总样本数的比例",
                "category": IndicatorCategory.BASIC_PERFORMANCE,
                "calculation_function": "accuracy"
            },
            {
                "name": "precision",
                "display_name": "精确率",
                "description": "在所有预测为正例的样本中，正确预测的比例",
                "category": IndicatorCategory.BASIC_PERFORMANCE,
                "calculation_function": "precision_recall_f1"
            },
            {
                "name": "recall",
                "display_name": "召回率",
                "description": "在所有真正为正例的样本中，正确预测为正例的比例",
                "category": IndicatorCategory.BASIC_PERFORMANCE,
                "calculation_function": "precision_recall_f1"
            },
            {
                "name": "f1_score",
                "display_name": "F1分数",
                "description": "精确率和召回率的调和平均数",
                "category": IndicatorCategory.BASIC_PERFORMANCE,
                "calculation_function": "precision_recall_f1"
            },
            {
                "name": "bleu",
                "display_name": "BLEU分数",
                "description": "通过计算机器生成的文本与参考译文之间的n-gram匹配度来评分",
                "category": IndicatorCategory.GENERATION_TASK,
                "calculation_function": "bleu"
            },
            {
                "name": "rouge_l",
                "display_name": "ROUGE-L分数",
                "description": "基于最长公共子序列的文本生成质量评估指标",
                "category": IndicatorCategory.GENERATION_TASK,
                "calculation_function": "rouge_l"
            },
            {
                "name": "adaptability",
                "display_name": "适应性",
                "description": "衡量智能体在未经专门训练的新领域或新任务中的表现",
                "category": IndicatorCategory.GENERALIZATION,
                "calculation_function": "adaptability"
            },
            {
                "name": "collaboration_efficiency",
                "display_name": "协作效率",
                "description": "在多智能体系统中，衡量它们共同完成复杂任务的效能",
                "category": IndicatorCategory.GENERALIZATION,
                "calculation_function": "collaboration_efficiency"
            },
            {
                "name": "portability",
                "display_name": "可移植性",
                "description": "衡量将智能体从一个环境迁移到另一个时的性能保持程度",
                "category": IndicatorCategory.GENERALIZATION,
                "calculation_function": "portability"
            },
        ]
        
        for ind_data in builtin_indicators:
            existing = db.query(Indicator).filter(Indicator.name == ind_data["name"]).first()
            if not existing:
                indicator = Indicator(**ind_data, is_builtin=True)
                db.add(indicator)
        
        db.commit()
    
    @staticmethod
    def get_indicator(db: Session, indicator_id: int) -> Optional[Indicator]:
        """获取指标"""
        return db.query(Indicator).filter(Indicator.id == indicator_id).first()
    
    @staticmethod
    def get_indicators(
        db: Session,
        category: IndicatorCategory = None,
        is_active: bool = True
    ) -> List[Indicator]:
        """获取指标列表"""
        query = db.query(Indicator)
        if category:
            query = query.filter(Indicator.category == category)
        if is_active:
            query = query.filter(Indicator.is_active == True)
        return query.order_by(Indicator.category, Indicator.name).all()
    
    @staticmethod
    def create_custom_indicator(
        db: Session,
        name: str,
        display_name: str,
        description: str,
        calculation_function: str,
        config_schema: dict = None,
        default_config: dict = None
    ) -> Indicator:
        """创建自定义指标"""
        indicator = Indicator(
            name=name,
            display_name=display_name,
            description=description,
            category=IndicatorCategory.CUSTOM,
            calculation_function=calculation_function,
            config_schema=config_schema,
            default_config=default_config,
            is_builtin=False
        )
        db.add(indicator)
        db.commit()
        db.refresh(indicator)
        return indicator

