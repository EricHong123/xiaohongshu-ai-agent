#!/usr/bin/env python3
"""
小红书 AI Agent CLI
优化版命令行界面 - 更精美的视觉体验
"""
import os
import sys
import json
import time
import argparse
from typing import Optional, Dict, Any, List
from datetime import datetime
import threading

# 导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.enhanced_agent import EnhancedAgent
from src.config_manager import ConfigManager, get_available_providers


# ============== 增强颜色 ==============
class Colors:
    RESET = "\033[0m"
    # 基础颜色
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    # 亮色
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    # 样式
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    # 背景色
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"
    BG_MAGENTA = "\033[45m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_RED = "\033[41m"
    # 渐变色 (模拟)
    GRADIENT_START = "\033[38;2;255;100;100m"  # 粉红
    GRADIENT_MID = "\033[38;2;255;150;50m"    # 橙色
    GRADIENT_END = "\033[38;2;100;200;255m"   # 蓝色


# ============== ASCII 艺术 Banner ==============
BANNER = f"""
{Colors.BRIGHT_MAGENTA}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   █████╗ ██╗      ██████╗  ██████╗ ██████╗ ██╗   ██╗██╗     ███████╗███████╗ ║
║  ██╔══██╗██║     ██╔═══██╗██╔═══██╗██╔══██╗╚██╗ ██╔╝██║     ██╔════╝██╔════╝ ║
║  ███████║██║     ██║   ██║██║   ██║██████╔╝ ╚████╔╝ ██║     █████╗  ███████╗ ║
║  ██╔══██║██║     ██║   ██║██║   ██║██╔══██╗  ╚██╔╝  ██║     ██╔══╝  ╚════██║ ║
║  ██║  ██║███████╗╚██████╔╝╚██████╔╝██║  ██║   ██║   ███████╗███████╗███████║ ║
║  ╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚══════╝╚══════╝ ║
║                                                                           ║
║         🤖  AI Agent  v1.1.0                                    ║
║                                                                           ║
║    ┌─────────────────────────────────────────────────────────────────┐    ║
║    │  🔍 搜索  │  📝 发布  │  🧠 记忆  │  💻 控制  │  ⚙️ 设置      │    ║
║    └─────────────────────────────────────────────────────────────────┘    ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
{Colors.RESET}
"""


# ============== 加载动画 ==============
class Spinner:
    """加载动画"""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    dots = ["   ", ".  ", ".. ", "..."]

    def __init__(self, message: str = "加载中"):
        self.message = message
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)
        # 清除这一行
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()

    def _spin(self):
        i = 0
        while self.running:
            frame = self.frames[i % len(self.frames)]
            sys.stdout.write(f"\r{Colors.CYAN}{frame}{Colors.RESET} {self.message}{self.dots[i % len(self.dots)]}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1


# ============== 进度条 ==============
def print_progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '',
                       length: int = 40, fill: str = '█', empty: str = '░'):
    """打印进度条"""
    percent = 100 * (iteration / float(total))
    filled = int(length * iteration // total)
    bar = fill * filled + empty * (length - filled)
    sys.stdout.write(f'\r{Colors.CYAN}{prefix}{Colors.RESET} |{Colors.GREEN}{bar}{Colors.RESET}| {percent:.1f}% {suffix}')
    sys.stdout.flush()
    if iteration == total:
        print()


# ============== 表格打印 ==============
def print_table(headers: List[str], rows: List[List[str]], title: str = "") -> None:
    """打印美化表格"""
    if not rows:
        print_info("暂无数据")
        return

    # 计算每列宽度
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    # 边框样式
    border_color = Colors.CYAN
    header_color = Colors.BOLD + Colors.YELLOW
    cell_color = Colors.WHITE

    # 打印标题
    if title:
        print(f"\n{border_color}╔{'═' * (sum(col_widths) + len(col_widths) * 3 + 1)}╗{Colors.RESET}")
        title_padding = (sum(col_widths) + len(col_widths) * 3 + 1 - len(title)) // 2
        print(f"{border_color}║{' ' * title_padding}{Colors.BOLD}{title}{Colors.RESET}{border_color}{' ' * (sum(col_widths) + len(col_widths) * 3 + 1 - title_padding - len(title))}║{Colors.RESET}")
        print(f"{border_color}╠{'═' * (sum(col_widths) + len(col_widths) * 3 + 1)}╣{Colors.RESET}")
    else:
        print(f"\n{border_color}╔{'═' * (sum(col_widths) + len(col_widths) * 3 + 1)}╗{Colors.RESET}")

    # 打印表头
    header_row = "║ " + " │ ".join(
        h.ljust(col_widths[i]) for i, h in enumerate(headers)
    ) + " ║"
    print(f"{border_color}{header_row}{Colors.RESET}")
    print(f"{border_color}╟{'─' * (sum(col_widths) + len(col_widths) * 3 + 1)}╢{Colors.RESET}")

    # 打印数据行
    for row in rows:
        data_row = "║ " + " │ ".join(
            str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)
        ) + " ║"
        print(f"{cell_color}{data_row}{Colors.RESET}")

    # 打印底部
    print(f"{border_color}╚{'═' * (sum(col_widths) + len(col_widths) * 3 + 1)}╝{Colors.RESET}")


