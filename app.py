"""
Flask Web应用 - LLM智能路由成本优化器
"""

from flask import Flask, render_template, request, jsonify
from router import SmartRouter, MODELS
import os

app = Flask(__name__)
router = SmartRouter()

@app.route('/')
def index():
    """主页面"""
    models_info = router.get_all_models()
    return render_template('index.html', models=models_info)

@app.route('/api/route', methods=['POST'])
def api_route():
    """API: 路由单个prompt"""
    data = request.json
    prompt = data.get('prompt', '')
    budget = data.get('budget')
    priority = data.get('priority', 'balanced')
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    try:
        budget_float = float(budget) if budget else None
    except (ValueError, TypeError):
        budget_float = None
    
    result = router.route(prompt, budget_float, priority)
    return jsonify(result)

@app.route('/api/batch', methods=['POST'])
def api_batch():
    """API: 批量路由"""
    data = request.json
    prompts = data.get('prompts', [])
    budget = data.get('budget')
    priority = data.get('priority', 'balanced')
    
    if not prompts or not isinstance(prompts, list):
        return jsonify({"error": "Prompts array is required"}), 400
    
    try:
        budget_float = float(budget) if budget else None
    except (ValueError, TypeError):
        budget_float = None
    
    results = router.batch_route(prompts, budget_float, priority)
    
    # 计算总成本
    total_cost = sum(r.get('cost', 0) for r in results if 'cost' in r)
    total_savings = sum(r.get('savings_percent', 0) for r in results if 'savings_percent' in r) / len(results) if results else 0
    
    return jsonify({
        "results": results,
        "summary": {
            "total_prompts": len(prompts),
            "total_cost": round(total_cost, 6),
            "avg_savings_percent": round(total_savings, 1)
        }
    })

@app.route('/api/models')
def api_models():
    """API: 获取所有模型信息"""
    return jsonify(router.get_all_models())

@app.route('/api/compare', methods=['POST'])
def api_compare():
    """API: 对比所有模型对某个prompt的成本"""
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    from router import Priority
    
    comparisons = []
    for model_id, model in MODELS.items():
        result = router.route(prompt, priority="balanced")
        
        # 重新计算这个特定模型的成本
        input_tokens = router.estimate_tokens(prompt)
        complexity = router.analyze_complexity(prompt)
        output_tokens = router.estimate_output_tokens(prompt, complexity)
        cost = router.calculate_cost(model_id, input_tokens, output_tokens)
        
        comparisons.append({
            "model_id": model_id,
            "name": model.name,
            "provider": model.provider,
            "cost": round(cost, 6),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "quality_score": model.quality_score,
            "speed_ms": model.avg_speed_ms
        })
    
    # 按成本排序
    comparisons.sort(key=lambda x: x['cost'])
    
    return jsonify({
        "prompt": prompt,
        "comparisons": comparisons
    })

@app.route('/api/stats')
def api_stats():
    """API: 获取系统统计信息"""
    models = router.get_all_models()
    
    providers = set(m['provider'] for m in models.values())
    
    cheapest = min(models.items(), key=lambda x: x[1]['input_cost_per_1m'] + x[1]['output_cost_per_1m'])
    fastest = min(models.items(), key=lambda x: x[1]['avg_speed_ms'])
    best_quality = max(models.items(), key=lambda x: x[1]['quality_score'])
    
    return jsonify({
        "total_models": len(models),
        "providers": list(providers),
        "cheapest_model": {"id": cheapest[0], **cheapest[1]},
        "fastest_model": {"id": fastest[0], **fastest[1]},
        "best_quality_model": {"id": best_quality[0], **best_quality[1]}
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
