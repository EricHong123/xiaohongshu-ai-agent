"""
命令行命令 - 增强版
支持键盘上下选择
"""
import sys
from pathlib import Path
from datetime import datetime
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
║                    🤖 AI Agent v1.2.0                                    ║
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
        return select_option_fallback(title, options)

    try:
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
    """数字选择回退方案"""
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
    """确认对话框"""
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
    """输入文本"""
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
    video: bool = typer.Option(False, "--video", help="视频生成模式"),
):
    """小红书 AI Agent"""
    print_banner()

    # 视频模式
    if video:
        from xiaohongshu_agent.cli.video_commands import video_app
        video_app()
        return
    from xiaohongshu_agent.bootstrap.build_agent import build_agent
    from xiaohongshu_agent.config import load_config

    cfg = load_config()

    console.print("\n[cyan]初始化 Agent...[/cyan]")
    agent = build_agent()

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
        console.print("  🔑 API: [green]已设置[/green]")
    else:
        console.print(f"  🔑 API: [red]未设置[/red]")

    mem = agent.get_memory_status()
    console.print(f"  🧠 记忆: [cyan]{mem['count']}/{mem['limit']}[/cyan] 条")


def do_search(agent, keyword):
    """搜索"""
    console.print(f"\n[cyan]搜索: {keyword}[/cyan]")
    from xiaohongshu_agent.apps.xhs.usecases import search_posts

    posts = search_posts(agent, keyword)

    if posts:
        console.print(f"\n[green]找到 {len(posts)} 条结果:[/green]\n")
        for i, p in enumerate(posts[:10], 1):
            console.print(f"  {i}. [yellow]{p.title[:40]}[/yellow]")
            console.print(f"      👍 {p.likes:,}  💬 {p.comments:,}  ⭐ {p.collects:,}\n")
    else:
        console.print("[yellow]未找到结果[/yellow]")


def do_stats(agent):
    """统计"""
    from xiaohongshu_agent.apps.xhs.usecases import get_stats

    stats = get_stats(agent)

    console.print("\n[bold cyan]📊 数据统计[/bold cyan]")
    console.print(f"  📝 已发布: [green]{stats.published_posts}[/green] 篇")
    console.print(f"  👍 总点赞: [red]{stats.total_likes}[/red]")
    console.print(f"  💬 总评论: [blue]{stats.total_comments}[/blue]")
    console.print(f"  ⭐ 已回复: [yellow]{stats.replied_comments}[/yellow]")


