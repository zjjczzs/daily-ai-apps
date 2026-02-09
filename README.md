# MCP Client CLI - AI时代的HTTP客户端

一个轻量级、交互式的Model Context Protocol (MCP)客户端工具，让你可以轻松连接、探索和管理MCP服务器。

## 🚀 功能特性

- 🔌 **多服务器管理** - 同时连接多个MCP服务器
- 🛠️ **工具发现** - 自动列出服务器提供的所有工具
- 💬 **交互式对话** - 与AI Agent自然语言交互
- 📊 **执行追踪** - 实时查看工具调用和执行结果
- ⚙️ **配置管理** - YAML配置文件，易于维护

## 📦 技术栈

- Python 3.10+
- `mcp` - Model Context Protocol官方SDK
- `asyncio` - 异步IO处理
- `rich` - 漂亮的终端UI
- `typer` - CLI框架
- `pydantic` - 数据验证

## 🛠️ 安装

```bash
# 克隆仓库
git clone https://github.com/zjjczzs/daily-ai-apps.git
cd daily-ai-apps/2026-02-09-mcp-client-cli

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 🎯 快速开始

### 1. 配置MCP服务器

编辑 `config.yaml`：

```yaml
servers:
  filesystem:
    command: npx
    args:
      - "-y"
      - "@modelcontextprotocol/server-filesystem"
      - "/path/to/your/files"
  
  fetch:
    command: uvx
    args:
      - "mcp-server-fetch"
  
  sqlite:
    command: uvx
    args:
      - "mcp-server-sqlite"
      - "--db-path"
      - "data.db"
```

### 2. 运行客户端

```bash
# 启动交互式CLI
python mcp_client.py

# 或带配置启动
python mcp_client.py --config config.yaml
```

### 3. 使用命令

```
mcp-cli> /connect          # 连接所有配置的服务器
mcp-cli> /list             # 列出所有可用工具
mcp-cli> /call <工具名>    # 调用指定工具
mcp-cli> /chat             # 进入对话模式
mcp-cli> /quit             # 退出
```

## 📝 使用示例

### 文件系统操作
```
mcp-cli> /connect
✓ Connected to filesystem server
✓ Connected to fetch server

mcp-cli> /list
📦 Available Tools:
  • filesystem-read_file
  • filesystem-write_file
  • filesystem-list_directory
  • fetch-fetch_url

mcp-cli> /call filesystem-list_directory path="/home/user/docs"
📁 Documents:
  - report.pdf
  - notes.txt
  - project/
```

### AI对话模式
```
mcp-cli> /chat
🤖 AI Agent: 你好！我可以帮你使用各种工具。需要做什么？

You: 读取我的todo.txt文件
🤖 AI Agent: 我来帮你读取...
[调用 filesystem-read_file]
✓ 结果：
- 完成MCP客户端
- 学习Rust
- 买牛奶
```

## 🔧 配置说明

### config.yaml 完整示例

```yaml
# MCP服务器配置
servers:
  # 文件系统服务器
  filesystem:
    command: npx
    args:
      - "-y"
      - "@modelcontextprotocol/server-filesystem"
      - "/home/user"
    env:
      NODE_ENV: production
  
  # Web获取服务器
  fetch:
    command: uvx
    args:
      - "mcp-server-fetch"
  
  # SQLite数据库服务器
  sqlite:
    command: uvx
    args:
      - "mcp-server-sqlite"
      - "--db-path"
      - "./data.db"
  
  # Git服务器
  git:
    command: uvx
    args:
      - "mcp-server-git"
      - "--repository"
      - "/path/to/repo"

# 客户端设置
settings:
  timeout: 30
  max_tools: 100
  log_level: INFO
```

## 🏗️ 架构

```
┌─────────────────────────────────────────┐
│           MCP Client CLI                │
├─────────────────────────────────────────┤
│  CLI Interface (Typer + Rich)           │
├─────────────────────────────────────────┤
│  MCP Client Manager                     │
│  • Server Connection                    │
│  • Tool Discovery                       │
│  • Request Routing                      │
├─────────────────────────────────────────┤
│  MCP Protocol Layer                     │
│  • JSON-RPC                             │
│  • stdio/sse transport                  │
├─────────────────────────────────────────┤
│  MCP Servers (External)                 │
│  • filesystem, fetch, sqlite, git...    │
└─────────────────────────────────────────┘
```

## 🤝 常用MCP服务器

| 服务器 | 安装命令 | 功能 |
|--------|----------|------|
| filesystem | `npx @modelcontextprotocol/server-filesystem` | 文件读写 |
| fetch | `uvx mcp-server-fetch` | HTTP请求 |
| sqlite | `uvx mcp-server-sqlite` | SQLite数据库 |
| git | `uvx mcp-server-git` | Git操作 |
| postgres | `npx @modelcontextprotocol/server-postgres` | PostgreSQL |
| slack | `npx @modelcontextprotocol/server-slack` | Slack集成 |

## 📚 相关资源

- [MCP官方文档](https://modelcontextprotocol.io/)
- [MCP服务器列表](https://github.com/modelcontextprotocol/servers)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## 📝 今日AI趋势

> **MCP协议将成为AI时代的HTTP** - 2026年2月9日
> 
> Model Context Protocol (MCP) 是Anthropic推出的开放协议，用于标准化AI模型与外部数据源、工具的连接。就像HTTP统一了互联网，MCP正在统一AI与世界的接口。

## 📄 License

MIT License - 详见 LICENSE 文件

---

Built with ❤️ by AI Agent | 2026-02-09
