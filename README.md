# 智能体通用化特征评估工具

## 项目简介

智能体通用化特征评估工具是一款用于评估基于LLM的智能体系统通用性的标准化平台。该系统提供了全面的评估指标、自动化评估流程和深度分析报告，帮助研究人员和开发者科学地衡量和提升智能体的综合能力。

## 项目结构

```
Agent_Versa/
├── backend/              # Python后端服务
│   ├── app/              # 应用主目录
│   │   ├── main.py       # FastAPI主应用
│   │   ├── models/       # 数据模型
│   │   ├── api/          # API路由
│   │   ├── services/     # 业务逻辑
│   │   └── utils/        # 工具函数
│   └── requirements.txt  # Python依赖
├── frontend/             # 前端应用
│   ├── index.html        # 主页面
│   ├── css/              # 样式文件
│   ├── js/               # JavaScript文件
│   └── assets/           # 静态资源
├── scripts/              # 构建和运行脚本
│   ├── setup.bat         # Windows环境设置脚本
│   ├── setup.sh          # Linux/Mac环境设置脚本
│   ├── run_backend.bat   # Windows后端启动脚本
│   ├── run_backend.sh    # Linux/Mac后端启动脚本
│   └── run_frontend.bat  # Windows前端启动脚本
└── README.md            # 项目说明文档
```

## 技术栈

- **后端**: Python 3.9+, FastAPI, SQLite/PostgreSQL
- **前端**: HTML5, CSS3, JavaScript (ES6+), Vue.js 3 (CDN方式，方便新手阅读)
- **评估指标**: 支持准确率、召回率、F1、BLEU、ROUGE等标准指标
- **数据存储**: SQLite (开发环境) / PostgreSQL (生产环境)

## 快速开始

### 1. 环境要求

- Python 3.9 或更高版本
- 现代浏览器 (Chrome, Firefox, Edge等)

### 2. 安装依赖

**Windows:**
```bash
scripts\setup.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 3. 启动后端服务

**Windows:**
```bash
scripts\run_backend.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/run_backend.sh
./scripts/run_backend.sh
```

后端服务默认运行在 `http://localhost:8000`

### 4. 启动前端服务

**Windows:**
```bash
scripts\run_frontend.bat
```

**Linux/Mac:**
在浏览器中打开 `frontend/index.html` 或使用简单的HTTP服务器：
```bash
cd frontend && python -m http.server 8080
```

前端服务默认运行在 `http://localhost:8080`

### 5. 访问系统

在浏览器中访问 `http://localhost:8080`，开始使用智能体评估工具。

## 核心功能

1. **评估任务管理**: 创建、配置、执行和管理评估任务
2. **评估指标体系**: 内置多维度评估指标，支持自定义指标
3. **数据接入与处理**: 支持多种数据源接入和数据预处理
4. **核心评估引擎**: 自动化评估流程和深度分析报告
5. **系统管理**: 用户管理、权限控制、系统监控

## API文档

启动后端服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 快速开始

详细的使用说明请参考 [QUICKSTART.md](QUICKSTART.md)

## 项目结构说明

### 后端 (`backend/app/`)

- `main.py`: FastAPI主应用入口
- `models/`: 数据模型定义
  - `database.py`: 数据库配置
  - `user.py`: 用户模型
  - `task.py`: 评估任务模型
  - `indicator.py`: 评估指标模型
  - `result.py`: 评估结果模型
- `api/`: API路由
  - `tasks.py`: 任务管理API
  - `indicators.py`: 指标管理API
  - `results.py`: 结果查询API
  - `system.py`: 系统管理API
- `services/`: 业务逻辑层
  - `task_service.py`: 任务服务
  - `indicator_service.py`: 指标服务
  - `evaluation_service.py`: 评估执行服务
- `utils/`: 工具函数
  - `auth.py`: 认证工具
  - `data_loader.py`: 数据加载器
  - `indicators.py`: 指标计算器
- `data/`: 示例数据文件
  - `samples.json`: 示例评估数据集

### 前端 (`frontend/`)

- `index.html`: 主页面
- `css/style.css`: 样式文件
- `js/app.js`: Vue.js应用逻辑

### 脚本 (`scripts/`)

- `setup.bat/sh`: 环境设置脚本
- `run_backend.bat/sh`: 后端启动脚本
- `run_frontend.bat`: 前端启动脚本
- `init_database.bat/sh`: 数据库初始化脚本

