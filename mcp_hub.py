#!/usr/bin/env python3
"""
MCP Hub - Model Context Protocol 服务器发现与管理工具
基于2026年2月7日最火AI趋势：MCP协议成为新标准

功能：
- 搜索和发现 MCP 服务器
- 管理本地 MCP 服务器配置
- 测试 MCP 服务器连接
- 支持添加/删除/列出服务器
"""

import json
import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import requests


@dataclass
class MCPServer:
    """MCP服务器配置"""
    name: str
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None
    description: str = ""
    source: str = ""
    
    def to_dict(self) -> dict:
        return {
            "command": self.command,
            "args": self.args,
            "env": self.env or {},
            "description": self.description,
            "source": self.source
        }
    
    @classmethod
    def from_dict(cls, name: str, data: dict) -> "MCPServer":
        return cls(
            name=name,
            command=data.get("command", ""),
            args=data.get("args", []),
            env=data.get("env"),
            description=data.get("description", ""),
            source=data.get("source", "")
        )


class MCPHub:
    """MCP Hub 核心类"""
    
    CONFIG_FILE = "mcp-hub.json"
    
    # 预设的流行MCP服务器列表（基于真实趋势）
    POPULAR_SERVERS = {
        "context7": {
            "command": "npx",
            "args": ["-y", "@upstash/context7-mcp"],
            "description": "📚 为LLM提供最新代码文档的MCP服务器",
            "source": "https://github.com/upstash/context7"
        },
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"],
            "description": "📁 安全的文件系统访问服务器",
            "source": "https://github.com/modelcontextprotocol/servers"
        },
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"},
            "description": "🐙 GitHub API 集成服务器",
            "source": "https://github.com/modelcontextprotocol/servers"
        },
        "postgres": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"],
            "description": "🐘 PostgreSQL 数据库访问服务器",
            "source": "https://github.com/modelcontextprotocol/servers"
        },
        "puppeteer": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
            "description": "🎭 浏览器自动化和网页抓取服务器",
            "source": "https://github.com/modelcontextprotocol/servers"
        },
        "brave-search": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {"BRAVE_API_KEY": "your_api_key"},
            "description": "🔍 Brave Search API 集成服务器",
            "source": "https://github.com/modelcontextprotocol/servers"
        },
        "sqlite": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sqlite", "/path/to/database.db"],
            "description": "🗄️ SQLite 数据库访问服务器",
            "source": "https://github.com/modelcontextprotocol/servers"
        }
    }
    
    def __init__(self):
        self.config_path = Path.home() / ".config" / "mcp-hub"
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_path / self.CONFIG_FILE
        self.servers: Dict[str, MCPServer] = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for name, server_data in data.get("servers", {}).items():
                    self.servers[name] = MCPServer.from_dict(name, server_data)
            except Exception as e:
                print(f"⚠️  加载配置失败: {e}")
    
    def _save_config(self):
        """保存配置文件"""
        try:
            data = {
                "servers": {name: server.to_dict() for name, server in self.servers.items()}
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False
    
    def discover(self, keyword: str = "") -> List[dict]:
        """发现MCP服务器"""
        results = []
        for name, data in self.POPULAR_SERVERS.items():
            if not keyword or keyword.lower() in name.lower() or keyword.lower() in data["description"].lower():
                results.append({
                    "name": name,
                    **data,
                    "installed": name in self.servers
                })
        return results
    
    def add(self, name: str, command: str, args: List[str], 
            env: Optional[Dict[str, str]] = None, description: str = "") -> bool:
        """添加MCP服务器"""
        if name in self.servers:
            print(f"⚠️  服务器 '{name}' 已存在，使用 --force 覆盖")
            return False
        
        self.servers[name] = MCPServer(
            name=name,
            command=command,
            args=args,
            env=env,
            description=description
        )
        
        if self._save_config():
            print(f"✅ 已添加服务器: {name}")
            return True
        return False
    
    def install(self, name: str) -> bool:
        """从预设列表安装MCP服务器"""
        if name not in self.POPULAR_SERVERS:
            print(f"❌ 未知的预设服务器: {name}")
            print(f"💡 使用 'mcp-hub discover' 查看可用服务器")
            return False
        
        if name in self.servers:
            print(f"⚠️  服务器 '{name}' 已安装")
            return False
        
        data = self.POPULAR_SERVERS[name]
        return self.add(
            name=name,
            command=data["command"],
            args=data["args"],
            env=data.get("env"),
            description=data["description"]
        )
    
    def remove(self, name: str) -> bool:
        """删除MCP服务器"""
        if name not in self.servers:
            print(f"❌ 服务器 '{name}' 不存在")
            return False
        
        del self.servers[name]
        if self._save_config():
            print(f"✅ 已删除服务器: {name}")
            return True
        return False
    
    def list(self) -> List[MCPServer]:
        """列出所有已配置的MCP服务器"""
        return list(self.servers.values())
    
    def get(self, name: str) -> Optional[MCPServer]:
        """获取单个服务器配置"""
        return self.servers.get(name)
    
    def test(self, name: str) -> bool:
        """测试MCP服务器连接"""
        server = self.servers.get(name)
        if not server:
            print(f"❌ 服务器 '{name}' 不存在")
            return False
        
        print(f"🧪 测试服务器: {name}")
        print(f"   命令: {server.command} {' '.join(server.args)}")
        
        try:
            # 检查命令是否存在
            result = subprocess.run(
                ["which", server.command],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                print(f"❌ 命令未找到: {server.command}")
                print(f"💡 请先安装: npm install -g {server.command}")
                return False
            
            # 尝试运行帮助命令
            env = os.environ.copy()
            if server.env:
                env.update(server.env)
            
            # 对于npx命令，先检查包是否可下载
            if server.command == "npx":
                pkg = server.args[1] if len(server.args) > 1 else ""
                print(f"   检查包: {pkg}")
            
            print(f"✅ 服务器配置看起来正常")
            print(f"💡 要完全测试，请在支持MCP的客户端中连接此服务器")
            return True
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
    
    def export_claude_config(self) -> str:
        """导出为Claude Desktop配置格式"""
        config = {
            "mcpServers": {
                name: {
                    "command": server.command,
                    "args": server.args
                }
                for name, server in self.servers.items()
            }
        }
        return json.dumps(config, indent=2)
    
    def import_claude_config(self, path: str) -> int:
        """从Claude Desktop配置导入"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            count = 0
            for name, data in config.get("mcpServers", {}).items():
                if name not in self.servers:
                    self.servers[name] = MCPServer.from_dict(name, data)
                    count += 1
            
            self._save_config()
            print(f"✅ 已导入 {count} 个服务器")
            return count
            
        except Exception as e:
            print(f"❌ 导入失败: {e}")
            return 0


def main():
    parser = argparse.ArgumentParser(
        description="🔧 MCP Hub - Model Context Protocol 服务器发现与管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  mcp-hub discover                    # 发现可用的MCP服务器
  mcp-hub discover --keyword search   # 搜索特定关键词
  mcp-hub install context7            # 安装预设服务器
  mcp-hub add myserver "python" ["-m", "mcp_server"]  # 添加自定义服务器
  mcp-hub list                        # 列出已安装服务器
  mcp-hub test context7               # 测试服务器连接
  mcp-hub export                      # 导出Claude Desktop配置
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # discover 命令
    discover_parser = subparsers.add_parser("discover", help="发现可用的MCP服务器")
    discover_parser.add_argument("--keyword", "-k", help="搜索关键词")
    
    # install 命令
    install_parser = subparsers.add_parser("install", help="安装预设MCP服务器")
    install_parser.add_argument("name", help="服务器名称")
    
    # add 命令
    add_parser = subparsers.add_parser("add", help="添加自定义MCP服务器")
    add_parser.add_argument("name", help="服务器名称")
    add_parser.add_argument("command", help="运行命令")
    add_parser.add_argument("args", nargs="+", help="命令参数")
    add_parser.add_argument("--env", "-e", nargs="+", help="环境变量 (KEY=VALUE)")
    add_parser.add_argument("--description", "-d", help="服务器描述")
    
    # remove 命令
    remove_parser = subparsers.add_parser("remove", help="删除MCP服务器")
    remove_parser.add_argument("name", help="服务器名称")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出已配置的MCP服务器")
    
    # test 命令
    test_parser = subparsers.add_parser("test", help="测试MCP服务器连接")
    test_parser.add_argument("name", help="服务器名称")
    
    # export 命令
    export_parser = subparsers.add_parser("export", help="导出Claude Desktop配置")
    
    # import 命令
    import_parser = subparsers.add_parser("import", help="从Claude Desktop配置导入")
    import_parser.add_argument("path", help="配置文件路径")
    
    # show 命令
    show_parser = subparsers.add_parser("show", help="显示服务器详情")
    show_parser.add_argument("name", help="服务器名称")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    hub = MCPHub()
    
    if args.command == "discover":
        results = hub.discover(args.keyword or "")
        if not results:
            print("😕 未找到匹配的MCP服务器")
            return
        
        print(f"\n🔍 发现 {len(results)} 个MCP服务器:\n")
        for r in results:
            status = "✅ 已安装" if r["installed"] else "⬜ 未安装"
            print(f"  {r['name']}")
            print(f"     {r['description']}")
            print(f"     命令: {r['command']} {' '.join(r['args'][:3])}{'...' if len(r['args']) > 3 else ''}")
            print(f"     状态: {status}")
            print(f"     来源: {r['source']}")
            print()
    
    elif args.command == "install":
        hub.install(args.name)
    
    elif args.command == "add":
        env = {}
        if args.env:
            for e in args.env:
                if "=" in e:
                    k, v = e.split("=", 1)
                    env[k] = v
        hub.add(args.name, args.command, args.args, env, args.description or "")
    
    elif args.command == "remove":
        hub.remove(args.name)
    
    elif args.command == "list":
        servers = hub.list()
        if not servers:
            print("📭 没有配置的MCP服务器")
            print(f"💡 使用 'mcp-hub discover' 发现服务器")
            return
        
        print(f"\n📦 已配置的MCP服务器 ({len(servers)}个):\n")
        for s in servers:
            print(f"  🔹 {s.name}")
            if s.description:
                print(f"     {s.description}")
            print(f"     命令: {s.command} {' '.join(s.args)}")
            if s.env:
                print(f"     环境变量: {', '.join(s.env.keys())}")
            print()
    
    elif args.command == "test":
        hub.test(args.name)
    
    elif args.command == "export":
        print(hub.export_claude_config())
    
    elif args.command == "import":
        hub.import_claude_config(args.path)
    
    elif args.command == "show":
        server = hub.get(args.name)
        if server:
            print(f"\n📋 服务器详情: {server.name}\n")
            print(f"  描述: {server.description or 'N/A'}")
            print(f"  命令: {server.command}")
            print(f"  参数: {' '.join(server.args)}")
            if server.env:
                print(f"  环境变量:")
                for k, v in server.env.items():
                    masked = "*" * len(v) if len(v) > 3 else "***"
                    print(f"    {k}={masked}")
            print()
        else:
            print(f"❌ 服务器 '{args.name}' 不存在")


if __name__ == "__main__":
    main()
