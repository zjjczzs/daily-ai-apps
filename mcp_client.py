#!/usr/bin/env python3
"""
MCP Client CLI - AI时代的HTTP客户端
一个轻量级、交互式的Model Context Protocol客户端工具

Author: AI Agent
Date: 2026-02-09
"""

import asyncio
import json
import sys
from typing import Any, Optional
from contextlib import AsyncExitStack
from pathlib import Path

import yaml
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box
from pydantic import BaseModel, Field

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("请先安装mcp包: pip install mcp>=1.0.0")
    sys.exit(1)


console = Console()
app = typer.Typer(help="MCP Client CLI - 连接AI与世界的桥梁")


class ServerConfig(BaseModel):
    """MCP服务器配置"""
    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)


class Config(BaseModel):
    """应用配置"""
    servers: dict[str, ServerConfig] = Field(default_factory=dict)
    settings: dict[str, Any] = Field(default_factory=dict)


class MCPServer:
    """MCP服务器连接封装"""
    
    def __init__(self, name: str, config: ServerConfig):
        self.name = name
        self.config = config
        self.session: Optional[ClientSession] = None
        self._client = None
        self._exit_stack = AsyncExitStack()
        self.tools: list[dict] = []
    
    async def connect(self):
        """连接到MCP服务器"""
        server_params = StdioServerParameters(
            command=self.config.command,
            args=self.config.args,
            env=self.config.env if self.config.env else None
        )
        
        self._client = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        
        read, write = self._client
        self.session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        
        await self.session.initialize()
        
        # 获取工具列表
        tools_result = await self.session.list_tools()
        self.tools = [
            {
                "name": tool.name,
                "description": tool.description or "无描述",
                "server": self.name
            }
            for tool in tools_result.tools
        ]
    
    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """调用工具"""
        if not self.session:
            raise RuntimeError(f"服务器 {self.name} 未连接")
        
        result = await self.session.call_tool(tool_name, arguments)
        return result
    
    async def disconnect(self):
        """断开连接"""
        await self._exit_stack.aclose()
        self.session = None
        self._client = None


class MCPClientManager:
    """MCP客户端管理器"""
    
    def __init__(self):
        self.servers: dict[str, MCPServer] = {}
        self.all_tools: list[dict] = []
    
    async def add_server(self, name: str, config: ServerConfig):
        """添加并连接服务器"""
        server = MCPServer(name, config)
        await server.connect()
        self.servers[name] = server
        self.all_tools.extend(server.tools)
        return server
    
    async def connect_all(self, config: Config):
        """连接所有配置的服务器"""
        with console.status("[bold green]正在连接MCP服务器..."):
            for name, server_config in config.servers.items():
                try:
                    await self.add_server(name, server_config)
                    console.print(f"✓ [green]已连接:[/green] {name}")
                except Exception as e:
                    console.print(f"✗ [red]连接失败:[/red] {name} - {e}")
    
    def get_tool(self, tool_name: str) -> Optional[tuple[MCPServer, dict]]:
        """查找工具所属服务器"""
        for tool in self.all_tools:
            if tool["name"] == tool_name:
                server = self.servers.get(tool["server"])
                return server, tool
        return None, None
    
    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """调用指定工具"""
        server, tool = self.get_tool(tool_name)
        if not server:
            raise ValueError(f"未找到工具: {tool_name}")
        
        return await server.call_tool(tool_name, arguments)
    
    async def disconnect_all(self):
        """断开所有服务器"""
        for server in self.servers.values():
            await server.disconnect()
        self.servers.clear()
        self.all_tools.clear()