## 核心功能实现

### 评估指标

系统内置了以下评估指标：

**基础性能指标**:
- 准确率 (Accuracy)
- 精确率 (Precision)
- 召回率 (Recall)
- F1分数

**生成任务指标**:
- BLEU分数
- ROUGE-L分数

**通用化特征指标**:
- 适应性 (Adaptability)
- 协作效率 (Collaboration Efficiency)
- 可移植性 (Portability)

### 评估流程

1. **任务创建**: 用户配置智能体、数据集和指标
2. **任务执行**: 系统自动加载数据，调用智能体API，计算各项指标
3. **结果聚合**: 汇总所有样本的结果，计算平均分和统计信息
4. **报告生成**: 生成综合评分、可视化图表和分析报告

## 数据流说明

### 从任务提交到分析报告的完整流程

#### 第一阶段：任务创建与提交

1. **前端创建任务**
   - 用户在前端界面填写任务信息（名称、描述、API端点、数据集路径、选择的指标等）
   - 调用 `POST /api/tasks` API创建任务

2. **后端创建任务**
   - `TaskService.create_task()` 接收任务配置
   - 如果数据集路径为空，自动设置为默认路径 `app/data/samples.json`
   - 将任务保存到数据库，状态设置为 `PENDING`
   - 返回任务ID

#### 第二阶段：任务启动与执行

3. **启动任务**
   - 前端调用 `POST /api/tasks/{task_id}/start` 启动任务
   - 后端检查任务状态（必须是 `PENDING` 或 `FAILED`）
   - 使用 FastAPI 的 `BackgroundTasks` 在后台异步执行评估

4. **执行评估任务** (`EvaluationService.execute_task`)

   **4.1 加载数据集**
   ```python
   dataset = await DataLoader.load_data(task.dataset_type, dataset_config)
   ```
   - 从 JSON/CSV/API 加载测试数据
   - 更新任务进度：`total_samples = len(dataset)`

   **4.2 获取选中的指标**
   ```python
   for ind_id in task.selected_indicators:
       indicator = IndicatorService.get_indicator(db, ind_id)
   ```
   - 从数据库获取指标对象（包含 `name`、`display_name`、`calculation_function` 等）

   **4.3 遍历数据集，计算每个样本的指标**
   
   对每个样本执行：
   - **调用智能体API** (`_call_agent`)
     - 发送 prompt 到智能体API端点
     - 获取智能体响应
     - 支持 DeepSeek/OpenAI 格式和通用格式
   
   - **准备指标数据** (`_prepare_indicator_data`)
     - 根据指标类型准备数据：
       - `accuracy/precision/recall/f1_score`: 需要 `y_true` 和 `y_pred`
       - `bleu/rouge_l`: 需要 `reference` 和 `candidate`
       - `adaptability/collaboration_efficiency/portability`: 需要特定字段
   
   - **计算指标** (`IndicatorCalculator.calculate_indicator`)
     - 根据指标名称调用对应计算函数：
       - `accuracy` → `calculate_accuracy()`
       - `precision_recall_f1` → `calculate_precision_recall_f1()`
       - `bleu` → `calculate_bleu()`
       - `rouge_l` → `calculate_rouge_l()`
     - 返回每个样本的指标得分
   
   - **更新进度**（每10个样本或完成时）

   **4.4 聚合结果** (`_aggregate_results`)
   ```python
   aggregated_results = {
       indicator_id: {
           "score": 平均分,
           "min": 最低分,
           "max": 最高分,
           "std": 标准差,
           "count": 样本数,
           "detailed": [所有样本的详细结果]
       }
   }
   ```

   **4.5 计算加权总分** (`_calculate_overall_score`)
   ```python
   overall_score = Σ(指标得分 × 指标权重) / Σ(指标权重)
   ```

   **4.6 生成分析报告** (`_generate_analysis_report`)
   - 生成文本分析报告，包含总体得分和各项指标详情

   **4.7 生成可视化数据** (`_generate_radar_chart_data`)
   ```python
   radar_chart_data = {
       "labels": [指标的中文显示名称],
       "datasets": [{
           "label": "智能体性能",
           "data": [各指标的得分]
       }]
   }
   ```

   **4.8 保存结果到数据库**
   - 创建 `EvaluationResult` 记录：
     - `overall_score`: 加权总分
     - `summary`: 统计摘要（样本数、指标数等）
     - `detailed_results`: 聚合后的详细结果（JSON）
     - `analysis_report`: 文本分析报告
     - `radar_chart_data`: 雷达图数据（JSON）
   
   - 创建 `ResultItem` 记录（每个指标一条）：
     - `indicator_id`: 指标ID
     - `score`: 指标得分
     - `weighted_score`: 加权得分
     - `raw_data`: 原始计算结果（包含 min/max/std 等）
   
   - 关联任务和结果：`task.result = result`
   - 更新任务状态为 `COMPLETED`

