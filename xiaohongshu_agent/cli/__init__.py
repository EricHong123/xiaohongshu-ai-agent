"""
统一命令行入口

整合所有启动方式：
- agent: 启动 AI Agent
- web: 启动 Web 服务
- gateway: 启动 Gateway 服务
- dashboard: 启动控制面板
"""
import sys
import argparse
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent


def main():
    parser = argparse.ArgumentParser(
        prog="xhs-agent",
        description="小红书 AI Agent - 统一命令行工具"
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # Agent 命令
    agent_parser = subparsers.add_parser("agent", help="启动 AI Agent")
    agent_parser.add_argument("--chat", action="store_true", help="对话模式")
    agent_parser.add_argument("--search", metavar="KEYWORD", help="搜索模式")
    agent_parser.add_argument("--stats", action="store_true", help="查看统计")
    agent_parser.add_argument("--gui", action="store_true", help="交互式界面")

    # Web 命令
    web_parser = subparsers.add_parser("web", help="启动 Web 服务")
    web_parser.add_argument("--port", type=int, default=5003, help="端口号")
    web_parser.add_argument("--host", default="0.0.0.0", help="主机地址")

    # Gateway 命令
    gateway_parser = subparsers.add_parser("gateway", help="启动 Gateway 服务")
    gateway_parser.add_argument("--port", type=int, default=3000, help="端口号")

    # Dashboard 命令
    dashboard_parser = subparsers.add_parser("dashboard", help="启动控制面板")
    dashboard_parser.add_argument("--port", type=int, default=8080, help="端口号")

    # 版本
    parser.add_argument("--version", action="store_true", help="显示版本")

    args = parser.parse_args()

    if args.version:
        from xiaohongshu_agent import __version__
        print(f"xiaohongshu-agent v{__version__}")
        return

    if not args.command:
        # 默认启动交互式界面
        from xiaohongshu_agent.cli.commands import app as cli_app
        cli_app()
        return

    # 根据命令启动相应服务
    if args.command == "agent":
        from xiaohongshu_agent.cli.commands import app as cli_app
        cli_app()

    elif args.command == "web":
        from xiaohongshu_agent.web import app as web_app
        web_app.run(host=args.host, port=args.port, debug=False)

    elif args.command == "gateway":
        from xiaohongshu_agent.gateway.server.combined import CombinedServer
        server = CombinedServer(config={})
        server.run(http_port=args.port)

    elif args.command == "dashboard":
        sys.path.insert(0, str(PROJECT_ROOT))
        from run_dashboard import run_server
        run_server(args.port)


if __name__ == "__main__":
    main()
