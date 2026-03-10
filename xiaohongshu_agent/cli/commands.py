"""
命令行命令 - 增强版
支持键盘上下选择
"""
import os
import sys
import typer
from typing import Optional
from rich.console import Console
from rich.theme import Theme

# 尝试导入 prompt_toolkit 用于交互式选择
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.keys import Keys
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.styles import Style
    from prompt_toolkit.shortcuts import radiolist_dialog, message_dialog, input_dialog
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

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


def select_option(title: str, options: list) -> Optional[int]:
    """
    使用键盘上下选择 - 增强版
    返回选择的索引，从 0 开始
    """
    if not options:
        return None

    if not PROMPT_TOOLKIT_AVAILABLE:
        # 回退到数字选择
        return select_option_fallback(title, options)

    try:
        # 使用 radiolist_dialog
        values = [(i, opt) for i, opt in enumerate(options)]
        result = radiolist_dialog(
            title=title,
            text="使用 ↑↓ 键选择，Enter 确认:",
            values=values,
        ).run()
        return result
    except Exception:
        return select_option_fallback(title, options)


def select_option_fallback(title: str, options: list) -> Optional[int]:
    """
    数字选择回退方案
    """
    console.print(f"\n[bold cyan]{title}[/bold cyan]\n")

    for i, opt in enumerate(options):
        console.print(f"  [yellow]{i + 1}.[/yellow] {opt}")

    while True:
        try:
            choice = console.input("\n[green]请选择 > [/green]")
            if not choice:
                continue
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return idx
        except ValueError:
            pass
        console.print("[red]无效选择，请重试[/red]")


def confirm_dialog(title: str, text: str) -> bool:
    """
    确认对话框
    """
    if not PROMPT_TOOLKIT_AVAILABLE:
        return confirm_fallback(title, text)

    try:
        return message_dialog(
            title=title,
            text=text,
            ok_text="确认",
            cancel_text="取消",
        ).run()
    except Exception:
        return confirm_fallback(title, text)


def confirm_fallback(title: str, text: str) -> bool:
    """确认回退"""
    console.print(f"\n[bold]{title}[/bold]")
    console.print(f"{text}")
    while True:
        result = console.input("\n[yellow]确认 (y/n) > [/yellow]").strip().lower()
        if result in ['y', 'yes', '是', '1']:
            return True
        if result in ['n', 'no', '否', '0']:
            return False


def input_text(title: str, default: str = "") -> str:
    """
    输入文本
    """
    if not PROMPT_TOOLKIT_AVAILABLE:
        return input_fallback(title, default)

    try:
        result = input_dialog(
            title=title,
            text="输入内容:",
            default=default,
        ).run()
        return result or default
    except Exception:
        return input_fallback(title, default)


def input_fallback(title: str, default: str = "") -> str:
    """输入回退"""
    if default:
        result = console.input(f"\n[cyan]{title}[/cyan] [{default}]: ").strip()
        return result if result else default
    return console.input(f"\n[cyan]{title}[/cyan]: ").strip()


