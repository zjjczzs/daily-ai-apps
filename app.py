#!/usr/bin/env python3
"""
MCP Hub - MCP服务器发现与管理平台
Flask Web应用主文件
"""

import json
import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATA_FILE = 'servers.json'

# 确保templates目录存在
os.makedirs('templates', exist_ok=True)


def load_servers():
    """加载服务器列表"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"servers": []}


def save_servers(data):
    """保存服务器列表"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_category_color(category):
    """获取分类颜色"""
    colors = {
        'documentation': 'bg-blue-100 text-blue-800',
        'integration': 'bg-green-100 text-green-800',
        'utility': 'bg-purple-100 text-purple-800',
        'database': 'bg-orange-100 text-orange-800',
        'automation': 'bg-red-100 text-red-800',
        'custom': 'bg-gray-100 text-gray-800'
    }
    return colors.get(category, 'bg-gray-100 text-gray-800')


@app.route('/')
def index():
    """首页 - 服务器列表"""
    data = load_servers()
    servers = data.get('servers', [])
    
    # 搜索过滤
    query = request.args.get('q', '').lower()
    category = request.args.get('category', '')
    
    if query:
        servers = [s for s in servers if query in s['name'].lower() 
                   or query in s['description'].lower()
                   or any(query in tag.lower() for tag in s.get('tags', []))]
    
    if category:
        servers = [s for s in servers if s.get('category') == category]
    
    # 获取所有分类
    categories = list(set(s.get('category', 'other') for s in data.get('servers', [])))
    
    return render_template('index.html', 
                         servers=servers, 
                         categories=categories,
                         query=query,
                         selected_category=category,
                         get_category_color=get_category_color,
                         total_servers=len(data.get('servers', [])))


@app.route('/server/<server_id>')
def server_detail(server_id):
    """服务器详情页"""
    data = load_servers()
    server = next((s for s in data['servers'] if s['id'] == server_id), None)
    
    if not server:
        flash('服务器未找到', 'error')
        return redirect(url_for('index'))
    
    return render_template('server_detail.html', 
                         server=server,
                         get_category_color=get_category_color)


@app.route('/add', methods=['GET', 'POST'])
def add_server():
    """添加服务器页面"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        transport = request.form.get('transport', 'stdio')
        command = request.form.get('command', '').strip()
        url = request.form.get('url', '').strip()
        category = request.form.get('category', 'custom')
        tags = request.form.get('tags', '').split(',')
        tags = [t.strip() for t in tags if t.strip()]
        
        if not name:
            flash('服务器名称不能为空', 'error')
            return render_template('add_server.html')
        
        data = load_servers()
        
        new_server = {
            "id": str(uuid.uuid4())[:8],
            "name": name,
            "description": description,
            "transport": transport,
            "command": command if transport == 'stdio' else None,
            "url": url if transport == 'sse' else None,
            "category": category,
            "tags": tags,
            "stars": 0,
            "github_url": "",
            "tools": [],
            "added_at": datetime.now().isoformat()
        }
        
        data['servers'].append(new_server)
        save_servers(data)
        
        flash('服务器添加成功！', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_server.html')


@app.route('/api/servers', methods=['GET'])
def api_servers():
    """API: 获取所有服务器"""
    data = load_servers()
    return jsonify(data['servers'])


@app.route('/api/servers/<server_id>', methods=['GET'])
def api_server_detail(server_id):
    """API: 获取单个服务器详情"""
    data = load_servers()
    server = next((s for s in data['servers'] if s['id'] == server_id), None)
    
    if not server:
        return jsonify({"error": "Server not found"}), 404
    
    return jsonify(server)


@app.route('/api/servers/<server_id>', methods=['DELETE'])
def api_delete_server(server_id):
    """API: 删除服务器"""
    data = load_servers()
    data['servers'] = [s for s in data['servers'] if s['id'] != server_id]
    save_servers(data)
    
    return jsonify({"success": True})


@app.route('/api/test/<server_id>', methods=['POST'])
def api_test_tool(server_id):
    """API: 测试工具调用"""
    data = load_servers()
    server = next((s for s in data['servers'] if s['id'] == server_id), None)
    
    if not server:
        return jsonify({"error": "Server not found"}), 404
    
    tool_name = request.json.get('tool')
    params = request.json.get('params', {})
    
    # 模拟工具调用结果
    result = {
        "status": "simulated",
        "message": f"工具 '{tool_name}' 调用模拟成功",
        "params": params,
        "server": server['name'],
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(result)


@app.route('/api/categories', methods=['GET'])
def api_categories():
    """API: 获取所有分类"""
    data = load_servers()
    categories = list(set(s.get('category', 'other') for s in data.get('servers', [])))
    return jsonify(categories)


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """API: 获取统计信息"""
    data = load_servers()
    servers = data.get('servers', [])
    
    stats = {
        "total_servers": len(servers),
        "total_tools": sum(len(s.get('tools', [])) for s in servers),
        "categories": len(set(s.get('category') for s in servers)),
        "stdio_servers": len([s for s in servers if s.get('transport') == 'stdio']),
        "sse_servers": len([s for s in servers if s.get('transport') == 'sse']),
        "total_stars": sum(s.get('stars', 0) for s in servers)
    }
    
    return jsonify(stats)


if __name__ == '__main__':
    # 初始化数据文件
    if not os.path.exists(DATA_FILE):
        save_servers({"servers": []})
    
    print("=" * 50)
    print("🚀 MCP Hub 已启动!")
    print("=" * 50)
    print("访问地址: http://localhost:5000")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