def do_chat(agent):
    """对话"""
    console.print("\n[bold magenta]🤖 AI 对话模式[/bold magenta]")
    console.print("  输入内容让 AI 帮你处理")
    console.print("  输入 'exit' 或 'q' 退出\n")

    from xiaohongshu_agent.apps.xhs.usecases import chat

    while True:
        try:
            user_input = input("[green]你[/green] > ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'q', 'quit']:
                break

            response = chat(agent, user_input)
            console.print(f"\n[magenta]🤖 AI[/magenta]: {response}\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]错误: {e}[/red]")


def do_video_menu():
    """视频工作流子菜单：生成视频 / 配置 API Key"""
    menu_items = [
        "🎬 生成视频",
        "📂 查看输出视频",
        "🔑 配置视频工作流 API Key / 模型",
        "⬅ 返回主菜单",
    ]

    from pathlib import Path as _Path
    import subprocess as _subprocess

    def _view_video_outputs():
        """列出并打开输出目录（默认 Finder）"""
        console.print("\n[bold cyan]📂 已生成的视频文件[/bold cyan]\n")

        # 兼容从项目根目录或任意目录启动 CLI 的情况
        candidates = [
            _Path.cwd() / "output" / "videos",
            _Path(__file__).resolve().parent.parent.parent / "output" / "videos",
        ]
        dir_path = next((p for p in candidates if p.exists()), None)

        if not dir_path:
            console.print("[yellow]暂未找到输出目录 output/videos，请先生成一次视频。[/yellow]")
            return

        files = sorted(
            [p for p in dir_path.glob("*.mp4") if p.is_file()],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if not files:
            console.print(f"[yellow]目录中暂时没有 mp4 视频文件: {dir_path}[/yellow]")
            # 仍然打开目录，方便你确认是否有其它输出
            try:
                if sys.platform == "darwin":
                    _subprocess.run(["open", str(dir_path)], check=False)
                elif sys.platform.startswith("win"):
                    _subprocess.run(["cmd", "/c", "start", "", str(dir_path)], check=False)
                else:
                    _subprocess.run(["xdg-open", str(dir_path)], check=False)
            except Exception:
                pass
            return

        console.print(f"[green]目录: {dir_path}[/green]\n")
        for idx, f in enumerate(files[:20], 1):
            mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            console.print(f"{idx}. {f.name}  [dim]({mtime})[/dim]")
            console.print(f"    路径: {f}")

        # 直接打开输出目录（macOS: Finder）
        try:
            if sys.platform == "darwin":
                _subprocess.run(["open", str(dir_path)], check=False)
            elif sys.platform.startswith("win"):
                _subprocess.run(["cmd", "/c", "start", "", str(dir_path)], check=False)
            else:
                _subprocess.run(["xdg-open", str(dir_path)], check=False)
            console.print("\n[green]已打开输出目录。[/green]")
        except Exception as e:
            console.print(f"[red]打开目录失败: {e}[/red]")
            console.print(f"[dim]你仍可手动打开该路径: {dir_path}[/dim]")

        console.print("\n[dim]提示：如需直接播放，复制上面某个 mp4 的路径到系统播放器打开即可。[/dim]")

    while True:
        choice = select_option("视频工作流", menu_items)
        if choice is None or choice == 3:
            break
        elif choice == 0:
            run_video_workflow_menu()
        elif choice == 1:
            _view_video_outputs()
        elif choice == 2:
            configure_video_env_keys()


def do_gui(agent, cfg):
    """交互式 GUI 菜单"""
    from xiaohongshu_agent.providers import get_available_providers

    menu_items = [
        "🔍 搜索热门帖子",
        "📝 创建并发布帖子",
        "🎬 视频生成工作流",
        "📊 查看数据统计",
        "🤖 AI 对话",
        "⚙️ 系统设置",
        "🚪 退出",
    ]

    while True:
        console.print()
        console.print("[bold magenta]╔═══════════════════════════════════════╗[/bold magenta]")
        console.print("[bold magenta]║         小红书 AI Agent              ║[/bold magenta]")
        console.print("[bold magenta]╠═══════════════════════════════════════╣[/bold magenta]")

        for i, item in enumerate(menu_items):
            console.print(f"[bold magenta]║[bold]  {item:<36} ║[/bold]")

        console.print("[bold magenta]╚═══════════════════════════════════════╝[/bold magenta]")

        choice = select_option("请选择操作", menu_items)

        if choice is None or choice == 6:
            console.print("\n[cyan]再见! 👋[/cyan]\n")
            break
        elif choice == 0:
            do_search_menu(agent)
        elif choice == 1:
            do_publish_menu(agent)
        elif choice == 2:
            do_video_menu()
        elif choice == 3:
            do_stats(agent)
        elif choice == 4:
            do_chat(agent)
        elif choice == 5:
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
    from xiaohongshu_agent.apps.xhs.usecases import generate_content

    content = generate_content(agent, keyword)

    console.print(f"\n[green]标题:[/green] {content.get('title')}")
    console.print(f"[green]标签:[/green] {' '.join(['#' + t for t in content.get('tags', [])])}")

    if confirm_dialog("确认发布", "确定要发布这篇帖子吗?"):
        from xiaohongshu_agent.apps.xhs.usecases import publish_post

        result = publish_post(
            agent,
            title=content.get("title"),
            content=content.get("content"),
            images=images,
            tags=content.get("tags"),
        )
        if result.success:
            console.print("[green]发布成功! 🎉[/green]")
        else:
            console.print(f"[red]发布失败: {result.error or '未知错误'}[/red]")


def do_video_workflow_help():
    """视频生成工作流入口说明"""
    console.print("\n[bold cyan]🎬 视频生成工作流[/bold cyan]\n")
    console.print("[yellow]当前版本通过命令行使用视频工作流。[/yellow]\n")
    console.print("示例：\n")
    console.print(
        "  [green]python3 -m xiaohongshu_agent --video create "
        "--images \"img1.jpg,img2.jpg\" --product \"护肤品\" --duration 10[/green]\n"
    )
    console.print("[dim]提示：视频工作流使用 config/.env 中的 ZHIPU_API_KEY / MINIMAX_API_KEY / KLING_API_KEY 及相关模型配置。[/dim]\n")


def run_video_workflow_menu():
    """在 CLI 中交互式启动视频生成工作流"""
    from xiaohongshu_agent.workflow import VideoWorkflow

    do_video_workflow_help()

    # 尝试加载 config/.env 以确保工作流用到最新 Key/模型
    try:
        from dotenv import load_dotenv

        base = Path(__file__).resolve().parent.parent.parent
        env_path = base / "config" / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=True)
    except Exception:
        pass

    console.print("\n[bold cyan]🎬 启动视频生成工作流[/bold cyan]\n")

    images = input_text("产品图片路径（本地路径，逗号分隔）", "")
    image_paths = [p.strip() for p in images.split(",") if p.strip()]
    if not image_paths:
        console.print("[yellow]未提供图片路径，已取消视频生成。[/yellow]")
        return

    product = input_text("产品名称", "测试产品")
    context = input_text("额外上下文（可选）", "")
    try:
        duration_str = input_text("视频时长（秒）", "10")
        duration = int(duration_str)
    except ValueError:
        duration = 10

    voice = input_text("配音音色 ID（留空使用默认 male-qn-qingse）", "male-qn-qingse")
    auto_publish = confirm_dialog("自动发布", "是否在生成后自动发布到小红书？")

    wf = VideoWorkflow(output_dir="output/videos")

    console.print(
        f"\n[green]开始生成视频...[/green]\n"
        f"  📷 图片: {len(image_paths)} 张\n"
        f"  📦 产品: {product or '自动识别'}\n"
        f"  ⏱️ 时长: {duration} 秒\n"
        f"  🔊 音色: {voice}\n"
    )

    try:
        result = wf.run(
            image_paths=image_paths,
            product_name=product,
            context=context,
            duration=duration,
            auto_publish=auto_publish,
            voice=voice,
        )

        status = result.get("status")
        if status == "completed":
            output = result.get("output", {})
            console.print("\n[bold green]✅ 视频生成完成![/bold green]")
            if output.get("video"):
                console.print(f"  📹 视频文件: {output['video']}")
            console.print(f"  ⏱️ 总耗时: {result.get('duration', 0):.1f} 秒")
            if "publish" in result.get("steps", {}):
                pub = result["steps"]["publish"]
                if pub.get("status") == "success":
                    console.print(f"  🌐 已发布: {pub.get('url', '')}")
        else:
            console.print("\n[bold red]❌ 视频生成失败[/bold red]")
            err = result.get("error", "未知错误")
            console.print(f"  错误: {err}")
            steps = result.get("steps", {})
            if steps.get("video", {}).get("last_error") and steps["video"].get("last_error") != err:
                console.print(f"  视频步骤详情: {steps['video']['last_error']}")
            if steps.get("analysis") and steps["analysis"].get("error"):
                console.print(f"  分析步骤: {steps['analysis']['error']}")
            if steps.get("script") and isinstance(steps["script"], dict) and steps["script"].get("error"):
                console.print(f"  脚本步骤: {steps['script']['error']}")
    except Exception as e:
        console.print(f"\n[bold red]❌ 运行工作流出错: {e}[/bold red]")


def configure_video_env_keys():
    """交互式配置视频工作流相关的 API Key（写入 config/.env）"""
    base = Path(__file__).resolve().parent.parent.parent
    env_path = base / "config" / ".env"

    existing = {}
    if env_path.exists():
        try:
            content = env_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                existing[k.strip()] = v.strip()
        except Exception:
            pass

    console.print("\n[cyan]配置将写入: [/cyan]" + str(env_path))
    console.print("[dim]已存在的值不会显示具体内容，仅显示是否已配置。[/dim]\n")

    keys = [
        ("ZHIPU_API_KEY", "智谱 GLM API Key"),
        ("ZHIPU_BASE_URL", "智谱 GLM Base URL（可选）"),
        ("MINIMAX_API_KEY", "Minimax API Key（音频/TTS）"),
        ("KLING_API_KEY", "Kling/可灵 视频生成 API Key"),
    ]

    for key, label in keys:
        masked = "（已配置）" if key in existing and existing[key] else "（未配置）"
        default = ""
        prompt_title = f"{label} [{key}] {masked}"
        value = input_text(prompt_title, default)
        if value.strip():
            existing[key] = value.strip()

    # 选择模型（主流选项）
    console.print("\n[bold cyan]选择各环节使用的模型（可留空使用默认）[/bold cyan]\n")

    # 图片分析模型（智谱）
    image_models = ["glm-4.6v", "glm-4", "glm-4-flash"]
    current_image = existing.get("ZHIPU_IMAGE_MODEL", "glm-4.6v")
    img_label = f"图片分析模型 [当前: {current_image}]"
    img_choice_idx = select_option(img_label, image_models + ["保持默认"])
    if img_choice_idx is not None and img_choice_idx < len(image_models):
        existing["ZHIPU_IMAGE_MODEL"] = image_models[img_choice_idx]

    # 脚本文案模型（Minimax）
    script_models = ["MiniMax-M2.5", "abab6.5s-chat", "abab6.5-chat"]
    current_script = existing.get("MINIMAX_SCRIPT_MODEL", "MiniMax-M2.5")
    script_label = f"脚本文案模型 [当前: {current_script}]"
    script_choice_idx = select_option(script_label, script_models + ["保持默认"])
    if script_choice_idx is not None and script_choice_idx < len(script_models):
        existing["MINIMAX_SCRIPT_MODEL"] = script_models[script_choice_idx]

    # 视频生成模型（智谱 CogVideoX 系列）
    video_models = ["cogvideoX-3", "cogvideoX-1.5"]
    current_video = existing.get("ZHIPU_VIDEO_MODEL", "cogvideoX-3")
    video_label = f"视频生成模型 [当前: {current_video}]"
    video_choice_idx = select_option(video_label, video_models + ["保持默认"])
    if video_choice_idx is not None and video_choice_idx < len(video_models):
        existing["ZHIPU_VIDEO_MODEL"] = video_models[video_choice_idx]

    # 音频/TTS 模型（Minimax）
    audio_models = ["speech-01-turbo", "speech-01"]
    current_audio = existing.get("MINIMAX_AUDIO_MODEL", "speech-01-turbo")
    audio_label = f"音频/TTS 模型 [当前: {current_audio}]"
    audio_choice_idx = select_option(audio_label, audio_models + ["保持默认"])
    if audio_choice_idx is not None and audio_choice_idx < len(audio_models):
        existing["MINIMAX_AUDIO_MODEL"] = audio_models[audio_choice_idx]

    try:
        env_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"{k}={v}" for k, v in existing.items()]
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        console.print(f"\n[green]已更新: {env_path}[/green]\n")
    except Exception as e:
        console.print(f"[red]写入失败: {e}[/red]")


