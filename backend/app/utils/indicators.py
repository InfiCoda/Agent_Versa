"""评估指标计算器"""

import re
from typing import List, Dict, Any, Optional
from collections import Counter
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


class IndicatorCalculator:
    """评估指标计算器"""
    
    @staticmethod
    def calculate_accuracy(y_true: List[Any], y_pred: List[Any]) -> float:
        """计算准确率"""
        if len(y_true) != len(y_pred):
            raise ValueError("真实值和预测值长度不一致")
        return accuracy_score(y_true, y_pred)
    
    @staticmethod
    def calculate_precision_recall_f1(y_true: List[Any], y_pred: List[Any], average: str = "binary") -> Dict[str, float]:
        """计算精确率、召回率和F1分数"""
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average=average, zero_division=0
        )
        return {
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1)
        }
    
    @staticmethod
    def calculate_bleu(reference: List[str], candidate: str, n: int = 4) -> float:
        """计算BLEU分数（简化版本）"""
        if not candidate or not reference:
            return 0.0
        
        # 将文本转换为n-gram列表
        def get_ngrams(text: str, n: int) -> List[str]:
            words = text.lower().split()
            if len(words) == 0:
                return []
            return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
        
        # 获取候选文本的n-gram
        candidate_ngrams = []
        for i in range(1, n + 1):
            candidate_ngrams.extend(get_ngrams(candidate, i))
        
        # 计算每个n-gram的最大匹配数
        matches = 0
        total_ngrams = len(candidate_ngrams)
        
        if total_ngrams == 0:
            return 0.0
        
        # 对每个参考文本计算匹配数，取最大值
        max_matches = 0
        for ref in reference:
            if not ref:
                continue
            ref_ngrams = []
            for i in range(1, n + 1):
                ref_ngrams.extend(get_ngrams(ref, i))
            
            ref_counter = Counter(ref_ngrams)
            cand_counter = Counter(candidate_ngrams)
            
            ref_matches = 0
            for ngram in cand_counter:
                if ngram in ref_counter:
                    ref_matches += min(cand_counter[ngram], ref_counter[ngram])
            
            max_matches = max(max_matches, ref_matches)
        
        precision = max_matches / total_ngrams if total_ngrams > 0 else 0.0
        return precision
    
    @staticmethod
    def calculate_rouge_l(reference: List[str], candidate: str) -> Dict[str, float]:
        """计算ROUGE-L分数（最长公共子序列）"""
        if not candidate or not reference:
            return {"score": 0.0, "rouge_l": 0.0, "rouge_l_precision": 0.0, "rouge_l_recall": 0.0}
        
        def lcs(text1: str, text2: str) -> int:
            """计算最长公共子序列长度"""
            words1 = text1.lower().split()
            words2 = text2.lower().split()
            m, n = len(words1), len(words2)
            if m == 0 or n == 0:
                return 0
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if words1[i-1] == words2[j-1]:
                        dp[i][j] = dp[i-1][j-1] + 1
                    else:
                        dp[i][j] = max(dp[i-1][j], dp[i][j-1])
            
            return dp[m][n]
        
        # 计算与每个参考文本的LCS
        lcs_scores = []
        candidate_len = len(candidate.split())
        
        if candidate_len == 0:
            return {"score": 0.0, "rouge_l": 0.0, "rouge_l_precision": 0.0, "rouge_l_recall": 0.0}
        
        for ref in reference:
            if not ref:
                continue
            ref_len = len(ref.split())
            if ref_len == 0:
                continue
            lcs_len = lcs(ref, candidate)
            precision = lcs_len / candidate_len if candidate_len > 0 else 0.0
            recall = lcs_len / ref_len if ref_len > 0 else 0.0
            lcs_scores.append({
                "lcs": lcs_len,
                "precision": precision,
                "recall": recall
            })
        
        if not lcs_scores:
            return {"score": 0.0, "rouge_l": 0.0, "rouge_l_precision": 0.0, "rouge_l_recall": 0.0}
        
        # 取最大值
        best_score = max(lcs_scores, key=lambda x: x["recall"])
        f1 = 2 * best_score["precision"] * best_score["recall"] / (
            best_score["precision"] + best_score["recall"]
        ) if (best_score["precision"] + best_score["recall"]) > 0 else 0.0
        
        return {
            "score": f1,
            "rouge_l": f1,
            "rouge_l_precision": best_score["precision"],
            "rouge_l_recall": best_score["recall"]
        }
    
    @staticmethod
    def calculate_adaptability(results: List[Dict[str, float]]) -> float:
        """计算适应性指标（跨领域平均性能）"""
        if not results:
            return 0.0
        # 计算不同领域的平均得分
        scores = [r.get("score", 0.0) for r in results]
        return float(np.mean(scores)) if scores else 0.0
    
    @staticmethod
    def calculate_collaboration_efficiency(
        task_quality: float,
        communication_rounds: int,
        task_time: float
    ) -> Dict[str, float]:
        """计算协作效率"""
        if task_time == 0:
            return {"efficiency": 0.0, "quality": task_quality, "efficiency_score": 0.0}
        
        # 效率 = 任务质量 / (通信轮次 * 时间成本)
        efficiency_score = task_quality / (communication_rounds * task_time + 1)
        
        return {
            "efficiency": efficiency_score,
            "quality": task_quality,
            "communication_rounds": communication_rounds,
            "task_time": task_time
        }
    
    @staticmethod
    def calculate_portability(
        original_score: float,
        transferred_score: float
    ) -> Dict[str, float]:
        """计算可移植性"""
        if original_score == 0:
            return {"portability": 0.0, "performance_loss": 1.0}
        
        performance_loss = (original_score - transferred_score) / original_score
        portability = 1.0 - min(performance_loss, 1.0)  # 确保在[0,1]范围内
        
        return {
            "portability": portability,
            "performance_loss": performance_loss,
            "original_score": original_score,
            "transferred_score": transferred_score
        }
    
    @staticmethod
    def calculate_indicator(
        indicator_name: str,
        data: Dict[str, Any],
        calculation_function: str = None
    ) -> Dict[str, Any]:
        """根据指标名称计算对应的指标值
        
        Args:
            indicator_name: 指标名称（如 "accuracy", "precision"）
            data: 计算所需的数据
            calculation_function: 计算函数名称（如果提供，优先使用）
        """
        # 如果提供了calculation_function，优先使用它
        func_name = calculation_function or indicator_name
        
        calculator_map = {
            "accuracy": lambda d: {"score": IndicatorCalculator.calculate_accuracy(
                d.get("y_true", []), d.get("y_pred", [])
            )},
            "precision_recall_f1": lambda d, ind_name=indicator_name: IndicatorCalculator._extract_precision_recall_f1(
                IndicatorCalculator.calculate_precision_recall_f1(
                    d.get("y_true", []), d.get("y_pred", [])
                ),
                ind_name
            ),
            "precision": lambda d: IndicatorCalculator._extract_precision_recall_f1(
                IndicatorCalculator.calculate_precision_recall_f1(
                    d.get("y_true", []), d.get("y_pred", [])
                ),
                "precision"
            ),
            "recall": lambda d: IndicatorCalculator._extract_precision_recall_f1(
                IndicatorCalculator.calculate_precision_recall_f1(
                    d.get("y_true", []), d.get("y_pred", [])
                ),
                "recall"
            ),
            "f1_score": lambda d: IndicatorCalculator._extract_precision_recall_f1(
                IndicatorCalculator.calculate_precision_recall_f1(
                    d.get("y_true", []), d.get("y_pred", [])
                ),
                "f1_score"
            ),
            "bleu": lambda d: {"score": IndicatorCalculator.calculate_bleu(
                d.get("reference", []), d.get("candidate", "")
            )},
            "rouge_l": lambda d: IndicatorCalculator.calculate_rouge_l(
                d.get("reference", []), d.get("candidate", "")
            ),
            "adaptability": lambda d: {"score": IndicatorCalculator.calculate_adaptability(
                d.get("results", [])
            )},
            "collaboration_efficiency": lambda d: IndicatorCalculator.calculate_collaboration_efficiency(
                d.get("task_quality", 0.0),
                d.get("communication_rounds", 0),
                d.get("task_time", 1.0)
            ),
            "portability": lambda d: IndicatorCalculator.calculate_portability(
                d.get("original_score", 0.0),
                d.get("transferred_score", 0.0)
            ),
        }
        
        # 首先尝试使用calculation_function，如果不存在则使用indicator_name
        if func_name in calculator_map:
            return calculator_map[func_name](data)
        elif indicator_name in calculator_map:
            return calculator_map[indicator_name](data)
        else:
            raise ValueError(f"不支持的指标: {indicator_name} (calculation_function: {func_name})")
    
    @staticmethod
    def _extract_precision_recall_f1(result: Dict[str, float], indicator_name: str) -> Dict[str, float]:
        """从precision_recall_f1结果中提取指定指标的值"""
        if indicator_name == "precision":
            return {"score": result.get("precision", 0.0)}
        elif indicator_name == "recall":
            return {"score": result.get("recall", 0.0)}
        elif indicator_name == "f1_score" or indicator_name == "f1":
            return {"score": result.get("f1", 0.0)}
        else:
            return result

