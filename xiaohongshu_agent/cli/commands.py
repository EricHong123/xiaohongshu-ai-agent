"""
命令行命令
"""
import os
import sys
import typer
from typing import Optional
from rich.console import Console
from rich.theme import Theme

# 自定义主题
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
})
console = Console(theme=custom_theme)

app = typer.Typer(help="小红书 AI Agent CLI")


def print_banner():
    """打印横幅"""
    banner = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   █████╗ ██╗     ██████╗  ██████╗ ██████╗ ██╗   ██╗██╗     ███████╗   ║
║  ██╔══██╗██║     ██╔═══██╗██╔═══██╗██╔══██╗╚██╗ ██╔╝██║     ██╔════╝   ║
║  ███████║██║     ██║   ██║██║   ██║██████╔╝ ╚████╔╝ ██║     █████╗     ║
║  ██╔══██║██║     ██║   ██║██║   ██║██╔══██╗  ╚██╔╝  ██║     ██╔══╝     ║
║  ██║  ██║███████╗╚██████╔╝╚██████╔╝██║  ██║   ██║   ███████╗███████╗   ║
║  ╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚══════╝   ║
║                                                                           ║
║                    🤖 AI Agent v1.1.0                                    ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="magenta bold")


@app.command()
def main(
    keyword: Optional[str] = typer.Option(None, "-k", "--keyword", help="搜索关键词"),
    search: bool = typer.Option(False, "--search", help="搜索模式"),
    stats: bool = typer.Option(False, "--stats", help="查看统计"),
    chat: bool = typer.Option(False, "--chat", help="对话模式"),
    config: bool = typer.Option(False, "--config", help="显示配置"),
    gui: bool = typer.Option(False, "--gui", help="交互式界面"),
):
    """小红书 AI Agent"""
    print_banner()

    # 延迟导入
    from xiaohongshu_agent import XiaohongshuAgent
    from xiaohongshu_agent.config import load_config

    # 加载配置
    cfg = load_config()
    api_key = cfg.get_api_key()
    model = cfg.get_model()
    provider = cfg.get("llm_provider", "openai")
    mcp_url = cfg.get("mcp_url", "http://localhost:18060/mcp")

    # 设置环境变量
    if api_key:
        os.environ[f"{provider.upper()}_API_KEY"] = api_key

    # 初始化 Agent
    console.print("\n[cyan]初始化 Agent...[/cyan]")
    agent = XiaohongshuAgent(
        provider=provider,
        model=model,
        api_key=api_key,
        mcp_url=mcp_url,
    )

    # 执行命令
    if config:
        show_config(agent, cfg)
    elif search or keyword:
        do_search(agent, keyword or "AI Agent")
    elif stats:
        do_stats(agent)
    elif chat:
        do_chat(agent)
    else:
        do_gui(agent)


def show_config(agent, cfg):
    """显示配置"""
    from xiaohongshu_agent.providers import PROVIDERS

    provider = cfg.get("llm_provider", "openai")
    providers = PROVIDERS
    provider_info = providers.get(provider, {})

    console.print("\n[bold cyan]⚙️ 当前配置[/bold cyan]")
    console.print(f"  🤖 LLM: [yellow]{provider}[/yellow] / [green]{cfg.get_model()}[/green]")
    console.print(f"  🔗 MCP: [blue]{cfg.get('mcp_url')}[/blue]")

    api_key = cfg.get_api_key()
    if api_key:
        console.print(f"  🔑 API: [green]{api_key[:8]}...{api_key[-4:]}[/green]")
    else:
        console.print(f"  🔑 API: [red]未设置[/red]")

    mem = agent.get_memory_status()
    console.print(f"  🧠 记忆: [cyan]{mem['count']}/{mem['limit']}[/cyan] 条")


def do_search(agent, keyword):
    """搜索"""
    console.print(f"\n[cyan]搜索: {keyword}[/cyan]")
    posts = agent.search(keyword)

    if posts:
        console.print(f"\n[green]找到 {len(posts)} 条结果:[/green]\n")
        for i, p in enumerate(posts[:10], 1):
            console.print(f"  {i}. [yellow]{p.get('title', '')[:40]}[/yellow]")
            console.print(f"      👍 {p.get('likes', 0):,}  💬 {p.get('comments', 0):,}  ⭐ {p.get('collects', 0):,}\n")
    else:
        console.print("[yellow]未找到结果[/yellow]")


def do_stats(agent):
    """统计"""
    stats = agent.get_stats()

    console.print("\n[bold cyan]📊 数据统计[/bold cyan]")
    console.print(f"  📝 已发布: [green]{stats['published_posts']}[/green] 篇")
    console.print(f"  👍 总点赞: [red]{stats['total_likes']}[/red]")
    console.print(f"  💬 总评论: [blue]{stats['total_comments']}[/blue]")
    console.print(f"  ⭐ 已回复: [yellow]{stats['replied_comments']}[/yellow]")


def do_chat(agent):
    """对话"""
    console.print("\n[bold magenta]🤖 AI 对话模式[/bold magenta]")
    console.print("  输入内容让 AI 帮你处理")
    console.print("  输入 'exit' 或 'q' 退出\n")

    while True:
        try:
            user_input = input("[green]你[/green] > ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'q', 'quit']:
                break

            response = agent.chat(user_input)
            console.print(f"\n[magenta]🤖 AI[/magenta]: {response}\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]错误: {e}[/red]")


def do_gui(agent):
    """GUI 模式"""
    console.print("[yellow]GUI 模式开发中，请使用命令行模式[/yellow]")
    do_chat(agent)


if __name__ == "__main__":
    app()
