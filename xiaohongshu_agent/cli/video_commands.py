"""
视频生成工作流 CLI 命令
"""
import os
import json
import time
from pathlib import Path

# #region agent log
_DEBUG_LOG = Path(__file__).resolve().parent.parent.parent / "debug-2ed257.log"
def _dlog(msg: str, data: dict, h: str = ""):
    try:
        with open(_DEBUG_LOG, "a") as f:
            f.write(json.dumps({"sessionId":"2ed257","runId":"create","hypothesisId":h,"location":"video_commands","message":msg,"data":data,"timestamp":int(time.time()*1000)}) + "\n")
    except Exception:
        pass
# #endregion

# 加载 config/.env（尝试项目根目录和 __file__ 相对路径）
try:
    from dotenv import load_dotenv, dotenv_values
    paths_tried = []
    used_path = None
    for base in (Path(__file__).resolve().parent.parent.parent, Path.cwd()):
        env_path = base / "config" / ".env"
        paths_tried.append(str(env_path))
        if env_path.exists():
            load_dotenv(env_path)
            used_path = str(env_path)
            break
    _dlog("module_load_dotenv", {"paths_tried": paths_tried, "used_path": used_path, "zhipu_set": bool(os.getenv("ZHIPU_API_KEY")), "minimax_set": bool(os.getenv("MINIMAX_API_KEY"))}, "H3")
    env_path_for_parse = used_path or (paths_tried[0] if paths_tried else None)
    if env_path_for_parse and Path(env_path_for_parse).exists():
        vals = dotenv_values(env_path_for_parse)
        _dlog("dotenv_parsed", {"keys": list(vals.keys()), "ZHIPU_len": len(vals.get("ZHIPU_API_KEY", "") or ""), "Zhipu_len": len(vals.get("Zhipu_API_KEY", "") or ""), "MINIMAX_len": len(vals.get("MINIMAX_API_KEY", "") or "")}, "H1,H2,H4")
except ImportError:
    _dlog("module_load_dotenv", {"error": "dotenv not installed"}, "H3")
except Exception as e:
    _dlog("module_load_dotenv", {"error": str(e)}, "H3")

import typer
from typing import Optional, List
from rich.console import Console

from xiaohongshu_agent.workflow import VideoWorkflow

console = Console()

video_app = typer.Typer(help="小红书视频生成工作流")


@video_app.command()
def create(
    images: str = typer.Option(..., "--images", "-i", help="产品图片路径,用逗号分隔"),
    product: str = typer.Option("", "--product", "-p", help="产品名称"),
    context: str = typer.Option("", "--context", "-c", help="额外上下文信息"),
    duration: int = typer.Option(10, "--duration", "-d", help="视频时长(秒)"),
    voice: str = typer.Option("male-qn-qingse", "--voice", "-v", help="配音音色"),
    publish: bool = typer.Option(False, "--publish", help="自动发布到小红书"),
    output: str = typer.Option("output/videos", "--output", "-o", help="输出目录"),
):
    """
    从产品图片生成小红书视频

    示例:
        xhs video create --images "img1.jpg,img2.jpg" --product "护肤品"
    """
    console.print("\n[bold cyan]🎬 小红书视频生成工作流[/bold cyan]\n")

    # 解析图片路径
    image_paths = [p.strip() for p in images.split(",") if p.strip()]

    if not image_paths:
        console.print("[red]错误: 请提供至少一张产品图片[/red]")
        raise typer.Exit(1)

    # 检查图片是否存在
    valid_images = []
    for path in image_paths:
        if os.path.exists(path):
            valid_images.append(path)
        else:
            console.print(f"[yellow]警告: 图片不存在: {path}[/yellow]")

    if not valid_images:
        console.print("[red]错误: 没有有效的图片文件[/red]")
        raise typer.Exit(1)

    # 再次加载 .env（确保在初始化工作流前已加载）
    try:
        from dotenv import load_dotenv
        loaded_path = None
        for env_path in [
            Path.cwd() / "config" / ".env",
            Path(__file__).resolve().parent.parent.parent / "config" / ".env",
        ]:
            if env_path.exists():
                load_dotenv(env_path, override=True)
                loaded_path = str(env_path)
                break
        # #region agent log
        _dlog("create_load_dotenv", {"loaded_path": loaded_path, "cwd": str(Path.cwd()), "zhipu_set": bool(os.getenv("ZHIPU_API_KEY")), "minimax_set": bool(os.getenv("MINIMAX_API_KEY"))}, "H3,H4,H5")
        # #endregion
    except ImportError:
        pass

    # 初始化工作流
    workflow = VideoWorkflow(output_dir=output)

    # 测试连接
    console.print("[cyan]测试 API 连接...[/cyan]")
    status = workflow.test()

    for service, result in status.items():
        status_icon = "✅" if "OK" in result or "已配置" in result else "❌"
        console.print(f"  {status_icon} {service}: {result}")

    if "❌" in str(status) or "未配置" in str(status):
        console.print("\n[yellow]请先配置 API Key 后再试[/yellow]")
        console.print("需要配置的环境变量:")
        console.print("  - ZHIPU_API_KEY (智谱多模态)")
        console.print("  - KLING_API_KEY (可灵视频)")
        console.print("  - MINIMAX_API_KEY (海螺音频)")
        raise typer.Exit(1)

    # 运行工作流
    console.print(f"\n[green]开始生成视频...[/green]")
    console.print(f"  📷 图片: {len(valid_images)} 张")
    console.print(f"  📦 产品: {product or '自动识别'}")
    console.print(f"  ⏱️ 时长: {duration}秒")
    console.print(f"  🔊 音色: {voice}\n")

    try:
        result = workflow.run(
            image_paths=valid_images,
            product_name=product,
            context=context,
            duration=duration,
            auto_publish=publish,
            voice=voice
        )

        if result.get("status") == "completed":
            console.print("\n[bold green]✅ 视频生成完成![/bold green]")
            console.print(f"  📹 视频: {result['output']['video']}")
            console.print(f"  ⏱️ 耗时: {result['duration']:.1f}秒")

            if "publish" in result.get("steps", {}):
                pub_result = result["steps"]["publish"]
                if pub_result.get("status") == "success":
                    console.print(f"  🌐 已发布: {pub_result.get('url', '')}")
        else:
            console.print(f"\n[bold red]❌ 生成失败[/bold red]")
            console.print(f"  错误: {result.get('error', '未知错误')}")

    except Exception as e:
        console.print(f"\n[bold red]❌ 错误: {str(e)}[/bold red]")


@video_app.command()
def test():
    """测试工作流组件连接状态"""
    console.print("\n[bold cyan]🔧 测试工作流组件[/bold cyan]\n")

    workflow = VideoWorkflow()
    status = workflow.test()

    for service, result in status.items():
        icon = "✅" if "OK" in result or "已配置" in result else "❌"
        console.print(f"  {icon} {service}: {result}")


@video_app.command()
def voices():
    """列出可用的配音音色"""
    from xiaohongshu_agent.workflow import AudioGenerator

    gen = AudioGenerator()
    voices = gen.get_available_voices()

    console.print("\n[bold cyan]🎤 可用音色[/bold cyan]\n")

    console.print("[bold]男声:[/bold]")
    for v in voices.get("male", []):
        console.print(f"  • {v}")

    console.print("\n[bold]女声:[/bold]")
    for v in voices.get("female", []):
        console.print(f"  • {v}")


if __name__ == "__main__":
    video_app()
