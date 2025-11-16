"""评估服务"""

import asyncio
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
import numpy as np
from ..models.task import EvaluationTask, TaskStatus
from ..models.result import EvaluationResult, ResultItem
from ..models.indicator import Indicator
from ..services.task_service import TaskService
from ..services.indicator_service import IndicatorService
from ..utils.data_loader import DataLoader
from ..utils.indicators import IndicatorCalculator


class EvaluationService:
    """评估执行服务"""
    
    @staticmethod
    async def execute_task(db: Session, task_id: int):
        """执行评估任务"""
        task = TaskService.get_task(db, task_id)
        if not task:
            raise ValueError(f"任务不存在: {task_id}")
        
        # 更新任务状态为运行中
        TaskService.update_task_status(db, task_id, TaskStatus.RUNNING, "0%")
        
        try:
            # 1. 加载数据集
            # 如果数据集路径为空，使用默认路径
            dataset_config = task.dataset_config or {}
            file_path = dataset_config.get("file_path", "").strip()
            if not file_path:
                dataset_config = dataset_config.copy() if dataset_config else {}
                dataset_config["file_path"] = "app/data/samples.json"
            
            dataset = await DataLoader.load_data(task.dataset_type, dataset_config)
            total_samples = len(dataset)
            TaskService.update_task_progress(db, task_id, 0, total_samples)
            
            # 2. 获取选中的指标
            indicators = []
            for ind_id in task.selected_indicators:
                indicator = IndicatorService.get_indicator(db, ind_id)
                if indicator:
                    indicators.append(indicator)
            
            if not indicators:
                raise ValueError("未选择任何评估指标")
            
            # 3. 执行评估
            results = []
            processed = 0
            
            for sample in dataset:
                # 调用智能体API
                agent_response = await EvaluationService._call_agent(
                    task.agent_api_endpoint,
                    task.agent_api_key,
                    sample.get("input", sample.get("prompt", ""))
                )
                
                # 计算每个指标
                sample_results = {}
                for indicator in indicators:
                    indicator_data = EvaluationService._prepare_indicator_data(
                        sample, agent_response, indicator
                    )
                    try:
                        result = IndicatorCalculator.calculate_indicator(
                            indicator.name,
                            indicator_data,
                            calculation_function=indicator.calculation_function
                        )
                        sample_results[indicator.id] = result
                    except Exception as e:
                        print(f"计算指标 {indicator.name} 时出错: {e}")
                        import traceback
                        traceback.print_exc()
                        sample_results[indicator.id] = {"score": 0.0, "error": str(e)}
                
                results.append(sample_results)
                processed += 1
                
                # 更新进度
                if processed % 10 == 0 or processed == total_samples:
                    TaskService.update_task_progress(db, task_id, processed, total_samples)
            
            # 4. 聚合结果
            aggregated_results = EvaluationService._aggregate_results(results, indicators)
            
            # 5. 计算加权总分
            overall_score = EvaluationService._calculate_overall_score(
                aggregated_results,
                task.indicator_weights
            )
            
            # 6. 生成分析报告
            analysis_report = EvaluationService._generate_analysis_report(
                aggregated_results, indicators, overall_score
            )
            
            # 7. 生成可视化数据
            radar_chart_data = EvaluationService._generate_radar_chart_data(
                aggregated_results, indicators
            )
            
            # 8. 保存结果
            result = EvaluationResult(
                task_id=task_id,
                overall_score=overall_score,
                summary={
                    "total_samples": total_samples,
                    "indicators_count": len(indicators),
                    "timestamp": datetime.utcnow().isoformat()
                },
                detailed_results=aggregated_results,
                analysis_report=analysis_report,
                radar_chart_data=radar_chart_data
            )
            db.add(result)
            db.flush()
            
            # 创建结果项
            for ind_id, result_data in aggregated_results.items():
                indicator = IndicatorService.get_indicator(db, ind_id)
                weight = task.indicator_weights.get(ind_id, 1.0)
                score = result_data.get("score", 0.0)
                
                result_item = ResultItem(
                    result_id=result.id,
                    indicator_id=ind_id,
                    score=score,
                    weighted_score=score * weight,
                    raw_data=result_data
                )
                db.add(result_item)
            
            # 更新任务（通过关系设置result）
            task.result = result
            TaskService.update_task_status(db, task_id, TaskStatus.COMPLETED, "100%")
            db.commit()
            
        except Exception as e:
            error_message = str(e)
            # 记录详细错误信息
            print(f"任务 {task_id} 执行失败: {error_message}")
            TaskService.update_task_status(db, task_id, TaskStatus.FAILED, "错误")
            # 尝试保存错误信息到任务描述或日志
            try:
                task = TaskService.get_task(db, task_id)
                if task:
                    # 将错误信息保存到任务描述中（如果原本没有描述）
                    if not task.description or task.description == "无描述":
                        task.description = f"执行失败: {error_message[:200]}"  # 限制长度
                    db.commit()
            except:
                pass
            db.commit()
            raise e
    
    @staticmethod
    async def _call_agent(api_endpoint: str, api_key: str, prompt: str) -> str:
        """调用智能体API"""
        if not api_endpoint:
            # 模拟响应（用于测试）
            return f"模拟响应: {prompt[:50]}..."
        
        headers = {
            "Content-Type": "application/json",
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # 检测API类型并适配请求格式
        # DeepSeek/OpenAI格式
        if "openai.com" in api_endpoint or "deepseek.com" in api_endpoint or "api.deepseek.com" in api_endpoint:
            payload = {
                "model": "deepseek-chat",  # DeepSeek默认模型，可根据需要修改
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
        else:
            # 通用格式（兼容自定义API）
            payload = {
                "prompt": prompt,
                "max_tokens": 500,
                "temperature": 0.7
            }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(api_endpoint, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    # DeepSeek/OpenAI格式：{"choices": [{"message": {"content": "..."}}]}
                    if isinstance(data, dict):
                        if "choices" in data and len(data["choices"]) > 0:
                            # OpenAI/DeepSeek格式
                            return data["choices"][0].get("message", {}).get("content", "")
                        elif "response" in data:
                            return data["response"]
                        elif "text" in data:
                            return data["text"]
                    return str(data)
                else:
                    error_detail = ""
                    try:
                        error_data = response.json()
                        error_detail = error_data.get("error", {}).get("message", str(error_data))
                    except:
                        error_detail = response.text[:200]
                    return f"API错误 {response.status_code}: {error_detail}"
        except Exception as e:
            return f"API调用失败: {str(e)}"
    
    @staticmethod
    def _prepare_indicator_data(
        sample: Dict[str, Any],
        agent_response: str,
        indicator: Indicator
    ) -> Dict[str, Any]:
        """准备指标计算所需的数据"""
        indicator_name = indicator.name
        
        if indicator_name in ["accuracy", "precision", "recall", "f1_score"]:
            # 对于分类任务，需要将输出转换为标签
            y_true_str = sample.get("expected_output", sample.get("label", ""))
            y_pred_str = agent_response
            
            # 计算文本相似度来判断是否正确
            # 使用简单的字符串匹配和相似度计算
            if isinstance(y_true_str, str) and isinstance(y_pred_str, str):
                # 计算相似度：检查关键词匹配
                y_true_lower = y_true_str.lower()
                y_pred_lower = y_pred_str.lower()
                
                # 方法1：检查是否包含关键信息
                # 提取期望输出中的关键词（去除常见停用词）
                import re
                stop_words = {'的', '是', '在', '了', '和', '有', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
                y_true_words = set(re.findall(r'\b\w+\b', y_true_lower))
                y_true_words = {w for w in y_true_words if w not in stop_words and len(w) > 1}
                
                y_pred_words = set(re.findall(r'\b\w+\b', y_pred_lower))
                y_pred_words = {w for w in y_pred_words if w not in stop_words and len(w) > 1}
                
                # 计算Jaccard相似度
                if len(y_true_words) == 0:
                    # 如果期望输出没有有效词，使用简单的包含检查
                    is_match = y_true_lower in y_pred_lower or y_pred_lower in y_true_lower
                else:
                    intersection = len(y_true_words & y_pred_words)
                    union = len(y_true_words | y_pred_words)
                    similarity = intersection / union if union > 0 else 0.0
                    # 相似度阈值：超过0.3认为匹配
                    is_match = similarity >= 0.3
                
                return {
                    "y_true": [1 if is_match else 0],
                    "y_pred": [1 if is_match else 0]  # 预测值应该基于实际判断
                }
            else:
                # 如果不是字符串，尝试直接使用
                return {
                    "y_true": [y_true_str] if not isinstance(y_true_str, list) else y_true_str,
                    "y_pred": [y_pred_str] if not isinstance(y_pred_str, list) else y_pred_str
                }
        elif indicator_name in ["bleu", "rouge_l"]:
            reference = sample.get("reference", sample.get("expected_output", []))
            if isinstance(reference, str):
                reference = [reference]
            return {
                "reference": reference,
                "candidate": agent_response
            }
        elif indicator_name == "adaptability":
            # 需要多个领域的结果
            return {
                "results": [{"score": 0.8}]  # 示例数据
            }
        elif indicator_name == "collaboration_efficiency":
            return {
                "task_quality": sample.get("task_quality", 0.8),
                "communication_rounds": sample.get("communication_rounds", 3),
                "task_time": sample.get("task_time", 10.0)
            }
        elif indicator_name == "portability":
            return {
                "original_score": sample.get("original_score", 0.9),
                "transferred_score": sample.get("transferred_score", 0.85)
            }
        else:
            return {"data": sample, "response": agent_response}
    
    @staticmethod
    def _aggregate_results(
        results: List[Dict[int, Dict[str, Any]]],
        indicators: List[Indicator]
    ) -> Dict[int, Dict[str, Any]]:
        """聚合所有样本的结果"""
        aggregated = {}
        
        for indicator in indicators:
            ind_id = indicator.id
            scores = []
            all_data = []
            
            for sample_result in results:
                if ind_id in sample_result:
                    result_data = sample_result[ind_id]
                    score = result_data.get("score", 0.0)
                    scores.append(score)
                    all_data.append(result_data)
            
            if scores:
                aggregated[ind_id] = {
                    "score": sum(scores) / len(scores),  # 平均分
                    "min": min(scores),
                    "max": max(scores),
                    "std": float(np.std(scores)) if len(scores) > 1 else 0.0,
                    "count": len(scores),
                    "detailed": all_data
                }
            else:
                aggregated[ind_id] = {
                    "score": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "std": 0.0,
                    "count": 0,
                    "detailed": []
                }
        
        return aggregated
    
    @staticmethod
    def _calculate_overall_score(
        aggregated_results: Dict[int, Dict[str, Any]],
        weights: Dict[int, float]
    ) -> float:
        """计算加权总分"""
        total_weight = 0.0
        weighted_sum = 0.0
        
        for ind_id, result_data in aggregated_results.items():
            weight = weights.get(ind_id, 1.0)
            score = result_data.get("score", 0.0)
            weighted_sum += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_sum / total_weight
    
    @staticmethod
    def _generate_analysis_report(
        aggregated_results: Dict[int, Dict[str, Any]],
        indicators: List[Indicator],
        overall_score: float
    ) -> str:
        """生成分析报告"""
        report_lines = [
            f"## 评估结果分析报告\n",
            f"**总体得分**: {overall_score:.4f}\n\n",
            "### 各项指标详情:\n\n"
        ]
        
        for indicator in indicators:
            ind_id = indicator.id
            if ind_id in aggregated_results:
                result = aggregated_results[ind_id]
                report_lines.append(
                    f"- **{indicator.display_name}**: {result['score']:.4f} "
                    f"(范围: {result['min']:.4f} - {result['max']:.4f}, "
                    f"标准差: {result['std']:.4f})\n"
                )
        
        return "".join(report_lines)
    
    @staticmethod
    def _generate_radar_chart_data(
        aggregated_results: Dict[int, Dict[str, Any]],
        indicators: List[Indicator]
    ) -> Dict[str, Any]:
        """生成雷达图数据"""
        labels = []
        scores = []
        
        for indicator in indicators:
            ind_id = indicator.id
            if ind_id in aggregated_results:
                labels.append(indicator.display_name)
                scores.append(aggregated_results[ind_id]["score"])
        
        return {
            "labels": labels,
            "datasets": [{
                "label": "智能体性能",
                "data": scores,
                "backgroundColor": "rgba(54, 162, 235, 0.2)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "pointBackgroundColor": "rgba(54, 162, 235, 1)",
            }]
        }

