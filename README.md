# 智能客服工单分类与自动路由系统

一个基于 LangChain 与 DeepSeek API 的中文智能客服工单处理练习项目。演示从自然语言工单中识别用户意图、提取关键信息、生成结构化结果，并根据分类分配处理部门。

> **项目性质说明：** 本项目为个人学习与求职作品集练习。仓库中的示例工单均为人工编写的模拟数据，不来自真实企业客服系统，不包含真实客户信息，也不代表任何企业的真实工单分布或业务表现。

## 功能

- 中文工单分类：退款申请、技术支持、客户投诉、产品咨询
- 提取工单摘要、订单号、涉及金额、紧急程度
- 使用 Pydantic 定义结构化输出
- 根据分类规则自动分配处理部门
- 支持单条分析与 CSV 批量处理
- Streamlit 交互界面
- 离线规则模式，无需 API Key 即可体验基础流程

## 技术栈

Python、LangChain、DeepSeek API、Pydantic、Streamlit、Pandas、Pytest

## 项目结构

```text
intelligent-ticket-classifier/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── data/sample_tickets.csv
├── src/
│   ├── __init__.py
│   ├── schemas.py
│   ├── classifier.py
│   └── router.py
└── tests/
    └── test_router.py
```

## 环境配置

建议使用 Python 3.10 或更高版本。

### 1. 克隆项目并安装依赖

```bash
git clone https://github.com/YU-270027/intelligent-ticket-classifier.git
cd intelligent-ticket-classifier
python -m venv .venv
```

Windows PowerShell 激活环境：`.venv\Scripts\Activate.ps1`

macOS / Linux 激活环境：`source .venv/bin/activate`

安装依赖：`pip install -r requirements.txt`

### 2. 配置 DeepSeek API（可选）

复制 `.env.example` 并重命名为 `.env`，填入你自己创建的 API Key：

```env
DEEPSEEK_API_KEY=在这里填写你自己的密钥
DEEPSEEK_MODEL=deepseek-chat
```

**不要将真实 API Key 提交到 GitHub。** 项目已通过 `.gitignore` 忽略 `.env` 文件。

### 3. 启动应用

```bash
streamlit run app.py
```

在侧边栏选择“DeepSeek API 模式”或“离线规则模式”。

## 使用说明

- **单条分析：** 输入工单文本，查看分类、摘要、订单号、金额、紧急程度和建议处理部门。
- **批量处理：** 上传包含“工单内容”列的 CSV 文件，批量分析并下载结果。
- **离线模式：** 使用关键词规则进行基础分类，不调用外部模型。该模式仅用于演示流程，不代表大语言模型的语义理解能力。

## 分类与路由规则

| 工单类别 | 默认处理部门 |
| --- | --- |
| 退款申请 | 售后退款组 |
| 技术支持 | 技术支持组 |
| 客户投诉 | 客户服务与质检组 |
| 产品咨询 | 产品咨询组 |

模型负责输出结构化分类；部门分配由本地路由规则完成。对于多意图、信息不足或判断不确定的工单，系统会标记人工复核。

## 数据说明

`data/sample_tickets.csv` 中的数据为人工编写的虚构示例，仅用于功能演示和基础测试。示例规模较小，不适合用于训练、统计真实客服业务规律或证明模型准确率。后续可在明确数据授权与隐私合规的前提下，替换为公开或脱敏数据集。

## 测试

```bash
pytest -q
```

当前测试覆盖本地路由规则与离线模式，不需要配置 API Key，也不会产生 API 调用费用。

## 当前限制与后续迭代

- 离线模式基于关键词规则，复杂语义、多意图和反讽可能判断错误。
- API 模式的输出质量受模型、提示词和输入文本质量影响。
- 当前示例数据为模拟数据，尚未开展有标注测试集上的系统性评估。
- 后续可增加人工复核队列、置信度评估、日志追踪、错误分析和更全面的测试集。

## 项目边界

这是一个个人工程练习原型，不是已部署的企业客服系统。分类、路由和界面用于展示技术实现思路，不应未经人工审核直接用于真实客户服务决策。
