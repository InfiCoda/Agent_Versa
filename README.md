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