def do_settings_menu(agent, cfg):
    """设置菜单"""
    from xiaohongshu_agent.providers import get_available_providers

    settings_items = [
        "🔐 切换 LLM 提供商",
        "📦 选择模型",
        "🔑 配置 API Key",
        "🌐 配置 MCP 地址",
        "📋 查看当前配置",
        "🧠 查看对话历史",
        "🔙 返回主菜单",
    ]

    while True:
        choice = select_option("系统设置", settings_items)

        if choice is None or choice == 6:
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
            # 选择模型
            providers = get_available_providers()
            provider = cfg.get("llm_provider", "openai")
            provider_info = providers.get(provider, providers["openai"])
            models = provider_info.get("models", [])
            current_model = cfg.get_model()

            # 添加当前模型标记
            model_options = []
            for m in models:
                if m == current_model:
                    model_options.append(f"{m} ✓")
                else:
                    model_options.append(m)

            idx = select_option(f"选择模型 ({provider})", model_options)
            if idx is not None:
                selected_model = models[idx]
                cfg.set(f"{provider}_model", selected_model)
                cfg.save()
                console.print(f"[green]已选择模型: {selected_model}[/green]")
        elif choice == 2:
            # 交互式配置 API Key
            providers = get_available_providers()
            current_provider = cfg.get("llm_provider", "openai")
            provider_info = providers.get(current_provider, providers.get("openai"))

            console.print(
                f"\n[cyan]当前提供商: {provider_info['name']} ({current_provider})[/cyan]"
            )
            console.print(
                "[dim]提示: 只会写入本机用户配置文件 ~/.xiaohongshu_agent/config.json[/dim]"
            )

            new_key = input_text("输入新的 API Key（留空则不修改）")
            if new_key.strip():
                cfg.set(f"{current_provider}_api_key", new_key.strip())
                cfg.save()
                console.print("[green]API Key 已更新并保存[/green]")
            else:
                console.print("[yellow]未输入内容，API Key 未修改[/yellow]")
        elif choice == 3:
            new_url = input_text("MCP 地址", cfg.get("mcp_url"))
            cfg.set("mcp_url", new_url)
            cfg.save()
            console.print(f"[green]MCP 地址已更新: {new_url}[/green]")
        elif choice == 4:
            show_config(agent, cfg)
        elif choice == 5:
            history = agent.memory.get_history(10)
            console.print(f"\n[cyan]对话历史 ({len(history)} 条):[/cyan]\n")
            for i, msg in enumerate(history, 1):
                role = "[green]用户[/green]" if msg["role"] == "user" else "[magenta]AI[/magenta]"
                content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
                console.print(f"  {i}. {role}: {content}")


if __name__ == "__main__":
    app()