#### 第三阶段：获取分析报告

5. **前端查看结果**
   - 调用 `GET /api/tasks/{task_id}` 获取任务信息
   - 检查 `task.result_id` 是否存在

6. **后端返回结果** (`GET /api/results/task/{task_id}`)
   ```python
   result_items = [
       {
           "indicator_id": item.indicator_id,
           "indicator_name": item.indicator.name,  # 英文名称
           "score": item.score,
           "weighted_score": item.weighted_score,
           "raw_data": item.raw_data
       }
       for item in result.result_items
   ]
   ```
   - 从 `EvaluationResult` 获取总体结果
   - 从 `ResultItem` 获取每个指标的详细结果
   - 通过 `item.indicator` 关系获取指标信息（包括 `name` 和 `display_name`）

7. **前端渲染分析报告**
   - **总体得分卡片**: 显示 `overall_score`
   - **指标概览网格**: 遍历 `result_items`，显示每个指标的得分
   - **雷达图**: 使用 `radar_chart_data` 渲染
   - **柱状图**: 从 `result_items` 提取 `indicator_name` 和 `score` 渲染
   - **详细结果表格**: 显示所有指标的详细信息
   - **统计摘要**: 显示 `summary` 中的统计信息

### 关键数据流图

```
任务创建
  ↓
selected_indicators: [1, 2, 3]  (指标ID列表)
  ↓
任务执行
  ↓
遍历数据集 → 调用API → 计算指标
  ↓
results: [{1: {score: 0.8}, 2: {score: 0.9}, ...}, ...]  (每个样本的结果)
  ↓
聚合结果
  ↓
aggregated_results: {1: {score: 0.85, min: 0.7, max: 1.0, ...}, ...}
  ↓
保存到数据库
  ↓
EvaluationResult {
  overall_score: 0.87,
  detailed_results: {1: {...}, 2: {...}},
  radar_chart_data: {labels: [...], datasets: [...]}
}
  ↓
ResultItem [
  {indicator_id: 1, score: 0.85, indicator: {name: "accuracy", display_name: "准确率"}},
  {indicator_id: 2, score: 0.90, indicator: {name: "precision", display_name: "精确率"}},
  ...
]
  ↓
前端获取结果
  ↓
result_items: [
  {indicator_name: "accuracy", score: 0.85, ...},
  {indicator_name: "precision", score: 0.90, ...},
  ...
]
  ↓
前端渲染分析报告
```

### 指标获取的关键点

1. **指标定义存储**
   - 指标定义存储在 `indicators` 表中，包含：
     - `name`: 英文名称（如 "accuracy"）
     - `display_name`: 中文显示名称（如 "准确率"）
     - `calculation_function`: 计算函数名称

2. **指标计算**
   - 通过 `IndicatorCalculator` 类实现
   - 根据指标名称调用对应的计算方法

3. **结果存储**
   - `EvaluationResult.detailed_results`: 所有指标的聚合结果（JSON格式）
   - `ResultItem`: 每个指标的详细记录，通过 `indicator` 关系关联到指标定义

4. **前端显示**
   - 通过 `item.indicator.name` 获取英文名称
   - 通过 `item.indicator.display_name` 获取中文显示名称
   - 用于显示和图表标签

## 自定义开发

### 添加自定义指标

1. 在 `backend/app/utils/indicators.py` 中添加计算函数
2. 在 `IndicatorCalculator.calculate_indicator` 中注册新指标
3. 通过API或前端界面创建自定义指标记录

### 扩展数据源

在 `backend/app/utils/data_loader.py` 中添加新的数据加载方法。

### 自定义评估逻辑

修改 `backend/app/services/evaluation_service.py` 中的评估执行逻辑。

## 许可证

本项目为学术研究项目。

## 联系方式

如有问题或建议，请联系项目组。