# ============== 确认框 ==============
def confirm(prompt: str, default: bool = False) -> bool:
    """带样式的确认框"""
    default_str = "Y/n" if default else "y/N"
    color = Colors.GREEN if default else Colors.RED

    while True:
        result = input(f"\n{Colors.YELLOW}{prompt} [{default_str}]: {Colors.RESET}").strip().lower()

        if not result:
            return default
        if result in ['y', 'yes', '是', '1']:
            return True
        if result in ['n', 'no', '否', '0']:
            return False

        print_error("请输入 y 或 n")


# ============== 打印函数 ==============
def print_banner():
    """打印横幅"""
    print(BANNER)
    print(f"  {Colors.DIM}启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print()


def print_success(msg: str):
    """成功消息"""
    print(f"\n{Colors.GREEN}✓ {msg}{Colors.RESET}\n")


def print_error(msg: str):
    """错误消息"""
    print(f"\n{Colors.RED}✗ {msg}{Colors.RESET}\n")


def print_warning(msg: str):
    """警告消息"""
    print(f"\n{Colors.YELLOW}⚠ {msg}{Colors.RESET}\n")


def print_info(msg: str):
    """信息消息"""
    print(f"\n{Colors.BLUE}ℹ {msg}{Colors.RESET}\n")


def print_header(title: str):
    """打印标题"""
    width = 60
    print(f"\n{Colors.CYAN}{Colors.BOLD}")
    print("┌" + "─" * width + "┐")
    print(f"│ {title.center(width - 2)} │")
    print("└" + "─" * width + "┘")
    print(Colors.RESET)


# ============== 菜单显示 ==============
def print_menu(title: str, options: List[tuple], footer: str = "") -> None:
    """打印美化菜单"""
    width = 62

    # 标题
    print(f"\n{Colors.CYAN}{Colors.BOLD}┌{'─' * width}┐{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}│{Colors.RESET}{Colors.BRIGHT_MAGENTA} {title.center(width - 2)}{Colors.RESET}{Colors.CYAN}{Colors.BOLD} │{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}├{'─' * width}┤{Colors.RESET}")

    # 选项
    for key, desc, _ in options:
        if key == "":  # 分隔符
            print(f"{Colors.CYAN}│{Colors.RESET}  {Colors.DIM}{'─' * (width - 4)}{Colors.RESET}{Colors.CYAN} │{Colors.RESET}")
        else:
            # 计算空格填充
            padding = width - len(desc) - len(key) - 10
            print(f"{Colors.CYAN}│{Colors.RESET}  {Colors.YELLOW}{key:^4}{Colors.RESET}   {desc}{' ' * max(0, padding)}{Colors.CYAN} │{Colors.RESET}")

    # 底部
    print(f"{Colors.CYAN}{Colors.BOLD}└{'─' * width}┘{Colors.RESET}")

    if footer:
        print(f"{Colors.DIM}{footer}{Colors.RESET}")


def print_box(content: str, title: str = "", color: str = Colors.CYAN) -> None:
    """打印内容框"""
    lines = content.split('\n')
    width = max(len(l) for l in lines) + 4

    print(f"\n{color}┌{'─' * width}┐{Colors.RESET}")
    if title:
        print(f"{color}│{Colors.RESET}{title.center(width - 2)}{color}│{Colors.RESET}")
        print(f"{color}├{'─' * width}┤{Colors.RESET}")

    for line in lines:
        print(f"{color}│{Colors.RESET} {line}{' ' * (width - len(line) - 3)}{color}│{Colors.RESET}")

    print(f"{color}└{'─' * width}┘{Colors.RESET}\n")


# ============== 输入 ==============
def input_text(prompt: str, default: str = "") -> str:
    """带默认值的输入"""
    if default:
        result = input(f"{Colors.CYAN}{prompt}{Colors.RESET} [{Colors.GREEN}{default}{Colors.RESET}]: ").strip()
        return result if result else default
    return input(f"{Colors.CYAN}{prompt}{Colors.RESET}: ").strip()


def input_choice(prompt: str, choices: List[str], default: int = 1) -> str:
    """选择输入"""
    print(f"\n{Colors.CYAN}{prompt}{Colors.RESET}")
    for i, choice in enumerate(choices, 1):
        marker = "◉" if i == default else "○"
        print(f"  {Colors.YELLOW}{i}.{Colors.RESET} {marker} {choice}")

    while True:
        try:
            result = input(f"\n{Colors.CYAN}请选择 [{default}]{Colors.RESET}: ").strip()
            if not result:
                return choices[default - 1]
            idx = int(result)
            if 1 <= idx <= len(choices):
                return choices[idx - 1]
        except ValueError:
            pass
        print_error("无效选择，请重新输入")


# ============== 分页显示 ==============
class Pager:
    """分页器"""
    def __init__(self, items: List[Any], per_page: int = 10):
        self.items = items
        self.per_page = per_page
        self.total = len(items)
        self.pages = (self.total + per_page - 1) // per_page

    def show(self, render_func, title: str = "") -> None:
        """显示分页内容"""
        if not self.items:
            print_info("暂无数据")
            return

        page = 1
        while True:
            start = (page - 1) * self.per_page
            end = min(start + self.per_page, self.total)
            page_items = self.items[start:end]

            # 显示标题
            print(f"\n{Colors.CYAN}{'─' * 60}{Colors.RESET}")
            if title:
                print(f"{Colors.BOLD}{title}{Colors.RESET} (第 {page}/{self.pages} 页，共 {self.total} 条)")
                print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")

            # 渲染内容
            for i, item in enumerate(page_items, start + 1):
                render_func(i, item)

            # 分页控制
            print(f"\n{Colors.DIM}[P]上一页 [N]下一页 [Q]返回 [{Colors.GREEN}输入页码{Colors.DIM}]{Colors.RESET}")
            cmd = input(f"{Colors.CYAN}请选择{Colors.RESET}: ").strip().lower()

            if cmd == 'q':
                break
            elif cmd == 'p' and page > 1:
                page -= 1
            elif cmd == 'n' and page < self.pages:
                page += 1
            else:
                try:
                    new_page = int(cmd)
                    if 1 <= new_page <= self.pages:
                        page = new_page
                except ValueError:
                    pass


# ============== 命令历史 ==============
class CommandHistory:
    """命令历史记录"""
    def __init__(self, max_size: int = 100):
        self.history = []
        self.max_size = max_size
        self.index = -1

    def add(self, cmd: str):
        """添加命令"""
        if cmd and (not self.history or self.history[-1] != cmd):
            self.history.append(cmd)
            if len(self.history) > self.max_size:
                self.history.pop(0)
        self.index = len(self.history)

    def get_previous(self) -> Optional[str]:
        """获取上一个命令"""
        if self.history and self.index > 0:
            self.index -= 1
            return self.history[self.index]
        return None

    def get_next(self) -> Optional[str]:
        """获取下一个命令"""
        if self.index < len(self.history) - 1:
            self.index += 1
            return self.history[self.index]
        self.index = len(self.history)
        return None


# ============== CLI 主类 ==============
class XiaohongshuCLI:
    """小红书 CLI - 优化版"""

    def __init__(self):
        self.config = ConfigManager()
        self.agent: Optional[EnhancedAgent] = None
        self.running = True
        self.history = CommandHistory()

        # 欢迎动画
        self._welcome()

    def _welcome(self):
        """欢迎动画"""
        print(f"\n{Colors.CYAN}初始化配置加载器{Colors.RESET}...", end="")
        time.sleep(0.3)
        print(f" {Colors.GREEN}完成{Colors.RESET}")

        print(f"{Colors.CYAN}加载主题配置{Colors.RESET}...", end="")
        time.sleep(0.2)
        print(f" {Colors.GREEN}完成{Colors.RESET}")

        print(f"{Colors.CYAN}初始化命令系统{Colors.RESET}...", end="")
        time.sleep(0.2)
        print(f" {Colors.GREEN}完成{Colors.RESET}")

    def init_agent(self) -> bool:
        """初始化 Agent"""
        print_info("正在初始化 Agent...")

        # 获取配置
        provider = self.config.get("llm_provider", "openai")
        model = self.config.get_model(provider)
        mcp_url = self.config.get("mcp_url", "http://localhost:18060/mcp")

        # 设置环境变量
        api_key = self.config.get_api_key(provider)
        if api_key:
            os.environ[f"{provider.upper()}_API_KEY"] = api_key
            os.environ["LLM_PROVIDER"] = provider

        # 带动画的初始化
        print(f"{Colors.CYAN}├─{Colors.RESET} 加载 LLM 适配器...", end="")
        sys.stdout.flush()
        time.sleep(0.3)
        print(f" {Colors.GREEN}✓{Colors.RESET}\n")

        try:
            self.agent = EnhancedAgent(
                mcp_url=mcp_url,
                enable_permissions=self.config.get("permissions", ["file_read", "browser_control", "clipboard"])
            )

            # 打印初始化结果
            print_box(
                f"""
{Colors.GREEN}🎉 Agent 初始化完成!{Colors.RESET}

  🤖 LLM 提供商: {Colors.BRIGHT_CYAN}{provider}{Colors.RESET}
  📦 模型: {Colors.BRIGHT_YELLOW}{model}{Colors.RESET}
  🔗 MCP: {mcp_url}
  🧠 对话历史: {self.agent.db.get_chat_history_count()} 条
  📚 知识库: {len(self.agent.rag.knowledge_base)} 条
                """,
                title=" 初始化成功 "
            )

            return True
        except Exception as e:
            print_error(f"初始化失败: {e}")
            return False

    # ============== 配置功能 ==============
    def config_provider(self):
        """配置 LLM 提供商"""
        print_header("选择 LLM 提供商")

        providers = get_available_providers()
        options = []
        for i, (key, info) in enumerate(providers.items(), 1):
            current = f" {Colors.GREEN}✓ 当前{Colors.RESET}" if key == self.config.get("llm_provider") else ""
            options.append((str(i), f"{info['name']}{current}", key))

        # 添加返回选项
        options.append(("B", "返回", None))

        print_menu("可用提供商", options)

        choice = input(f"\n{Colors.CYAN}请选择 [1]{Colors.RESET}: ").strip()

        try:
            idx = int(choice) if choice else 1
            if 1 <= idx <= len(providers):
                selected_provider = list(providers.keys())[idx - 1]
                self.config.set("llm_provider", selected_provider)

                # 选择模型
                print(f"\n{Colors.CYAN}选择模型:{Colors.RESET}\n")
                models = providers[selected_provider]["models"]
                for i, model in enumerate(models, 1):
                    print(f"  {Colors.YELLOW}{i}.{Colors.RESET} {model}")

                model_choice = input(f"\n{Colors.CYAN}请选择 [1]{Colors.RESET}: ").strip() or "1"
                if 1 <= int(model_choice) <= len(models):
                    selected_model = models[int(model_choice) - 1]
                    self.config.set_model(selected_provider, selected_model)

                self.config.save()
                print_success(f"已保存: {selected_provider} - {selected_model}")
        except (ValueError, IndexError):
            print_error("无效选择")

    def config_api_key(self):
        """配置 API Key"""
        print_header("配置 API Key")

        providers = get_available_providers()
        provider = self.config.get("llm_provider", "openai")
        provider_info = providers.get(provider, {})

        print(f"\n  {Colors.CYAN}当前提供商:{Colors.RESET} {provider_info.get('name', provider)}")
        print(f"  {Colors.CYAN}环境变量:{Colors.RESET} {provider_info.get('env_key', '')}\n")

        # 显示当前状态
        current_key = self.config.get_api_key(provider)
        if current_key:
            masked = current_key[:8] + "..." + current_key[-4:]
            print(f"  {Colors.GREEN}状态: 已配置 ({masked}){Colors.RESET}")
        elif os.getenv(provider_info.get("env_key", "")):
            print(f"  {Colors.GREEN}状态: 已配置 (环境变量){Colors.RESET}")
        else:
            print(f"  {Colors.RED}状态: 未配置{Colors.RESET}")

        print(f"\n  {Colors.YELLOW}输入新 API Key (直接回车跳过):{Colors.RESET}")
        new_key = input("  > ").strip()

        if new_key:
            self.config.set_api_key(provider, new_key)
            print_success("API Key 已保存")
        else:
            print_info("保留原配置")

    def config_mcp(self):
        """配置 MCP"""
        print_header("配置 MCP 地址")

        current = self.config.get("mcp_url", "http://localhost:18060/mcp")
        print(f"\n  {Colors.CYAN}当前地址:{Colors.RESET} {current}\n")

        new_url = input_text("新 MCP 地址", current)
        self.config.set("mcp_url", new_url)
        self.config.save()
        print_success(f"MCP 地址已更新: {new_url}")

    def config_permissions(self):
        """配置权限"""
        print_header("配置权限")

        all_perms = [
            ("file_read", "读取文件", "📖"),
            ("file_write", "写入文件", "✏️"),
            ("command_exec", "执行命令", "💻"),
            ("browser_control", "控制浏览器", "🌐"),
            ("screenshot", "截图", "📸"),
            ("clipboard", "剪贴板", "📋"),
        ]

        current_perms = self.config.get("permissions", [])

        print(f"\n{Colors.CYAN}可选权限:{Colors.RESET}\n")
        for perm, desc, icon in all_perms:
            enabled = perm in current_perms
            status = f"{Colors.GREEN}◉ 启用{Colors.RESET}" if enabled else f"{Colors.RED}○ 禁用{Colors.RESET}"
            print(f"  {icon} {perm:<18} {desc:<12} {status}")

        print(f"\n{Colors.YELLOW}输入要启用的权限（逗号分隔）:{Colors.RESET}")
        new_perms = input("  > ").strip()

        if new_perms:
            perm_list = [p.strip() for p in new_perms.split(",")]
            self.config.set("permissions", perm_list)
            self.config.save()
            print_success(f"权限已更新: {', '.join(perm_list)}")

    def show_config(self):
        """显示当前配置"""
        print_header("当前配置")

        provider = self.config.get("llm_provider", "openai")
        providers = get_available_providers()
        provider_info = providers.get(provider, {})

        # 配置表格
        config_data = [
            ["🤖 LLM 提供商", provider_info.get('name', provider)],
            ["📦 模型", self.config.get_model(provider)],
            ["🔗 MCP 地址", self.config.get('mcp_url')],
            ["🔐 权限", ', '.join(self.config.get('permissions', []))],
        ]

        # API Key 状态
        api_key = self.config.get_api_key(provider)
        env_key = provider_info.get("env_key", "")
        if api_key:
            api_status = f"{Colors.GREEN}{api_key[:8]}...{api_key[-4:]}{Colors.RESET}"
        elif os.getenv(env_key):
            api_status = f"{Colors.GREEN}环境变量{Colors.RESET}"
        else:
            api_status = f"{Colors.RED}未设置{Colors.RESET}"

        config_data.append(["🔑 API Key", api_status])

        print()
        for label, value in config_data:
            print(f"  {Colors.CYAN}{label:<12}{Colors.RESET} {value}")

        # Memory 状态
        if self.agent:
            mem_status = self.agent.get_memory_status()
            print(f"\n  {Colors.CYAN}{'🧠 对话历史':<12}{Colors.RESET} {mem_status['history_count']}/{mem_status['limit']} 条")

        print()

    # ============== Memory 功能 ==============
    def show_memory(self):
        """显示对话历史"""
        print_header("对话历史 (Memory)")

        status = self.agent.get_memory_status()
        print(f"\n  {Colors.CYAN}当前记录:{Colors.RESET} {status['history_count']} 条")
        print(f"  {Colors.CYAN}保存上限:{Colors.RESET} {status['limit']} 条")

        history = self.agent.db.get_chat_history(50)
        if history:
            print(f"\n{Colors.CYAN}最近对话:{Colors.RESET}\n")

            # 分页显示
            pager = Pager(history, per_page=8)

            def render(idx, msg):
                role = msg["role"]
                icon = "👤" if role == "user" else "🤖"
                role_color = Colors.GREEN if role == "user" else Colors.MAGENTA
                content = msg["content"]

                # 截断长内容
                if len(content) > 50:
                    content = content[:50] + "..."

                time_str = msg.get("created_at", "")[:19]
                print(f"  {icon} {role_color}{role:<8}{Colors.RESET} {content:<52} {Colors.DIM}{time_str}{Colors.RESET}")

            pager.show(render, "对话记录")
        else:
            print_info("暂无对话历史")

    def clear_memory(self):
        """清空对话历史"""
        print_header("清空对话历史")

        status = self.agent.get_memory_status()
        print(f"\n{Colors.YELLOW}当前有 {status['history_count']} 条对话历史将被永久删除！{Colors.RESET}\n")

        if confirm("确定要清空所有对话历史吗？"):
            result = self.agent.clear_memory()
            print_success(result)
        else:
            print_info("已取消")

    # ============== 主菜单 ==============
    def main_menu(self):
        """主菜单"""
        options = [
            ("1", "🔍 搜索热门帖子", self.search_posts),
            ("2", "📝 创建并发布帖子", self.create_post),
            ("3", "📊 查看数据统计", self.view_stats),
            ("", "", None),
            ("4", "📁 文件管理", self.file_menu),
            ("5", "💻 电脑控制", self.computer_menu),
            ("6", "🤖 AI 对话", self.ai_chat),
            ("", "", None),
            ("S", "⚙️ 系统设置", self.settings_menu),
            ("H", "📖 帮助", self.show_help),
            ("Q", "🚪 退出", self.quit),
        ]

        while self.running:
            print_menu("主菜单", options, footer=f"  {Colors.DIM}输入选项按回车 | S:设置 | H:帮助 | Q:退出{Colors.RESET}")
            choice = input(f"\n{Colors.BRIGHT_GREEN}请选择 > {Colors.RESET}").strip().upper()

            # 保存到历史
            if choice:
                self.history.add(choice)

            if choice == 'Q':
                self.quit()
            elif choice == 'S':
                self.settings_menu()
            elif choice == 'H':
                self.show_help()
            elif choice == '4':
                self.file_menu()
            elif choice == '5':
                self.computer_menu()
            else:
                for key, _, func in options:
                    if choice == key and func:
                        try:
                            func()
                        except Exception as e:
                            print_error(f"执行错误: {e}")
                            import traceback
                            traceback.print_exc()

    def show_help(self):
        """显示帮助"""
        print_box("""
╔═══════════════════════════════════════════════════════════════╗
║                      小红书 AI Agent 帮助                      ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  主菜单功能:                                                  ║
║                                                               ║
║    [1] 🔍 搜索热门帖子                                        ║
║         搜索小红书上的热门内容                                ║
║                                                               ║
║    [2] 📝 创建并发布帖子                                      ║
║         AI 生成内容并发布到小红书                            ║
║                                                               ║
║    [3] 📊 查看数据统计                                        ║
║         查看已发布笔记的数据统计                             ║
║                                                               ║
║    [4] 📁 文件管理                                           ║
║         读取、写入、列出本地文件                             ║
║                                                               ║
║    [5] 💻 电脑控制                                           ║
║         浏览器、截图、剪贴板、命令执行等                      ║
║                                                               ║
║    [6] 🤖 AI 对话                                            ║
║         与 AI 助手进行多轮对话                               ║
║                                                               ║
║    [S] ⚙️ 系统设置                                           ║
║         配置 LLM、API Key、权限等                            ║
║                                                               ║
║  快捷键:                                                     ║
║                                                               ║
║    Ctrl+C    取消当前操作                                    ║
║    Ctrl+L    清屏                                            ║
║    Exit/Quit 退出对话                                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
        """, title=" 帮助文档 ")

    # ============== 功能实现 ==============
    def search_posts(self):
        """搜索帖子"""
        keyword = input_text("搜索关键词", "AI Agent")
        if not keyword:
            return

        spinner = Spinner(f"正在搜索: {keyword}")
        spinner.start()

        posts = self.agent.search(keyword)

        spinner.stop()

        if posts:
            print_box(
                f"\n{Colors.GREEN}找到 {len(posts)} 条结果:{Colors.RESET}\n" +
                "\n".join([
                    f"  {Colors.CYAN}{i:2}.{Colors.RESET} {p.get('title', '无标题')[:40]}..."
                    f"\n      {Colors.YELLOW}👍{Colors.RESET} {p.get('likes', 0):>5}  "
                    f"{Colors.BLUE}💬{Colors.RESET} {p.get('comments', 0):>5}  "
                    f"{Colors.MAGENTA}⭐{Colors.RESET} {p.get('collects', 0):>5}"
                    for i, p in enumerate(posts[:10], 1)
                ]),
                title=f" 搜索结果: {keyword} "
            )
        else:
            print_warning("未找到相关帖子")

    def create_post(self):
        """创建并发布帖子"""
        keyword = input_text("帖子主题", "AI Agent")
        images_input = input_text("图片路径（逗号分隔）", "")
        images = [img.strip() for img in images_input.split(",") if img.strip()]

        if not images:
            print_error("需要图片才能发布")
            return

        spinner = Spinner("AI 正在生成内容...")
        spinner.start()

        content = self.agent.generate_content(keyword)
        spinner.stop()

        print_box(
            f"""
{Colors.CYAN}生成内容:{Colors.RESET}

  {Colors.YELLOW}标题:{Colors.RESET} {content.get('title')}
  {Colors.CYAN}标签:{Colors.RESET} {' '.join(['#' + t for t in content.get('tags', [])])}

  {Colors.CYAN}正文:{Colors.RESET}
  {content.get('content', '')[:200]}...
            """,
            title=" 预览 "
        )

        if confirm("确认发布?"):
            spinner = Spinner("正在发布...")
            spinner.start()

            result = self.agent.publish(content, images)
            spinner.stop()

            if result.get("success"):
                print_success("发布成功! 🎉")
            else:
                print_error(f"发布失败: {result.get('error')}")
        else:
            print_info("已取消发布")

    def view_stats(self):
        """查看统计"""
        stats = self.agent.get_stats()

        print_box(
            f"""
  📊 {Colors.BOLD}数据统计{Colors.RESET}

    📝 已发布帖子:    {Colors.CYAN}{stats.get('published_posts', 0):>5}{Colors.RESET} 篇
    👍 总点赞数:      {Colors.RED}{stats.get('total_likes', 0):>5}{Colors.RESET}
    💬 总评论数:      {Colors.BLUE}{stats.get('total_comments', 0):>5}{Colors.RESET}
    ⭐ 已回复:        {Colors.GREEN}{stats.get('replied_comments', 0):>5}{Colors.RESET}
    📚 知识库:        {Colors.YELLOW}{stats.get('knowledge_items', 0):>5}{Colors.RESET} 条
            """,
            title=" 数据统计 "
        )

    # ============== 文件菜单 ==============
    def file_menu(self):
        """文件菜单"""
        options = [
            ("1", "📂 列出目录", self.list_files),
            ("2", "📄 读取文件", self.read_file),
            ("3", "📝 写入文件", self.write_file),
            ("B", "🔙 返回主菜单", lambda: None),
        ]

        while True:
            print_menu("文件管理", options)
            choice = input(f"\n{Colors.GREEN}请选择 > {Colors.RESET}").strip().upper()

            if choice == 'B':
                break
            elif choice == '1':
                self.list_files()
            elif choice == '2':
                self.read_file()
            elif choice == '3':
                self.write_file()

    def list_files(self):
        """列文件"""
        path = input_text("目录路径", os.path.expanduser("~/Desktop"))

        result = self.agent.list_files(path)

        if result.get("success"):
            items = result.get("items", [])
            print(f"\n{Colors.CYAN}📁 {result.get('path')}{Colors.RESET}")
            print(f"  {Colors.DIM}共 {len(items)} 个项目{Colors.RESET}\n")

            for item in items[:20]:
                icon = "📁" if item["type"] == "directory" else "📄"
                size = item.get("size", 0)
                if size > 1024 * 1024:
                    size_str = f"{size / 1024 / 1024:.1f}M"
                elif size > 1024:
                    size_str = f"{size / 1024:.1f}K"
                else:
                    size_str = f"{size}B"

                print(f"  {icon} {item['name'][:40]:<40} {Colors.YELLOW}{size_str:>10}{Colors.RESET}")
        else:
            print_error(f"错误: {result.get('error')}")

    def read_file(self):
        """读文件"""
        path = input_text("文件路径")
        result = self.agent.read_file(path)

        if result.get("success"):
            print_box(
                f"\n{result.get('content', '')}",
                title=f" 📄 {path} ({result.get('size')} bytes) "
            )
        else:
            print_error(f"错误: {result.get('error')}")

    def write_file(self):
        """写文件"""
        path = input_text("文件路径")
        content = input_text("文件内容")

        result = self.agent.write_file(path, content)

        if result.get("success"):
            print_success(f"已写入: {path}")
        else:
            print_error(f"错误: {result.get('error')}")

    # ============== 电脑控制菜单 ==============
    def computer_menu(self):
        """电脑控制菜单"""
        options = [
            ("1", "🌐 打开网页", self.open_browser),
            ("2", "📸 截屏", self.take_screenshot),
            ("3", "📋 读剪贴板", lambda: self.clipboard_oper(False)),
            ("4", "📋 写剪贴板", lambda: self.clipboard_oper(True)),
            ("5", "🔔 发送通知", self.send_notification),
            ("6", "🔊 语音播报", self.speak_text),
            ("7", "💻 执行命令", self.execute_command),
            ("B", "🔙 返回主菜单", lambda: None),
        ]

        while True:
            print_menu("电脑控制", options)
            choice = input(f"\n{Colors.GREEN}请选择 > {Colors.RESET}").strip().upper()

            if choice == 'B':
                break

            func_map = {
                '1': self.open_browser,
                '2': self.take_screenshot,
                '3': lambda: self.clipboard_oper(False),
                '4': lambda: self.clipboard_oper(True),
                '5': self.send_notification,
                '6': self.speak_text,
                '7': self.execute_command,
            }

            if choice in func_map:
                try:
                    func_map[choice]()
                except Exception as e:
                    print_error(f"执行错误: {e}")

    def open_browser(self):
        """打开浏览器"""
        url = input_text("网址", "https://www.xiaohongshu.com")
        result = self.agent.open_browser(url)
        print_success(f"已打开: {url}") if result.get("success") else print_error(f"错误: {result.get('error')}")

    def take_screenshot(self):
        """截图"""
        result = self.agent.take_screenshot()
        print_success(f"截图保存到: {result.get('path')}") if result.get("success") else print_error(f"错误: {result.get('error')}")

    def clipboard_oper(self, write: bool):
        """剪贴板操作"""
        if write:
            content = input_text("内容")
            result = self.agent.write_clipboard(content)
        else:
            result = self.agent.read_clipboard()

        if result.get("success"):
            if write:
                print_success("已复制到剪贴板")
            else:
                print_box(result.get("content", ""), title=" 剪贴板内容 ")
        else:
            print_error(f"错误: {result.get('error')}")

    def send_notification(self):
        """发送通知"""
        title = input_text("标题", "AI Agent")
        message = input_text("消息内容")
        result = self.agent.send_notification(title, message)
        print_success("通知已发送") if result.get("success") else print_error(f"错误: {result.get('error')}")

    def speak_text(self):
        """语音播报"""
        text = input_text("要朗读的内容")
        result = self.agent.speak(text)
        print_success("正在朗读...") if result.get("success") else print_error(f"错误: {result.get('error')}")

    def execute_command(self):
        """执行命令"""
        if not self.agent.computer.security.permissions.has_permission("command_exec"):
            print_error("没有命令执行权限")
            return

        command = input_text("命令")
        spinner = Spinner("执行中...")
        spinner.start()

        result = self.agent.execute_command(command)
        spinner.stop()

        if result.get("success"):
            print_box(result.get("stdout", "")[:1000], title=" 命令输出 ")
        else:
            print_error(f"错误: {result.get('error')}")

    # ============== AI 对话 ==============
    def ai_chat(self):
        """AI 对话"""
        print_box(
            """
  🤖 AI 对话模式

  • 输入内容让 AI 帮你处理
  • 支持多轮对话，AI 会记住之前的对话
  • 输入 'exit' 或 'q' 退出
  • 输入 'help' 查看帮助
            """,
            title=" AI 对话 "
        )

        while True:
            try:
                user_input = input(f"\n{Colors.GREEN}你{Colors.RESET} > ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'q', 'quit']:
                    print_info("退出对话")
                    break

                if user_input.lower() in ['help', 'h']:
                    print_box("""
  对话命令:
    exit, q, quit   退出对话
    help, h         显示帮助
    clear           清屏
    memory          查看对话历史数量
                    """, title=" 帮助 ")
                    continue

                if user_input.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue

                if user_input.lower() == 'memory':
                    status = self.agent.get_memory_status()
                    print_info(f"对话历史: {status['history_count']}/{status['limit']} 条")
                    continue

                # AI 回复
                response = self.agent.chat(user_input)

                print(f"\n{Colors.MAGENTA}🤖 AI{Colors.RESET}: {response}\n")

            except KeyboardInterrupt:
                print()
                break
            except Exception as e:
                print_error(f"错误: {e}")

    # ============== 设置菜单 ==============
    def settings_menu(self):
        """设置菜单"""
        options = [
            ("1", "🔐 选择 LLM 提供商", self.config_provider),
            ("2", "🔑 配置 API Key", self.config_api_key),
            ("3", "🌐 配置 MCP 地址", self.config_mcp),
            ("4", "⚡ 配置权限", self.config_permissions),
            ("5", "📋 查看当前配置", self.show_config),
            ("6", "🧠 查看对话历史", self.show_memory),
            ("7", "🗑️ 清空对话历史", self.clear_memory),
            ("B", "🔙 返回主菜单", lambda: None),
        ]

        while True:
            print_menu("系统设置", options)
            choice = input(f"\n{Colors.GREEN}请选择 > {Colors.RESET}").strip().upper()

            if choice == 'B':
                break

            func_map = {
                '1': self.config_provider,
                '2': self.config_api_key,
                '3': self.config_mcp,
                '4': self.config_permissions,
                '5': self.show_config,
                '6': self.show_memory,
                '7': self.clear_memory,
            }

            if choice in func_map:
                try:
                    func_map[choice]()
                except Exception as e:
                    print_error(f"错误: {e}")

    def quit(self):
        """退出"""
        print(f"\n{Colors.CYAN}{'═' * 50}{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}  再见! 感谢使用小红书 AI Agent 👋{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 50}{Colors.RESET}\n")
        self.running = False


# ============== 入口 ==============
def main():
    parser = argparse.ArgumentParser(
        description="小红书 AI Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-k", "--keyword", help="搜索关键词")
    parser.add_argument("--search", action="store_true", help="搜索模式")
    parser.add_argument("--stats", action="store_true", help="查看统计")
    parser.add_argument("--chat", action="store_true", help="AI 对话模式")
    parser.add_argument("--config", action="store_true", help="显示配置")
    parser.add_argument("--gui", action="store_true", help="启动交互式界面")

    args = parser.parse_args()

    print_banner()

    # 创建 CLI
    cli = XiaohongshuCLI()

    # 显示配置
    if args.config:
        cli.init_agent()
        cli.show_config()
        return

    # 初始化
    if not cli.init_agent():
        return

    # 执行命令
    if args.search or args.keyword:
        posts = cli.agent.search(args.keyword or "AI Agent")
        print(f"\n找到 {len(posts)} 条结果:\n")
        for i, p in enumerate(posts[:10], 1):
            print(f"  {i}. {p.get('title', '')[:40]}... [👍{p.get('likes')}]")

    elif args.stats:
        cli.view_stats()

    elif args.chat:
        cli.ai_chat()

    else:
        # 启动交互式界面
        cli.main_menu()


if __name__ == "__main__":
    main()
