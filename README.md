# LLM智能路由成本优化器 (LLM Smart Router Cost Optimizer)

一个基于ClawRouter概念的智能LLM路由工具，帮助开发者自动选择最优模型，显著降低推理成本。

## ✨ 核心功能

- 🧠 **智能模型选择**: 根据任务复杂度自动推荐最优LLM
- 💰 **成本计算器**: 实时计算多模型调用成本
- 🔄 **动态路由**: 模拟x402微支付路由策略
- 📊 **可视化仪表板**: 直观展示成本节省效果
- 🔌 **多提供商支持**: OpenAI, Anthropic, Google, 本地模型等

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python app.py
```

然后访问 http://localhost:5000

### 使用CLI工具

```bash
# 计算单个请求成本
python router.py --prompt "解释量子计算" --budget 0.01

# 批量处理文件
python router.py --file prompts.txt --output results.json
```

## 📁 项目结构

```
llm-router-optimizer/
├── app.py              # Flask Web应用
├── router.py           # 核心路由逻辑
├── cost_models.py      # 成本模型定义
├── templates/
│   └── index.html      # Web界面
├── static/
│   └── style.css       # 样式文件
├── requirements.txt    # Python依赖
└── README.md          # 说明文档
```

## 💡 使用示例

### Web界面

1. 输入你的prompt
2. 设置预算上限
3. 系统智能选择最优模型
4. 查看成本对比和节省比例

### Python API

```python
from router import SmartRouter

router = SmartRouter()
result = router.route(
    prompt="生成一段Python代码",
    budget_usd=0.005,
    priority="balanced"  # speed | quality | balanced
)

print(f"推荐模型: {result['model']}")
print(f"预估成本: ${result['cost']:.6f}")
print(f"预计节省: {result['savings']}%")
```

## 🔧 支持的模型

| 提供商 | 模型 | 输入$/1M tokens | 输出$/1M tokens |
|--------|------|-----------------|-----------------|
| OpenAI | GPT-4o | $2.50 | $10.00 |
| OpenAI | GPT-4o-mini | $0.15 | $0.60 |
| Anthropic | Claude 3.5 Sonnet | $3.00 | $15.00 |
| Anthropic | Claude 3 Haiku | $0.25 | $1.25 |
| Google | Gemini 1.5 Pro | $3.50 | $10.50 |
| Google | Gemini 1.5 Flash | $0.075 | $0.30 |
| 本地 | Ollama/Llama | $0.00 | $0.00 |

## 🎯 路由策略

- **Speed**: 优先选择响应最快的模型
- **Quality**: 优先选择输出质量最高的模型
- **Balanced**: 质量与成本的最佳平衡
- **Cost**: 严格按预算选择最便宜方案

## 📊 成本节省

基于模拟数据，相比单一使用GPT-4o，本路由系统可节省:
- 🟢 简单任务: 85-95% 成本
- 🟡 中等任务: 60-75% 成本
- 🔴 复杂任务: 20-40% 成本

## 📝 License

MIT License

## 🔗 参考

- 灵感来源: [ClawRouter](https://github.com/BlockRunAI/ClawRouter)
- 相关技术: x402 micropayments, LLM routing, cost optimization
