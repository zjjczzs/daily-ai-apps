"""
LLM Smart Router Cost Optimizer
核心路由逻辑 - 智能选择最优LLM模型
"""

from typing import Dict, List, Optional, Literal
import json
from dataclasses import dataclass
from enum import Enum

class Priority(Enum):
    SPEED = "speed"
    QUALITY = "quality"
    BALANCED = "balanced"
    COST = "cost"

@dataclass
class ModelConfig:
    name: str
    provider: str
    input_cost_per_1m: float  # $ per 1M input tokens
    output_cost_per_1m: float  # $ per 1M output tokens
    avg_speed_ms: int  # 平均响应时间
    quality_score: float  # 质量评分 0-10
    context_window: int  # 上下文窗口大小

# 模型定价数据 (2026年2月)
MODELS = {
    "gpt-4o": ModelConfig(
        name="GPT-4o",
        provider="OpenAI",
        input_cost_per_1m=2.50,
        output_cost_per_1m=10.00,
        avg_speed_ms=800,
        quality_score=9.5,
        context_window=128000
    ),
    "gpt-4o-mini": ModelConfig(
        name="GPT-4o-mini",
        provider="OpenAI",
        input_cost_per_1m=0.15,
        output_cost_per_1m=0.60,
        avg_speed_ms=400,
        quality_score=7.5,
        context_window=128000
    ),
    "claude-3-5-sonnet": ModelConfig(
        name="Claude 3.5 Sonnet",
        provider="Anthropic",
        input_cost_per_1m=3.00,
        output_cost_per_1m=15.00,
        avg_speed_ms=1000,
        quality_score=9.5,
        context_window=200000
    ),
    "claude-3-haiku": ModelConfig(
        name="Claude 3 Haiku",
        provider="Anthropic",
        input_cost_per_1m=0.25,
        output_cost_per_1m=1.25,
        avg_speed_ms=350,
        quality_score=7.0,
        context_window=200000
    ),
    "gemini-1-5-pro": ModelConfig(
        name="Gemini 1.5 Pro",
        provider="Google",
        input_cost_per_1m=3.50,
        output_cost_per_1m=10.50,
        avg_speed_ms=900,
        quality_score=9.0,
        context_window=1000000
    ),
    "gemini-1-5-flash": ModelConfig(
        name="Gemini 1.5 Flash",
        provider="Google",
        input_cost_per_1m=0.075,
        output_cost_per_1m=0.30,
        avg_speed_ms=300,
        quality_score=7.5,
        context_window=1000000
    ),
    "llama-3-1-70b": ModelConfig(
        name="Llama 3.1 70B",
        provider="Local/Ollama",
        input_cost_per_1m=0.0,
        output_cost_per_1m=0.0,
        avg_speed_ms=1500,
        quality_score=8.0,
        context_window=128000
    ),
}