class InteractiveCLI:
    """交互式命令行界面"""
    
    def __init__(self, manager: MCPClientManager):
        self.manager = manager
        self.running = True
    
    def print_help(self):
        """打印帮助信息"""
        help_text = """
[bold cyan]MCP Client CLI 命令[/bold cyan]

[green]/connect[/green]          - 连接所有配置的服务器
[green]/list[/green]             - 列出所有可用工具
[green]/call <工具名> <参数>[/green] - 调用指定工具
[green]/servers[/green]          - 显示已连接的服务器
[green]/chat[/green]             - 进入AI对话模式
[green]/clear[/green]            - 清屏
[green]/help[/green]             - 显示帮助
[green]/quit[/green]             - 退出程序

[dim]示例:[/dim]
  /call filesystem-read_file path="test.txt"
  /call fetch-fetch_url url="https://api.github.com"
        """
        console.print(Panel(help_text, title="帮助", border_style="blue"))
    
    def list_tools(self):
        """列出所有工具"""
        if not self.manager.all_tools:
            console.print("[yellow]暂无可用工具，请先连接服务器[/yellow]")
            return
        
        table = Table(title="📦 可用工具列表", box=box.ROUNDED)
        table.add_column("工具名称", style="cyan", no_wrap=True)
        table.add_column("所属服务器", style="green")
        table.add_column("描述", style="white")
        
        for tool in self.manager.all_tools:
            table.add_row(
                tool["name"],
                tool["server"],
                tool["description"][:50] + "..." if len(tool["description"]) > 50 else tool["description"]
            )
        
        console.print(table)
    
    def list_servers(self):
        """列出已连接的服务器"""
        if not self.manager.servers:
            console.print("[yellow]暂无连接的服务器[/yellow]")
            return
        
        table = Table(title="🔌 已连接服务器", box=box.ROUNDED)
        table.add_column("服务器", style="cyan")
        table.add_column("工具数量", style="green")
        table.add_column("命令", style="dim")
        
        for name, server in self.manager.servers.items():
            table.add_row(
                name,
                str(len(server.tools)),
                f"{server.config.command} {' '.join(server.config.args[:2])}..."
            )
        
        console.print(table)
    
    async def call_tool(self, args: list[str]):
        """调用工具"""
        if not args:
            console.print("[red]用法:[/red] /call <工具名> key=value key2=value2")
            return
        
        tool_name = args[0]
        
        # 解析参数
        arguments = {}
        for arg in args[1:]:
            if "=" in arg:
                key, value = arg.split("=", 1)
                # 尝试解析为JSON
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass  # 保持字符串
                arguments[key] = value
        
        try:
            with console.status(f"[bold green]正在调用 {tool_name}..."):
                result = await self.manager.call_tool(tool_name, arguments)
            
            console.print(f"[bold green]✓ 调用成功:[/bold green] {tool_name}")
            
            # 显示结果
            if result.content:
                for content in result.content:
                    if content.type == "text":
                        console.print(Panel(
                            content.text,
                            title="执行结果",
                            border_style="green"
                        ))
            
            if result.isError:
                console.print("[red]执行出现错误[/red]")
                
        except Exception as e:
            console.print(f"[red]调用失败:[/red] {e}")
    
    async def chat_mode(self):
        """AI对话模式"""
        console.print(Panel(
            "[bold cyan]🤖 AI Agent 对话模式[/bold cyan]\n"
            "输入你的问题，AI会使用可用工具帮你完成。\n"
            "输入 [bold]/exit[/bold] 退出对话模式",
            border_style="cyan"
        ))
        
        # 简化的模拟对话
        while True:
            try:
                user_input = console.input("[bold green]你:[/bold green] ").strip()
                
                if user_input.lower() in ["/exit", "quit", "exit"]:
                    break
                
                if not user_input:
                    continue
                
                # 模拟AI响应（实际应该调用LLM）
                console.print("[bold cyan]🤖 AI Agent:[/bold cyan] 我理解你的需求了。让我帮你处理...")
                console.print("[dim]💡 提示: 这是演示版本，完整版本需要集成LLM来解析意图并调用工具[/dim]")
                console.print("[dim]    你可以直接使用 /call 命令调用工具[/dim]")
                
            except KeyboardInterrupt:
                break
        
        console.print("[cyan]已退出对话模式[/cyan]")
    
    async def run(self, config: Config):
        """运行交互式CLI"""
        console.print(Panel.fit(
            "[bold cyan]MCP Client CLI[/bold cyan]\n"
            "[dim]AI时代的HTTP客户端 | Model Context Protocol[/dim]\n"
            "输入 /help 查看命令",
            border_style="cyan"
        ))
        
        while self.running:
            try:
                user_input = console.input("[bold blue]mcp-cli>[/bold blue] ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split()
                cmd = parts[0].lower()
                args = parts[1:]
                
                if cmd in ["/quit", "quit", "exit", "/exit"]:
                    self.running = False
                
                elif cmd == "/help":
                    self.print_help()
                
                elif cmd == "/connect":
                    await self.manager.connect_all(config)
                
                elif cmd == "/list":
                    self.list_tools()
                
                elif cmd == "/servers":
                    self.list_servers()
                
                elif cmd == "/call":
                    await self.call_tool(args)
                
                elif cmd == "/chat":
                    await self.chat_mode()
                
                elif cmd == "/clear":
                    console.clear()
                
                else:
                    console.print(f"[red]未知命令:[/red] {cmd}，输入 /help 查看帮助")
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]使用 /quit 退出程序[/yellow]")
            except EOFError:
                self.running = False


def load_config(config_path: str) -> Config:
    """加载配置文件"""
    path = Path(config_path)
    if not path.exists():
        # 创建默认配置
        default_config = Config(
            servers={
                "fetch": ServerConfig(
                    command="uvx",
                    args=["mcp-server-fetch"]
                )
            }
        )
        # 保存默认配置
        with open(path, "w") as f:
            yaml.dump(default_config.model_dump(), f, default_flow_style=False)
        console.print(f"[yellow]已创建默认配置:[/yellow] {config_path}")
        return default_config
    
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    
    return Config(**data)


@app.command()
def main(
    config: str = typer.Option("config.yaml", "--config", "-c", help="配置文件路径"),
    server: Optional[str] = typer.Option(None, "--server", "-s", help="快速连接单个服务器命令"),
):
    """启动MCP Client CLI"""
    
    async def async_main():
        manager = MCPClientManager()
        
        try:
            if server:
                # 快速模式：直接连接单个服务器
                parts = server.split()
                if len(parts) < 1:
                    console.print("[red]错误: 请提供服务器命令[/red]")
                    return
                
                quick_config = ServerConfig(
                    command=parts[0],
                    args=parts[1:] if len(parts) > 1 else []
                )
                await manager.add_server("quick", quick_config)
                console.print("[green]✓ 已连接到快速服务器[/green]")
            else:
                # 加载配置
                cfg = load_config(config)
                await manager.connect_all(cfg)
            
            # 启动交互式CLI
            cli = InteractiveCLI(manager)
            await cli.run(load_config(config) if not server else Config())
            
        finally:
            await manager.disconnect_all()
            console.print("[dim]已断开所有连接[/dim]")
    
    asyncio.run(async_main())


@app.command()
def version():
    """显示版本信息"""
    console.print("[bold cyan]MCP Client CLI[/bold cyan] v1.0.0")
    console.print("[dim]构建日期: 2026-02-09[/dim]")
    console.print("[dim]基于 Model Context Protocol[/dim]")


if __name__ == "__main__":
    app()