@app.command()
def main(
    keyword: Optional[str] = typer.Argument(None, help="搜索关键词"),
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
    from xiaohongshu_agent.providers import get_available_providers

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
        do_gui(agent, cfg)


def show_config(agent, cfg):
    """显示配置"""
    provider = cfg.get("llm_provider", "openai")
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


def do_gui(agent, cfg):
    """交互式 GUI 菜单"""
    from xiaohongshu_agent.providers import get_available_providers

    menu_items = [
        "🔍 搜索热门帖子",
        "📝 创建并发布帖子",
        "📊 查看数据统计",
        "🤖 AI 对话",
        "⚙️ 系统设置",
        "🚪 退出",
    ]

    while True:
        console.print()
        # 打印菜单
        console.print("[bold magenta]╔═══════════════════════════════════════╗[/bold magenta]")
        console.print("[bold magenta]║         小红书 AI Agent              ║[/bold magenta]")
        console.print("[bold magenta]╠═══════════════════════════════════════╣[/bold magenta]")

        for i, item in enumerate(menu_items):
            console.print(f"[bold magenta]║[bold]  {item:<36} ║[/bold]")

        console.print("[bold magenta]╚═══════════════════════════════════════╝[/bold magenta]")

        # 使用上下选择
        choice = select_option("请选择操作", menu_items)

        if choice is None or choice == 5:  # 退出
            console.print("\n[cyan]再见! 👋[/cyan]\n")
            break
        elif choice == 0:  # 搜索
            do_search_menu(agent)
        elif choice == 1:  # 发布
            do_publish_menu(agent)
        elif choice == 2:  # 统计
            do_stats(agent)
        elif choice == 3:  # 对话
            do_chat(agent)
        elif choice == 4:  # 设置
            do_settings_menu(agent, cfg)


def do_search_menu(agent):
    """搜索菜单"""
    keyword = input_text("搜索关键词", "AI")
    if keyword:
        do_search(agent, keyword)


def do_publish_menu(agent):
    """发布菜单"""
    console.print("\n[yellow]发布功能需要 MCP 服务运行中...[/yellow]")
    keyword = input_text("帖子主题", "AI")
    images = input_text("图片路径（逗号分隔）", "").split(",")

    if not images or not images[0].strip():
        console.print("[red]需要图片才能发布[/red]")
        return

    console.print("[cyan]AI 生成内容中...[/cyan]")
    content = agent.generate_content(keyword)

    console.print(f"\n[green]标题:[/green] {content.get('title')}")
    console.print(f"[green]标签:[/green] {' '.join(['#' + t for t in content.get('tags', [])])}")

    if confirm_dialog("确认发布", "确定要发布这篇帖子吗?"):
        result = agent.publish(content.get('title'), content.get('content'), images, content.get('tags'))
        if result.get("success"):
            console.print("[green]发布成功! 🎉[/green]")
        else:
            console.print(f"[red]发布失败: {result.get('error')}[/red]")


def do_settings_menu(agent, cfg):
    """设置菜单"""
    from xiaohongshu_agent.providers import get_available_providers

    settings_items = [
        "🔐 切换 LLM 提供商",
        "🔑 配置 API Key",
        "🌐 配置 MCP 地址",
        "📋 查看当前配置",
        "🧠 查看对话历史",
        "🔙 返回主菜单",
    ]

    while True:
        choice = select_option("系统设置", settings_items)

        if choice is None or choice == 5:
            break
        elif choice == 0:
            # 切换提供商
            providers = get_available_providers()
            provider_names = [f"{v['name']} ({k})" for k, v in providers.items()]
            idx = select_option("选择 LLM 提供商", provider_names)
            if idx is not None:
                provider_key = list(providers.keys())[idx]
                cfg.set("llm_provider", provider_key)
                cfg.save()
                console.print(f"[green]已切换到: {provider_names[idx]}[/green]")
        elif choice == 1:
            console.print("\n[yellow]请在配置文件中设置 API Key[/yellow]")
        elif choice == 2:
            new_url = input_text("MCP 地址", cfg.get("mcp_url"))
            cfg.set("mcp_url", new_url)
            cfg.save()
            console.print(f"[green]MCP 地址已更新: {new_url}[/green]")
        elif choice == 3:
            show_config(agent, cfg)
        elif choice == 4:
            # 查看对话历史
            history = agent.memory.get_history(10)
            console.print(f"\n[cyan]对话历史 ({len(history)} 条):[/cyan]\n")
            for i, msg in enumerate(history, 1):
                role = "[green]用户[/green]" if msg["role"] == "user" else "[magenta]AI[/magenta]"
                content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
                console.print(f"  {i}. {role}: {content}")


if __name__ == "__main__":
    app()
