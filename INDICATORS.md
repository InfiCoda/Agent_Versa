# 评估指标详细说明

本文档详细说明了智能体通用化特征评估工具中所有评估指标的含义、计算方法和代码实现。

## 目录

- [基础性能指标](#基础性能指标)
  - [准确率 (Accuracy)](#准确率-accuracy)
  - [精确率 (Precision)](#精确率-precision)
  - [召回率 (Recall)](#召回率-recall)
  - [F1分数 (F1 Score)](#f1分数-f1-score)
- [生成任务指标](#生成任务指标)
  - [BLEU分数](#bleu分数)
  - [ROUGE-L分数](#rouge-l分数)
- [通用化特征指标](#通用化特征指标)
  - [适应性 (Adaptability)](#适应性-adaptability)
  - [协作效率 (Collaboration Efficiency)](#协作效率-collaboration-efficiency)
  - [可移植性 (Portability)](#可移植性-portability)

---

## 基础性能指标

### 准确率 (Accuracy)

#### 定义
准确率是模型预测正确的样本数占总样本数的比例。它是最直观的性能指标，表示模型整体预测的准确性。

#### 计算公式
```
Accuracy = (正确预测的样本数) / (总样本数)
```

#### 数据准备

系统使用**Jaccard相似度**算法将文本响应转换为二分类标签：

```python
# 代码位置: backend/app/services/evaluation_service.py
# _prepare_indicator_data 方法

# 1. 提取关键词（去除停用词）
stop_words = {'的', '是', '在', '了', '和', '有', '就', '不', '人', '都', ...}
y_true_words = set(re.findall(r'\b\w+\b', y_true_str.lower()))
y_true_words = {w for w in y_true_words if w not in stop_words and len(w) > 1}
y_pred_words = set(re.findall(r'\b\w+\b', y_pred_str.lower()))
y_pred_words = {w for w in y_pred_words if w not in stop_words and len(w) > 1}

# 2. 计算Jaccard相似度
intersection = len(y_true_words & y_pred_words)
union = len(y_true_words | y_pred_words)
similarity = intersection / union if union > 0 else 0.0

# 3. 相似度阈值判断（≥ 0.3 认为匹配）
is_match = similarity >= 0.3

# 4. 转换为二分类标签
y_true = [1 if is_match else 0]
y_pred = [1 if is_match else 0]
```

#### 代码实现

```python
# 代码位置: backend/app/utils/indicators.py
# calculate_accuracy 方法

@staticmethod
def calculate_accuracy(y_true: List[Any], y_pred: List[Any]) -> float:
    """计算准确率"""
    if len(y_true) != len(y_pred):
        raise ValueError("真实值和预测值长度不一致")
    return accuracy_score(y_true, y_pred)  # 使用sklearn的accuracy_score
```

**实现说明：** 使用scikit-learn的`accuracy_score`函数计算准确率，即正确预测数除以总样本数。

---

### 精确率 (Precision)

#### 定义
精确率衡量在所有被预测为正例的样本中，真正为正例的比例。它关注的是**预测为正例的准确性**。

#### 计算公式
```
Precision = TP / (TP + FP)

其中：
- TP (True Positive): 真正例（预测为正，实际为正）
- FP (False Positive): 假正例（预测为正，实际为负）
```

#### 数据准备

与准确率使用相同的文本相似度匹配策略，将匹配结果转换为二分类标签。

#### 代码实现

```python
# 代码位置: backend/app/utils/indicators.py
# calculate_precision_recall_f1 方法

@staticmethod
def calculate_precision_recall_f1(y_true: List[Any], y_pred: List[Any], 
                                   average: str = "binary") -> Dict[str, float]:
    """计算精确率、召回率和F1分数"""
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average=average, zero_division=0
    )
    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1)
    }

# 从结果中提取精确率
@staticmethod
def _extract_precision_recall_f1(result: Dict[str, float], 
                                  indicator_name: str) -> Dict[str, float]:
    if indicator_name == "precision":
        return {"score": result.get("precision", 0.0)}
    # ...
```

**实现说明：** 使用scikit-learn的`precision_recall_fscore_support`函数同时计算精确率、召回率和F1分数，然后从结果中提取精确率值。

---

### 召回率 (Recall)

#### 定义
召回率衡量在所有真正的正例中，被正确预测为正例的比例。它关注的是**找到所有正例的能力**。

#### 计算公式
```
Recall = TP / (TP + FN)

其中：
- TP (True Positive): 真正例
- FN (False Negative): 假负例（预测为负，实际为正）
```

#### 数据准备

与精确率使用相同的数据准备和计算方式。

#### 代码实现

```python
# 代码位置: backend/app/utils/indicators.py
# 使用 calculate_precision_recall_f1 方法，然后提取召回率

@staticmethod
def _extract_precision_recall_f1(result: Dict[str, float], 
                                  indicator_name: str) -> Dict[str, float]:
    if indicator_name == "recall":
        return {"score": result.get("recall", 0.0)}
    # ...
```

**实现说明：** 与精确率使用相同的计算函数，从结果中提取召回率值。

---

### F1分数 (F1 Score)

#### 定义
F1分数是精确率和召回率的**调和平均数**，用于平衡精确率和召回率，提供单一的综合性能指标。

#### 计算公式
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

#### 数据准备

基于精确率和召回率的计算结果，自动计算调和平均数。

#### 代码实现

```python
# 代码位置: backend/app/utils/indicators.py
# 使用 calculate_precision_recall_f1 方法，然后提取F1分数

@staticmethod
def _extract_precision_recall_f1(result: Dict[str, float], 
                                  indicator_name: str) -> Dict[str, float]:
    if indicator_name == "f1_score" or indicator_name == "f1":
        return {"score": result.get("f1", 0.0)}
    # ...
```

**实现说明：** 使用scikit-learn的`precision_recall_fscore_support`函数计算F1分数（精确率和召回率的调和平均数），然后从结果中提取F1值。

---

## 生成任务指标

### BLEU分数

#### 定义
BLEU (Bilingual Evaluation Understudy) 分数通过计算机器生成的文本与参考文本之间的**n-gram匹配度**来评估文本生成质量。它广泛用于机器翻译和文本生成任务。

#### 计算公式
```
BLEU = (匹配的n-gram数量) / (候选文本的n-gram总数)

其中n-gram包括1-gram, 2-gram, 3-gram, 4-gram
```

#### 数据准备

需要提供参考文本列表（`reference`字段），智能体的响应作为候选文本（`candidate`）。

#### 代码实现

```python
# 代码位置: backend/app/utils/indicators.py
# calculate_bleu 方法

@staticmethod
def calculate_bleu(reference: List[str], candidate: str, n: int = 4) -> float:
    """计算BLEU分数（简化版本）"""
    if not candidate or not reference:
        return 0.0
    
    # 1. 将文本转换为n-gram列表（n=1到4）
    def get_ngrams(text: str, n: int) -> List[str]:
        words = text.lower().split()
        if len(words) == 0:
            return []
        return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
    
    # 2. 获取候选文本的所有n-gram
    candidate_ngrams = []
    for i in range(1, n + 1):
        candidate_ngrams.extend(get_ngrams(candidate, i))
    
    if len(candidate_ngrams) == 0:
        return 0.0
    
    # 3. 对每个参考文本计算匹配数，取最大值
    max_matches = 0
    for ref in reference:
        if not ref:
            continue
        ref_ngrams = []
        for i in range(1, n + 1):
            ref_ngrams.extend(get_ngrams(ref, i))
        
        # 使用Counter统计n-gram出现次数
        ref_counter = Counter(ref_ngrams)
        cand_counter = Counter(candidate_ngrams)
        
        # 计算匹配的n-gram数量（取最小值避免重复计数）
        ref_matches = 0
        for ngram in cand_counter:
            if ngram in ref_counter:
                ref_matches += min(cand_counter[ngram], ref_counter[ngram])
        
        max_matches = max(max_matches, ref_matches)
    
    # 4. 计算精确率
    precision = max_matches / len(candidate_ngrams) if len(candidate_ngrams) > 0 else 0.0
    return precision
```

**实现说明：** 
1. 将参考文本和候选文本转换为1-gram到4-gram
2. 对每个参考文本计算匹配的n-gram数量（使用Counter统计，取最小值避免重复计数）
3. 取所有参考文本中的最大匹配数
4. 计算精确率：匹配数 / 候选文本n-gram总数

---

### ROUGE-L分数

#### 定义
ROUGE-L (Recall-Oriented Understudy for Gisting Evaluation - Longest Common Subsequence) 基于**最长公共子序列 (LCS)** 评估文本生成质量。它关注文本的语义连贯性和信息覆盖度。

#### 计算公式
```
ROUGE-L = F1分数(LCS)

其中：
- Precision = LCS长度 / 候选文本长度
- Recall = LCS长度 / 参考文本长度
- F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

#### 数据准备

需要提供参考文本列表（`reference`字段），智能体的响应作为候选文本（`candidate`）。

#### 代码实现

```python
# 代码位置: backend/app/utils/indicators.py
# calculate_rouge_l 方法

@staticmethod
def calculate_rouge_l(reference: List[str], candidate: str) -> Dict[str, float]:
    """计算ROUGE-L分数（最长公共子序列）"""
    if not candidate or not reference:
        return {"score": 0.0, "rouge_l": 0.0, "rouge_l_precision": 0.0, "rouge_l_recall": 0.0}
    
    # 1. 计算最长公共子序列（LCS）长度
    def lcs(text1: str, text2: str) -> int:
        """使用动态规划计算LCS长度"""
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
    
    # 2. 对每个参考文本计算LCS
    candidate_len = len(candidate.split())
    if candidate_len == 0:
        return {"score": 0.0, "rouge_l": 0.0, "rouge_l_precision": 0.0, "rouge_l_recall": 0.0}
    
    lcs_scores = []
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
    
    # 3. 选择召回率最高的参考文本
    best_score = max(lcs_scores, key=lambda x: x["recall"])
    
    # 4. 计算F1分数
    f1 = 2 * best_score["precision"] * best_score["recall"] / (
        best_score["precision"] + best_score["recall"]
    ) if (best_score["precision"] + best_score["recall"]) > 0 else 0.0
    
    return {
        "score": f1,
        "rouge_l": f1,
        "rouge_l_precision": best_score["precision"],
        "rouge_l_recall": best_score["recall"]
    }
```

**实现说明：** 
1. 使用动态规划算法计算候选文本与每个参考文本的最长公共子序列（LCS）长度
2. 对每个参考文本计算精确率（LCS长度/候选文本长度）和召回率（LCS长度/参考文本长度）
3. 选择召回率最高的参考文本
4. 计算F1分数（精确率和召回率的调和平均数）作为最终ROUGE-L分数

---

## 通用化特征指标

### 适应性 (Adaptability)

#### 定义
适应性衡量智能体在**未经专门训练的新领域或新任务**中的表现。它评估智能体的泛化能力和跨领域迁移能力。

#### 计算公式
```
Adaptability = 平均(各领域得分)

其中各领域得分来自不同领域的评估结果
```

#### 数据准备

需要提供多个不同领域的评估结果列表，每个结果包含该领域的性能得分。

#### 代码实现

```python
# 代码位置: backend/app/utils/indicators.py
# calculate_adaptability 方法

@staticmethod
def calculate_adaptability(results: List[Dict[str, float]]) -> float:
    """计算适应性指标（跨领域平均性能）"""
    if not results:
        return 0.0
    # 提取所有领域的得分，计算平均值
    scores = [r.get("score", 0.0) for r in results]
    return float(np.mean(scores)) if scores else 0.0
```

**实现说明：** 从多个领域的评估结果中提取得分，计算平均值作为适应性指标。

---

### 协作效率 (Collaboration Efficiency)

#### 定义
协作效率衡量在多智能体系统中，智能体们**共同完成复杂任务**的效能。它综合考虑任务质量、通信成本和执行时间。

#### 计算公式
```
Efficiency = Task Quality / (Communication Rounds × Task Time + 1)

其中：
- Task Quality: 任务完成质量 [0, 1]
- Communication Rounds: 通信轮次
- Task Time: 任务执行时间（秒）
```

#### 数据准备

需要提供以下字段：
- `task_quality`: 任务完成质量（0-1）
- `communication_rounds`: 智能体间的通信轮次
- `task_time`: 任务执行时间（秒）

#### 代码实现

```python
# 代码位置: backend/app/utils/indicators.py
# calculate_collaboration_efficiency 方法

@staticmethod
def calculate_collaboration_efficiency(
    task_quality: float,
    communication_rounds: int,
    task_time: float
) -> Dict[str, float]:
    """计算协作效率"""
    if task_time == 0:
        return {"efficiency": 0.0, "quality": task_quality, "efficiency_score": 0.0}
    
    # 效率 = 任务质量 / (通信轮次 * 时间成本 + 1)
    efficiency_score = task_quality / (communication_rounds * task_time + 1)
    
    return {
        "efficiency": efficiency_score,
        "quality": task_quality,
        "communication_rounds": communication_rounds,
        "task_time": task_time
    }
```

**实现说明：** 使用公式 `效率 = 任务质量 / (通信轮次 × 时间成本 + 1)` 计算协作效率，综合考虑任务质量、通信成本和执行时间。

---

### 可移植性 (Portability)

#### 定义
可移植性衡量将智能体从**一个环境迁移到另一个环境**时的性能保持程度。它评估智能体的环境适应能力和迁移成本。

#### 计算公式
```
Performance Loss = (Original Score - Transferred Score) / Original Score
Portability = 1 - min(Performance Loss, 1.0)

其中：
- Original Score: 原始环境中的性能得分
- Transferred Score: 迁移后环境中的性能得分
```

#### 数据准备

需要提供以下字段：
- `original_score`: 原始环境中的性能得分
- `transferred_score`: 迁移后环境中的性能得分

#### 代码实现

```python
# 代码位置: backend/app/utils/indicators.py
# calculate_portability 方法

@staticmethod
def calculate_portability(
    original_score: float,
    transferred_score: float
) -> Dict[str, float]:
    """计算可移植性"""
    if original_score == 0:
        return {"portability": 0.0, "performance_loss": 1.0}
    
    # 计算性能损失比例
    performance_loss = (original_score - transferred_score) / original_score
    # 可移植性 = 1 - 性能损失（限制在[0,1]范围内）
    portability = 1.0 - min(performance_loss, 1.0)
    
    return {
        "portability": portability,
        "performance_loss": performance_loss,
        "original_score": original_score,
        "transferred_score": transferred_score
    }
```

**实现说明：** 
1. 计算性能损失比例：`(原始得分 - 迁移后得分) / 原始得分`
2. 可移植性 = `1 - min(性能损失, 1.0)`，确保结果在[0,1]范围内

---

---

## 数据集要求

### 基础性能指标（Accuracy, Precision, Recall, F1）

**必需字段：**
```json
{
  "input": "问题或提示",
  "expected_output": "期望输出（用于匹配判断）"
}
```

**可选字段：**
- `label`: 如果提供，将优先使用此字段作为期望输出

### 生成任务指标（BLEU, ROUGE-L）

**必需字段：**
```json
{
  "input": "问题或提示",
  "reference": ["参考文本1", "参考文本2", ...]
}
```

**可选字段：**
- `expected_output`: 如果没有`reference`，将使用此字段作为参考文本

### 通用化特征指标

**适应性 (Adaptability)：**
```json
{
  "results": [
    {"score": 0.85, "domain": "技术问答"},
    {"score": 0.72, "domain": "文学创作"}
  ]
}
```

**协作效率 (Collaboration Efficiency)：**
```json
{
  "task_quality": 0.9,
  "communication_rounds": 3,
  "task_time": 10.0
}
```

**可移植性 (Portability)：**
```json
{
  "original_score": 0.9,
  "transferred_score": 0.85
}
```

---

## 注意事项

### 1. 文本相似度阈值
- 当前系统使用 **Jaccard相似度 ≥ 0.3** 作为匹配阈值
- 对于特定任务，可能需要调整阈值以获得更准确的结果

### 2. 停用词处理
- 系统会自动去除常见的中文停用词
- 停用词列表包括：的、是、在、了、和、有、就、不、人、都等

### 3. 多参考文本
- BLEU和ROUGE-L支持多个参考文本
- 系统会自动选择最佳匹配的参考文本进行计算

### 4. 指标组合使用
- 建议同时使用多个指标进行综合评估
- 不同指标关注不同方面，组合使用更全面

### 5. 数据质量
- 确保数据集中的`expected_output`和`reference`字段准确
- 参考文本应该多样化，以提高评估的鲁棒性

---

## 参考资料

- **BLEU**: Papineni, K., et al. (2002). "BLEU: a method for automatic evaluation of machine translation"
- **ROUGE**: Lin, C. Y. (2004). "ROUGE: A Package for Automatic Evaluation of Summaries"
- **Precision/Recall/F1**: 经典的分类评估指标，广泛应用于机器学习领域

---

*最后更新: 2024年*