class SmartRouter:
    """智能LLM路由器"""
    
    def __init__(self):
        self.models = MODELS
        
    def estimate_tokens(self, text: str) -> int:
        """估算token数量 (粗略估计: 1 token ≈ 4 chars)"""
        return len(text) // 4
    
    def estimate_output_tokens(self, prompt: str, complexity: str = "medium") -> int:
        """估算输出token数量"""
        complexity_multipliers = {
            "low": 50,
            "medium": 150,
            "high": 400,
            "very_high": 800
        }
        base = complexity_multipliers.get(complexity, 150)
        # 根据prompt长度调整
        prompt_tokens = self.estimate_tokens(prompt)
        if prompt_tokens < 20:
            return base // 2
        elif prompt_tokens > 500:
            return base * 2
        return base
    
    def analyze_complexity(self, prompt: str) -> str:
        """分析prompt复杂度"""
        prompt_lower = prompt.lower()
        
        # 复杂任务关键词
        complex_keywords = [
            "code", "programming", "algorithm", "debug", "refactor",
            "analyze", "compare", "synthesize", "architecture",
            "mathematical", "proof", "theorem", "optimization",
            "creative writing", "story", "novel", "poem"
        ]
        
        # 简单任务关键词
        simple_keywords = [
            "hello", "hi", "what is", "who is", "when", "where",
            "define", "explain briefly", "short", "quick"
        ]
        
        complex_score = sum(1 for kw in complex_keywords if kw in prompt_lower)
        simple_score = sum(1 for kw in simple_keywords if kw in prompt_lower)
        
        prompt_length = len(prompt)
        
        if complex_score >= 2 or prompt_length > 1000:
            return "high"
        elif simple_score >= 1 or prompt_length < 100:
            return "low"
        else:
            return "medium"
    
    def calculate_cost(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        """计算调用成本"""
        model = self.models[model_id]
        input_cost = (input_tokens / 1_000_000) * model.input_cost_per_1m
        output_cost = (output_tokens / 1_000_000) * model.output_cost_per_1m
        return input_cost + output_cost
    
    def score_model(self, model_id: str, prompt: str, priority: Priority) -> float:
        """为模型打分 (分数越高越推荐)"""
        model = self.models[model_id]
        complexity = self.analyze_complexity(prompt)
        
        input_tokens = self.estimate_tokens(prompt)
        output_tokens = self.estimate_output_tokens(prompt, complexity)
        cost = self.calculate_cost(model_id, input_tokens, output_tokens)
        
        if priority == Priority.COST:
            # 成本优先: 成本越低分数越高
            max_cost = 0.05  # 假设最大成本$0.05
            return max(0, (max_cost - cost) / max_cost * 100)
        
        elif priority == Priority.SPEED:
            # 速度优先: 响应时间越短分数越高
            max_time = 2000  # 2秒
            return max(0, (max_time - model.avg_speed_ms) / max_time * 100)
        
        elif priority == Priority.QUALITY:
            # 质量优先: 直接使用质量评分
            return model.quality_score * 10
        
        else:  # BALANCED
            # 平衡模式: 综合考虑质量、成本、速度
            quality_weight = 0.4
            cost_weight = 0.35
            speed_weight = 0.25
            
            # 质量分数 (0-100)
            quality_score = model.quality_score * 10
            
            # 成本分数 (成本越低分数越高)
            max_cost = 0.05
            cost_score = max(0, (max_cost - cost) / max_cost * 100)
            
            # 速度分数 (越快分数越高)
            max_time = 2000
            speed_score = max(0, (max_time - model.avg_speed_ms) / max_time * 100)
            
            return (quality_score * quality_weight + 
                    cost_score * cost_weight + 
                    speed_score * speed_weight)
    
    def route(self, prompt: str, budget_usd: Optional[float] = None, 
              priority: str = "balanced") -> Dict:
        """
        智能路由 - 选择最优模型
        
        Args:
            prompt: 用户输入
            budget_usd: 预算上限 (可选)
            priority: 优先级 (speed | quality | balanced | cost)
        
        Returns:
            包含推荐模型、成本、节省比例等信息的字典
        """
        priority_enum = Priority(priority)
        complexity = self.analyze_complexity(prompt)
        input_tokens = self.estimate_tokens(prompt)
        output_tokens = self.estimate_output_tokens(prompt, complexity)
        
        # 过滤超出预算的模型
        candidates = self.models
        if budget_usd:
            candidates = {
                k: v for k, v in self.models.items()
                if self.calculate_cost(k, input_tokens, output_tokens) <= budget_usd
            }
        
        if not candidates:
            return {
                "error": "Budget too low for any model",
                "min_required": min(
                    self.calculate_cost(m, input_tokens, output_tokens)
                    for m in self.models.keys()
                )
            }
        
        # 为所有候选模型打分并排序
        scored_models = [
            (model_id, self.score_model(model_id, prompt, priority_enum))
            for model_id in candidates.keys()
        ]
        scored_models.sort(key=lambda x: x[1], reverse=True)
        
        # 选择最佳模型
        best_model_id = scored_models[0][0]
        best_model = self.models[best_model_id]
        best_cost = self.calculate_cost(best_model_id, input_tokens, output_tokens)
        
        # 计算与最贵模型的对比
        max_cost = max(
            self.calculate_cost(m, input_tokens, output_tokens)
            for m in self.models.keys()
        )
        savings_pct = ((max_cost - best_cost) / max_cost * 100) if max_cost > 0 else 0
        
        # 生成备选方案
        alternatives = []
        for model_id, score in scored_models[1:4]:
            model = self.models[model_id]
            cost = self.calculate_cost(model_id, input_tokens, output_tokens)
            alternatives.append({
                "model_id": model_id,
                "name": model.name,
                "provider": model.provider,
                "cost": round(cost, 6),
                "quality_score": model.quality_score,
                "speed_ms": model.avg_speed_ms
            })
        
        return {
            "model_id": best_model_id,
            "name": best_model.name,
            "provider": best_model.provider,
            "cost": round(best_cost, 6),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "savings_percent": round(savings_pct, 1),
            "complexity": complexity,
            "priority": priority,
            "quality_score": best_model.quality_score,
            "speed_ms": best_model.avg_speed_ms,
            "context_window": best_model.context_window,
            "alternatives": alternatives
        }
    
    def batch_route(self, prompts: List[str], budget_usd: Optional[float] = None,
                    priority: str = "balanced") -> List[Dict]:
        """批量路由多个prompt"""
        return [self.route(p, budget_usd, priority) for p in prompts]
    
    def get_all_models(self) -> Dict:
        """获取所有模型信息"""
        return {
            model_id: {
                "name": m.name,
                "provider": m.provider,
                "input_cost_per_1m": m.input_cost_per_1m,
                "output_cost_per_1m": m.output_cost_per_1m,
                "avg_speed_ms": m.avg_speed_ms,
                "quality_score": m.quality_score,
                "context_window": m.context_window
            }
            for model_id, m in self.models.items()
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LLM Smart Router CLI")
    parser.add_argument("--prompt", "-p", help="Single prompt to route")
    parser.add_argument("--file", "-f", help="File containing prompts (one per line)")
    parser.add_argument("--budget", "-b", type=float, default=None, help="Budget in USD")
    parser.add_argument("--priority", choices=["speed", "quality", "balanced", "cost"],
                        default="balanced", help="Routing priority")
    parser.add_argument("--output", "-o", help="Output file for batch results")
    
    args = parser.parse_args()
    
    router = SmartRouter()
    
    if args.prompt:
        result = router.route(args.prompt, args.budget, args.priority)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.file:
        with open(args.file, 'r') as f:
            prompts = [line.strip() for line in f if line.strip()]
        results = router.batch_route(prompts, args.budget, args.priority)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Results saved to {args.output}")
        else:
            print(json.dumps(results, indent=2, ensure_ascii=False))
    
    else:
        # Demo mode
        print("🧠 LLM Smart Router - Demo Mode\n")
        test_prompts = [
            "Hello!",
            "Explain quantum computing in simple terms",
            "Write a Python function to sort a list",
            "Analyze the themes in Shakespeare's Hamlet",
            "Debug this code: def fib(n): return fib(n-1) + fib(n-2)"
        ]
        
        for prompt in test_prompts:
            print(f"\n📝 Prompt: {prompt[:50]}...")
            result = router.route(prompt, priority="balanced")
            print(f"   ➜ 推荐: {result['name']} ({result['provider']})")
            print(f"   💰 成本: ${result['cost']:.6f} (节省 {result['savings_percent']}%)")
            print(f"   📊 复杂度: {result['complexity']}")
