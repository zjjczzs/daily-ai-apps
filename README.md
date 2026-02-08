# MCP Hub - MCP服务器发现与管理平台

一个用于发现、管理和测试MCP (Model Context Protocol) 服务器的Web应用。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![MCP](https://img.shields.io/badge/MCP-Protocol-orange.svg)

## 功能特性

- 🔍 **服务器发现** - 浏览和搜索流行的MCP服务器
- 📊 **服务器管理** - 添加、配置和删除MCP服务器
- 🧪 **在线测试** - 直接在浏览器中测试MCP工具
- 📚 **文档查看** - 查看MCP服务器的详细文档
- 🔌 **连接管理** - 管理SSE和Stdio连接

## 技术栈

- **后端**: Python + Flask
- **前端**: HTML + JavaScript + Tailwind CSS
- **MCP协议**: 支持SSE和Stdio传输
- **数据存储**: JSON文件存储

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python app.py
```

访问 http://localhost:5000

### 使用Docker

```bash
docker build -t mcp-hub .
docker run -p 5000:5000 mcp-hub
```

## 使用指南

### 1. 浏览服务器

打开首页即可看到预置的流行MCP服务器列表，包括：
- Context7 - 代码文档MCP服务器
- GitHub MCP - GitHub操作集成
- Filesystem MCP - 文件系统操作
- PostgreSQL MCP - 数据库查询

### 2. 添加自定义服务器

点击"添加服务器"按钮，输入：
- 服务器名称
- 传输类型 (SSE/Stdio)
- 连接URL或命令
- 描述信息

### 3. 测试工具

点击服务器卡片进入详情页，查看可用工具并直接测试：
- 选择工具
- 填写参数
- 点击执行查看结果

## 项目结构

```
.
├── app.py              # Flask应用主文件
├── mcp_client.py       # MCP客户端实现
├── servers.json        # 服务器配置存储
├── requirements.txt    # Python依赖
├── Dockerfile         # Docker配置
└── templates/         # HTML模板
    ├── base.html
    ├── index.html
    ├── server_detail.html
    └── add_server.html
```

## MCP协议简介

Model Context Protocol (MCP) 是Anthropic推出的开放协议，用于标准化AI模型与外部工具和数据源的连接。

### 核心概念

- **Server**: 提供工具和资源的MCP服务
- **Client**: 连接到Server的客户端
- **Tool**: 可被AI调用的功能
- **Resource**: 可被访问的数据

### 传输方式

- **SSE (Server-Sent Events)**: HTTP长连接，适合远程服务
- **Stdio**: 标准输入输出，适合本地进程

## 热门MCP服务器

| 名称 | 描述 | GitHub Stars |
|------|------|-------------|
| context7 | 代码文档MCP | 44k+ |
| github-mcp | GitHub集成 | 8k+ |
| filesystem | 文件系统操作 | 5k+ |
| postgres | PostgreSQL查询 | 3k+ |
| fetch | Web内容获取 | 2k+ |

## 开发计划

- [ ] 支持更多传输协议
- [ ] MCP工具调用历史
- [ ] 服务器健康检查
- [ ] 批量导入/导出
- [ ] REST API接口

## 贡献

欢迎提交Issue和PR！

## 许可证

MIT License

## 相关链接

- [MCP官方文档](https://modelcontextprotocol.io)
- [MCP GitHub](https://github.com/modelcontextprotocol)
- [Awesome MCP Servers](https://github.com/modelcontextprotocol/servers)

---

**生成日期**: 2026-02-08  
**基于趋势**: MCP (Model Context Protocol) 成为AI工具新标准
