# AutoResearch Assistant

一个自主研究助手，能够自动搜索、分析、总结任何主题，并生成研究报告。基于当前最热门的AI趋势——自主研究/自动实验循环（Autonomous Research/Autoresearch）。

## 功能特性

- **自主研究循环**: 自动进行多轮搜索，深入挖掘主题
- **智能分析**: 使用LLM分析搜索结果，提取关键信息
- **报告生成**: 自动生成结构化的Markdown研究报告
- **引用追踪**: 自动记录和整理信息来源
- **可配置深度**: 支持设置研究深度（浅层/中等/深度）

## 技术栈

- Python 3.10+
- OpenAI API / OpenAI-compatible API
- DuckDuckGo Search (无需API Key)
- AsyncIO 异步处理
- Pydantic 数据验证

## 安装

```bash
# 克隆仓库
git clone https://github.com/zjjczzs/daily-ai-apps.git
cd daily-ai-apps/2026-03-15-autoresearch-assistant

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置你的API配置
```

## 配置

编辑 `.env` 文件：

```env
# OpenAI API配置
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选，用于兼容其他API
OPENAI_MODEL=gpt-4o-mini

# 研究配置
DEFAULT_RESEARCH_DEPTH=medium  # shallow, medium, deep
MAX_SEARCH_ROUNDS=5
MAX_RESULTS_PER_QUERY=10
```

## 使用方法

### 命令行使用

```bash
# 基础用法
python autoresearch.py "量子计算最新进展"

# 指定研究深度
python autoresearch.py "AI Agent架构设计" --depth deep

# 指定输出文件
python autoresearch.py "Rust异步编程" --output rust_async_report.md

# 使用特定模型
python autoresearch.py "机器学习优化算法" --model gpt-4o
```

### Python API使用

```python
import asyncio
from autoresearch import AutoResearcher, ResearchConfig

async def main():
    config = ResearchConfig(depth="medium")
    researcher = AutoResearcher(config)
    report = await researcher.research("你的研究主题")
    print(report.to_markdown())

asyncio.run(main())
```

## 研究深度说明

- **shallow (浅层)**: 1-2轮搜索，适合快速了解
- **medium (中等)**: 3-4轮搜索，平衡深度和速度
- **deep (深度)**: 5+轮搜索，全面深入研究

## 输出示例

```markdown
# 研究报告: AI Agent架构设计

> 生成时间: 2026-03-15 14:30:00
> 研究轮次: 4

## 执行摘要
[核心发现概述]

## 关键发现
1. ...
2. ...

## 详细分析
...

## 信息来源
- [1] ...
- [2] ...
```

## 工作原理

1. **查询生成**: 基于主题生成多个搜索查询
2. **搜索执行**: 使用DuckDuckGo搜索获取结果
3. **内容分析**: LLM分析搜索结果，提取关键信息
4. **迭代深入**: 基于发现生成新的查询，深入挖掘
5. **综合报告**: 整合所有信息，生成结构化报告

## 项目结构

```
2026-03-15-autoresearch-assistant/
├── autoresearch.py      # 主程序
├── requirements.txt     # 依赖
├── .env.example        # 环境变量示例
├── README.md           # 说明文档
└── .gitignore          # Git忽略文件
```

## 许可证

MIT License
