# MCP Hub 🔧

基于 **2026年2月7日最火AI趋势：MCP协议成为新标准** 生成的应用

> 🚀 Model Context Protocol (MCP) 正在成为AI工具连接外部世界的标准接口。本项目是一个MCP服务器发现、安装、管理和测试的一站式工具。

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Trend](https://img.shields.io/badge/AI%20Trend-MCP%20Protocol-orange)

## ✨ 功能特性

- 🔍 **发现** - 浏览流行的MCP服务器（如Context7、GitHub、PostgreSQL等）
- 📦 **安装** - 一键安装预设的MCP服务器到本地配置
- ➕ **添加** - 支持添加自定义MCP服务器配置
- 🧪 **测试** - 验证MCP服务器配置是否正确
- 📤 **导出** - 导出为Claude Desktop兼容的配置格式
- 📥 **导入** - 从Claude Desktop配置导入现有服务器
- 🗑️ **管理** - 删除、查看已配置的服务器

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/zjjczzs/daily-ai-apps.git
cd daily-ai-apps/2026-02-07-mcp-protocol

# 安装
pip install -e .
```

### 基本用法

```bash
# 发现可用的MCP服务器
mcp-hub discover

# 搜索特定类型的服务器
mcp-hub discover --keyword search

# 安装预设服务器（例如 Context7）
mcp-hub install context7

# 列出已安装的服务器
mcp-hub list

# 测试服务器连接
mcp-hub test context7

# 查看服务器详情
mcp-hub show context7

# 导出Claude Desktop配置
mcp-hub export

# 添加自定义服务器
mcp-hub add myserver "python" ["-m", "my_mcp_server"] --description "我的自定义服务器"

# 删除服务器
mcp-hub remove myserver
```

## 📋 预设服务器列表

| 服务器 | 描述 | 来源 |
|--------|------|------|
| **context7** | 📚 为LLM提供最新代码文档 | upstash/context7 |
| **filesystem** | 📁 安全的文件系统访问 | MCP官方 |
| **github** | 🐙 GitHub API 集成 | MCP官方 |
| **postgres** | 🐘 PostgreSQL 数据库访问 | MCP官方 |
| **puppeteer** | 🎭 浏览器自动化和网页抓取 | MCP官方 |
| **brave-search** | 🔍 Brave Search API 集成 | MCP官方 |
| **sqlite** | 🗄️ SQLite 数据库访问 | MCP官方 |

## 🛠️ 技术栈

- **Python 3.8+** - 核心语言
- **JSON** - 配置存储格式
- **argparse** - CLI接口
- **setuptools** - 包管理

## 📁 项目结构

```
mcp-hub/
├── mcp_hub.py      # 核心代码（单文件，约400行）
├── setup.py        # 包安装配置
├── README.md       # 项目说明
└── .gitignore      # Git忽略规则
```

## 🔧 配置存储

配置文件存储在：
- **Linux/macOS**: `~/.config/mcp-hub/mcp-hub.json`
- **Windows**: `%USERPROFILE%\.config\mcp-hub\mcp-hub.json`

## 📝 配置示例

```json
{
  "servers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "env": {},
      "description": "📚 为LLM提供最新代码文档的MCP服务器",
      "source": "https://github.com/upstash/context7"
    }
  }
}
```

## 🎯 为什么创建这个项目？

根据今天（2026年2月7日）的AI趋势分析，**MCP协议正在成为新标准**：

1. **Context7**、**BetterBugs MCP**等MCP服务器快速涌现
2. **Claude Desktop**、**OpenClaw**等客户端开始原生支持MCP
3. 开发者需要一个简单的工具来管理多个MCP服务器配置

MCP Hub解决了这个痛点，让发现、安装、管理MCP服务器变得简单。

## 🤝 与Claude Desktop集成

MCP Hub生成的配置与Claude Desktop完全兼容：

```bash
# 导出配置
mcp-hub export > claude_config.json

# 将内容复制到 Claude Desktop 配置文件中
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
# Windows: %APPDATA%\Claude\claude_desktop_config.json
```

## 📜 许可证

MIT License - 详见 LICENSE 文件

## 🔗 相关链接

- [MCP Protocol Spec](https://modelcontextprotocol.io)
- [Context7 MCP Server](https://github.com/upstash/context7)
- [MCP Official Servers](https://github.com/modelcontextprotocol/servers)

---

> 📅 生成日期: 2026年2月7日
> 
> 🔥 基于趋势: MCP协议成为新标准
