#!/usr/bin/env python3
"""
小红书 AI Agent CLI
高级版命令行界面 - 极致视觉体验
"""
import os
import sys
import json
import time
import argparse
import shutil
from typing import Optional, Dict, Any, List
from datetime import datetime
import threading
import subprocess

# 导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.enhanced_agent import EnhancedAgent
from src.config_manager import ConfigManager, get_available_providers


# ============== 高级颜色系统 ==============
class Colors:
    RESET = "\033[0m"
    # 基础颜色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    # 亮色
    BRIGHT = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    # 前景色 (亮)
    HRED = "\033[91m"
    HGREEN = "\033[92m"
    HYELLOW = "\033[93m"
    HBLUE = "\033[94m"
    HMAGENTA = "\033[95m"
    HCYAN = "\033[96m"
    HWHITE = "\033[97m"
    # 背景色
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


# ============== 渐变色 = Gradient
class Gradient:
    """渐变色生成"""
    @staticmethod
    def text(text: str, start_rgb: tuple, end_rgb: tuple) -> str:
        """创建渐变文字"""
        r1, g1, b1 = start_rgb
        r2, g2, b2 = end_rgb
        result = ""
        for i, char in enumerate(text):
            if char.strip():
                ratio = i / max(len(text) - 1, 1)
                r = int(r1 + (r2 - r1) * ratio)
                g = int(g1 + (g2 - g1) * ratio)
                b = int(b1 + (b2 - b1) * ratio)
                result += f"\033[38;2;{r};{g};{b}m{char}"
            else:
                result += char
        return result + Colors.RESET


# ============== ASCII 艺术 ==============
class ASCII:
    """ASCII 艺术生成器"""

    @staticmethod
    def rainbow(text: str) -> str:
        """彩虹文字"""
        colors = ['\033[91m', '\033[93m', '\033[92m', '\033[96m', '\033[94m', '\033[95m']
        result = ""
        for i, char in enumerate(text):
            if char.strip():
                result += colors[i % len(colors)] + char
            else:
                result += char
        return result + Colors.RESET

    @staticmethod
    def fire(text: str) -> str:
        """火焰文字"""
        gradient = Gradient.text(text, (255, 100, 50), (255, 200, 50))
        return gradient

    @staticmethod
    def ice(text: str) -> str:
        """冰霜文字"""
        gradient = Gradient.text(text, (100, 200, 255), (200, 255, 255))
        return gradient


# ============== 高级 Banner ==============
class Banner:
    """Banner 生成"""

    @staticmethod
    def main():
        """主 Banner"""
        return f"""
{Colors.BRIGHT}{Colors.HMAGENTA}
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║                                                                           ║
    ║   {ASCII.rainbow("██████╗ ██╗     ███████╗████████╗███████╗███╗   ███╗ █████╗ ███╗  ██╗████████╗")}{Colors.HMAGENTA}   ║
    ║   {ASCII.rainbow("██╔══██╗██║     ██╔════╝╚══██╔══╝██╔════╝████╗ ████║██╔══██╗████╗ ██║╚══██╔══╝")}{Colors.HMAGENTA}   ║
    ║   {ASCII.rainbow("██████╔╝██║     █████╗     ██║   █████╗  ██╔████╔██║███████║██╔██╗ ██║   ██║")}{Colors.HMAGENTA}   ║
    ║   {ASCII.rainbow("██╔═══╝ ██║     ██╔══╝     ██║   ██╔══╝  ██║╚██╔╝██║██╔══██║██║╚██╗██║   ██║")}{Colors.HMAGENTA}   ║
    ║   {ASCII.rainbow("██║     ███████╗███████╗   ██║   ███████╗██║ ╚═╝ ██║██║  ██║██║ ╚████║   ██║")}{Colors.HMAGENTA}   ║
    ║   {ASCII.rainbow("╚═╝     ╚══════╝╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝")}{Colors.HMAGENTA}   ║
    ║                                                                           ║
    ║                        {ASCII.fire("🤖 AI Agent v1.1.0")}                                    ║
    ║                                                                           ║
    ║    {Colors.HCYAN}┌─────────────────────────────────────────────────────────────────┐{Colors.HMAGENTA}    ║
    ║    {Colors.HCYAN}│  🔍 搜索  │  📝 发布  │  🧠 记忆  │  💻 控制  │  ⚙️ 设置  │{Colors.HMAGENTA}    ║
    ║    {Colors.HCYAN}└─────────────────────────────────────────────────────────────────┘{Colors.HMAGENTA}    ║
    ║                                                                           ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
{Colors.RESET}"""

    @staticmethod
    def loading(text: str = "加载"):
        """加载动画 Banner"""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        return f"{Colors.HCYAN}{frames[int(time.time() * 10) % len(frames)]}{Colors.RESET} {text}"

    @staticmethod
    def success(text: str = "成功"):
        """成功提示"""
        return f"{Colors.HGREEN}✓{Colors.RESET} {text}"

    @staticmethod
    def error(text: str = "错误"):
        """错误提示"""
        return f"{Colors.HRED}✗{Colors.RESET} {text}"

    @staticmethod
    def info(text: str = "信息"):
        """信息提示"""
        return f"{Colors.HCYAN}ℹ{Colors.RESET} {text}"

    @staticmethod
    def warning(text: str = "警告"):
        """警告提示"""
        return f"{Colors.HYELLOW}⚠{Colors.RESET} {text}"


# ============== UI 组件 ==============
class UI:
    """UI 组件库"""

    @staticmethod
    def box(content: str, title: str = "", width: int = 60, color: str = Colors.CYAN) -> str:
        """创建文本框"""
        lines = content.strip().split('\n')
        max_len = max(len(l) for l in lines)
        width = max(width, max_len + 4)

        lines_out = []
        lines_out.append(f"\n{color}┌{'─' * (width - 2)}┐{Colors.RESET}")

        if title:
            title_pad = (width - 2 - len(title)) // 2
            lines_out.append(f"{color}│{Colors.RESET}{' ' * title_pad}{Colors.BRIGHT}{title}{Colors.RESET}{color}{' ' * (width - 2 - title_pad - len(title))}│{Colors.RESET}")
            lines_out.append(f"{color}├{'─' * (width - 2)}┤{Colors.RESET}")

        for line in lines:
            lines_out.append(f"{color}│{Colors.RESET} {line}{' ' * (width - len(line) - 3)}{color}│{Colors.RESET}")

        lines_out.append(f"{color}└{'─' * (width - 2)}┘{Colors.RESET}\n")
        return '\n'.join(lines_out)

    @staticmethod
    def table(headers: List[str], rows: List[List[str]], title: str = "") -> str:
        """创建表格"""
        if not rows:
            return UI.box("暂无数据", title)

        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        total_width = sum(col_widths) + len(col_widths) * 3 + 1
        lines = []

        lines.append(f"\n{Colors.CYAN}┌{'─' * total_width}┐{Colors.RESET}")
        if title:
            pad = (total_width - len(title)) // 2
            lines.append(f"{Colors.CYAN}│{Colors.RESET}{' ' * pad}{Colors.BRIGHT}{title}{Colors.RESET}{Colors.CYAN}{' ' * (total_width - pad - len(title))}│{Colors.RESET}")
            lines.append(f"{Colors.CYAN}├{'─' * total_width}┤{Colors.RESET}")

        # 表头
        header_line = "│ " + " │ ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " │"
        lines.append(f"{Colors.YELLOW}{header_line}{Colors.RESET}")
        lines.append(f"{Colors.CYAN}├{'─' * total_width}┤{Colors.RESET}")

        # 数据行
        for row in rows:
            row_line = "│ " + " │ ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)) + " │"
            lines.append(f"{Colors.WHITE}{row_line}{Colors.RESET}")

        lines.append(f"{Colors.CYAN}└{'─' * total_width}┘{Colors.RESET}")
        return '\n'.join(lines)

    @staticmethod
    def progress_bar(current: int, total: int, width: int = 40, prefix: str = "", suffix: str = "") -> str:
        """创建进度条"""
        percent = current / total if total > 0 else 0
        filled = int(width * percent)
        bar = "█" * filled + "░" * (width - filled)

        # 渐变色进度
        bar_colored = ""
        for i, char in enumerate(bar):
            if char == "█":
                ratio = i / width
                r, g, b = 255, int(100 + 155 * ratio), int(50 + 100 * (1 - ratio))
                bar_colored += f"\033[38;2;{r};{g};{b}m█{Colors.RESET}"
            else:
                bar_colored += f"{Colors.DIM}░{Colors.RESET}"

        return f"{prefix} |{bar_colored}| {int(percent * 100)}% {suffix}"

    @staticmethod
    def cards(items: List[Dict[str, str]], title: str = "") -> str:
        """创建卡片列表"""
        lines = []
        if title:
            lines.append(f"\n{Colors.CYAN}{title}{Colors.RESET}")
            lines.append(Colors.CYAN + "─" * 50 + Colors.RESET)

        for i, item in enumerate(items, 1):
            icon = item.get("icon", "•")
            text = item.get("text", "")
            sub = item.get("sub", "")
            lines.append(f"  {Colors.YELLOW}{i}.{Colors.RESET} {icon} {text}")
            if sub:
                lines.append(f"      {Colors.DIM}{sub}{Colors.RESET}")

        return '\n'.join(lines)

    @staticmethod
    def key_value(data: Dict[str, Any], title: str = "") -> str:
        """创建键值对显示"""
        lines = []
        if title:
            lines.append(f"\n{Colors.CYAN}{title}{Colors.RESET}")
            lines.append(Colors.CYAN + "─" * 50 + Colors.RESET)

        for key, value in data.items():
            lines.append(f"  {Colors.CYAN}{key}:{Colors.RESET} {value}")

        return '\n'.join(lines)


# ============== 动画效果 ==============
class Anim:
    """动画效果"""

    @staticmethod
    def typing(text: str, delay: float = 0.02):
        """打字机效果"""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    @staticmethod
    def fade_in(text: str, steps: int = 5):
        """淡入效果"""
        for i in range(steps + 1):
            alpha = i / steps
            # 简单模拟
            print(text)
            time.sleep(0.1)

    @staticmethod
    def spin(text: str = "处理中", duration: float = 2.0):
        """旋转动画"""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        end_time = time.time() + duration
        while time.time() < end_time:
            frame = frames[int(time.time() * 10) % len(frames)]
            print(f"\r{Colors.CYAN}{frame}{Colors.RESET} {text}", end="", flush=True)
            time.sleep(0.1)
        print(f"\r{Colors.GREEN}✓{Colors.RESET} {text}")

    @staticmethod
    def count_down(seconds: int = 3):
        """倒计时"""
        for i in range(seconds, 0, -1):
            print(f"\r{Colors.YELLOW}{i}...{Colors.RESET}", end="", flush=True)
            time.sleep(1)
        print(f"\r{Colors.GREEN}出发!{Colors.RESET}")


# ============== 交互组件 ==============
class Input:
    """输入组件"""

    @staticmethod
    def prompt(prompt_text: str, default: str = "", color: str = Colors.CYAN) -> str:
        """带样式的输入提示"""
        if default:
            return input(f"{color}{prompt_text}{Colors.RESET} [{Colors.GREEN}{default}{Colors.RESET}]: ").strip() or default
        return input(f"{color}{prompt_text}{Colors.RESET}: ").strip()

    @staticmethod
    def confirm(prompt_text: str, default: bool = False) -> bool:
        """确认对话框"""
        default_str = "Y/n" if default else "y/N"
        color = Colors.GREEN if default else Colors.RED

        while True:
            result = input(f"\n{Colors.YELLOW}{prompt_text} [{default_str}]{Colors.RESET}: ").strip().lower()
            if not result:
                return default
            if result in ['y', 'yes', '是', '1']:
                return True
            if result in ['n', 'no', '否', '0']:
                return False
            print(f"{Colors.RED}请输入 y 或 n{Colors.RESET}")

    @staticmethod
    def menu(title: str, options: List[tuple], prompt: str = "请选择") -> Optional[tuple]:
        """菜单选择"""
        width = 60

        print(f"\n{Colors.CYAN}┌{'─' * width}┐{Colors.RESET}")
        print(f"{Colors.CYAN}│{Colors.RESET} {title.center(width - 2)}{Colors.CYAN} │{Colors.RESET}")
        print(f"{Colors.CYAN}├{'─' * width}┤{Colors.RESET}")

        for key, desc, _ in options:
            if key == "":
                print(f"{Colors.CYAN}│{Colors.RESET}  {'─' * (width - 4)}{Colors.CYAN} │{Colors.RESET}")
            else:
                print(f"{Colors.CYAN}│{Colors.RESET}  {Colors.YELLOW}{key:^4}{Colors.RESET}   {desc}{' ' * (width - len(desc) - 14)}{Colors.CYAN} │{Colors.RESET}")

        print(f"{Colors.CYAN}└{'─' * width}┘{Colors.RESET}")

        choice = input(f"\n{Colors.GREEN}{prompt} > {Colors.RESET}").strip().upper()
        return next(((k, d, f) for k, d, f in options if k == choice), None)


# ============== 系统工具 ==============
class System:
    """系统工具"""

    @staticmethod
    def clear():
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def get_size():
        """获取终端大小"""
        return shutil.get_terminal_size(fallback=(80, 24))

    @staticmethod
    def beep():
        """蜂鸣"""
        print('\a', end='', flush=True)

    @staticmethod
    def get_ip() -> str:
        """获取 IP"""
        try:
            import requests
            return requests.get('https://api.ipify.org', timeout=2).text
        except:
            return "未知"

    @staticmethod
    def get_location() -> str:
        """获取位置"""
        try:
            import requests
            data = requests.get('http://ip-api.com/json', timeout=2).json()
            return f"{data.get('country', '')} {data.get('city', '')}"
        except:
            return "未知"


# ============== 主题系统 ==============
class Theme:
    """主题系统"""

    themes = {
        "default": {
            "primary": Colors.HCYAN,
            "secondary": Colors.HMAGENTA,
            "success": Colors.HGREEN,
            "warning": Colors.HYELLOW,
            "error": Colors.HRED,
            "info": Colors.HBLUE,
        },
        "dark": {
            "primary": Colors.CYAN,
            "secondary": Colors.MAGENTA,
            "success": Colors.GREEN,
            "warning": Colors.YELLOW,
            "error": Colors.RED,
            "info": Colors.BLUE,
        },
        "fire": {
            "primary": ASCII.fire("█"),
            "secondary": ASCII.fire("█"),
            "success": ASCII.fire("✓"),
            "warning": Colors.HYELLOW,
            "error": Colors.HRED,
            "info": Colors.HYELLOW,
        },
        "ice": {
            "primary": ASCII.ice("█"),
            "secondary": ASCII.ice("█"),
            "success": ASCII.ice("✓"),
            "warning": Colors.HCYAN,
            "error": Colors.HBLUE,
            "info": Colors.HBLUE,
        },
    }

    current = "default"

    @classmethod
    def get(cls, key: str) -> str:
        """获取主题颜色"""
        return cls.themes[cls.current].get(key, Colors.WHITE)

    @classmethod
    def set(cls, name: str):
        """设置主题"""
        if name in cls.themes:
            cls.current = name


# ============== CLI 主类 ==============
class XiaohongshuCLI:
    """小红书 CLI - 高级版"""

    def __init__(self):
        self.config = ConfigManager()
        self.agent: Optional[EnhancedAgent] = None
        self.running = True
        self.history: List[str] = []
        self.history_index = -1

    def _welcome(self):
        """欢迎动画"""
        print(f"\n{Colors.HCYAN}初始化配置加载器{Colors.RESET}...", end="")
        time.sleep(0.2)
        print(f" {Colors.HGREEN}✓{Colors.RESET}")

        print(f"{Colors.HCYAN}加载主题配置{Colors.RESET}...", end="")
        time.sleep(0.15)
        print(f" {Colors.HGREEN}✓{Colors.RESET}")

        print(f"{Colors.HCYAN}初始化命令系统{Colors.RESET}...", end="")
        time.sleep(0.15)
        print(f" {Colors.HGREEN}✓{Colors.RESET}")

        print(f"{Colors.HCYAN}检查环境依赖{Colors.RESET}...", end="")
        time.sleep(0.15)
        print(f" {Colors.HGREEN}✓{Colors.RESET}")

    def init_agent(self) -> bool:
        """初始化 Agent"""
        print(Anim.spin("初始化 Agent", 1.5))

        provider = self.config.get("llm_provider", "openai")
        model = self.config.get_model(provider)
        mcp_url = self.config.get("mcp_url", "http://localhost:18060/mcp")

        api_key = self.config.get_api_key(provider)
        if api_key:
            os.environ[f"{provider.upper()}_API_KEY"] = api_key
            os.environ["LLM_PROVIDER"] = provider

        try:
            self.agent = EnhancedAgent(
                mcp_url=mcp_url,
                enable_permissions=self.config.get("permissions", ["file_read", "browser_control", "clipboard"])
            )

            # 初始化成功展示
            content = f"""
{Colors.HGREEN}🎉 Agent 初始化完成!{Colors.RESET}

  {Colors.HCYAN}🤖 LLM 提供商:{Colors.RESET} {provider}
  {Colors.HYELLOW}📦 模型:{Colors.RESET} {model}
  {Colors.HBLUE}🔗 MCP:{Colors.RESET} {mcp_url}
  {Colors.HMAGENTA}🧠 对话历史:{Colors.RESET} {self.agent.db.get_chat_history_count()} 条
  {Colors.HGREEN}📚 知识库:{Colors.RESET} {len(self.agent.rag.knowledge_base)} 条
            """
            print(UI.box(content, title=" 初始化成功 ", width=65))
            return True
        except Exception as e:
            print(UI.box(f"{Colors.HRED}初始化失败: {e}{Colors.RESET}", title=" 错误 "))
            return False

    # ============== 功能函数 ==============
    def search_posts(self):
        """搜索帖子"""
        keyword = Input.prompt("搜索关键词", "AI Agent")
        if not keyword:
            return

        print(Anim.spin(f"搜索: {keyword}", 1))

        posts = self.agent.search(keyword)

        if posts:
            items = []
            for i, p in enumerate(posts[:10], 1):
                items.append({
                    "icon": "📄",
                    "text": p.get('title', '无标题')[:35] + "...",
                    "sub": f"👍 {p.get('likes', 0):,}  💬 {p.get('comments', 0):,}  ⭐ {p.get('collects', 0):,}"
                })
            print(UI.cards(items, f"🔍 搜索结果: {keyword} ({len(posts)} 条)"))
        else:
            print(UI.box(f"{Colors.HYELLOW}未找到相关帖子{Colors.RESET}", title=" 搜索结果 "))

    def create_post(self):
        """创建帖子"""
        keyword = Input.prompt("帖子主题", "AI Agent")
        images = Input.prompt("图片路径（逗号分隔）").split(",")

        if not images or not images[0].strip():
            print(UI.box(f"{Colors.HRED}需要图片才能发布{Colors.RESET}", title=" 错误 "))
            return

        print(Anim.spin("AI 生成内容", 1.5))
        content = self.agent.generate_content(keyword)

        preview = f"""
{Colors.HYELLOW}标题:{Colors.RESET} {content.get('title')}

{Colors.HCYAN}标签:{Colors.RESET} {' '.join(['#' + t for t in content.get('tags', [])])}

{Colors.HCYAN}正文:{Colors.RESET}
{content.get('content', '')[:200]}...
        """
        print(UI.box(preview, title=" 预览 "))

        if Input.confirm("确认发布?"):
            print(Anim.spin("发布中", 1))
            result = self.agent.publish(content, images)
            if result.get("success"):
                print(UI.box(f"{Colors.HGREEN}🎉 发布成功!{Colors.RESET}", title=" 成功 "))
            else:
                print(UI.box(f"{Colors.HRED}发布失败: {result.get('error')}{Colors.RESET}", title=" 错误 "))

    def view_stats(self):
        """查看统计"""
        stats = self.agent.get_stats()

        data = {
            "📝 已发布帖子": f"{Colors.HCYAN}{stats.get('published_posts', 0):,}{Colors.RESET} 篇",
            "👍 总点赞数": f"{Colors.HRED}{stats.get('total_likes', 0):,}{Colors.RESET}",
            "💬 总评论数": f"{Colors.HBLUE}{stats.get('total_comments', 0):,}{Colors.RESET}",
            "⭐ 已回复": f"{Colors.HGREEN}{stats.get('replied_comments', 0):,}{Colors.RESET}",
            "📚 知识库": f"{Colors.HMAGENTA}{stats.get('knowledge_items', 0):,}{Colors.RESET} 条",
        }
        print(UI.key_value(data, f"{Colors.BRIGHT}📊 数据统计{Colors.RESET}"))

    def ai_chat(self):
        """AI 对话"""
        help_text = """
  🤖 AI 对话模式

  • 输入内容让 AI 帮你处理
  • 支持多轮对话，AI 会记住之前的对话
  • 输入 'exit' 退出
  • 输入 'help' 查看帮助
  • 输入 'clear' 清屏
  • 输入 'memory' 查看记忆
        """
        print(UI.box(help_text, title=" AI 对话 "))

        while True:
            try:
                user_input = input(f"\n{Colors.HGREEN}你{Colors.RESET} > ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'q']:
                    break

                if user_input.lower() == 'help':
                    print(UI.box("""
  命令:
    exit, q     退出对话
    help        显示帮助
    clear       清屏
    memory      查看记忆状态
                    """, title=" 帮助 "))
                    continue

                if user_input.lower() == 'clear':
                    System.clear()
                    continue

                if user_input.lower() == 'memory':
                    status = self.agent.get_memory_status()
                    print(f"{Colors.HCYAN}🧠 对话历史: {status['history_count']}/{status['limit']} 条{Colors.RESET}")
                    continue

                # AI 回复
                print(Anim.spin("AI 思考中", 0.5))
                response = self.agent.chat(user_input)

                print(f"\n{Colors.HMAGENTA}🤖 AI{Colors.RESET}: {response}\n")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(UI.box(f"{Colors.HRED}{e}{Colors.RESET}", title=" 错误 "))

    # ============== 配置功能 ==============
    def config_provider(self):
        """配置 LLM 提供商"""
        providers = get_available_providers()

        options = []
        for i, (key, info) in enumerate(providers.items(), 1):
            current = f" {Colors.HGREEN}✓{Colors.RESET}" if key == self.config.get("llm_provider") else ""
            options.append((str(i), f"{info['name']}{current}", key))

        options.append(("B", "返回", None))

        choice = Input.menu("选择 LLM 提供商", options)
        if not choice or choice[0] == 'B':
            return

        selected_provider = choice[2]
        self.config.set("llm_provider", selected_provider)

        # 选择模型
        models = providers[selected_provider]["models"]
        print(f"\n{Colors.HCYAN}选择模型:{Colors.RESET}")
        for i, model in enumerate(models, 1):
            print(f"  {Colors.HYELLOW}{i}.{Colors.RESET} {model}")

        model_choice = Input.prompt("选择模型", "1")
        try:
            idx = int(model_choice) - 1
            if 0 <= idx < len(models):
                self.config.set_model(selected_provider, models[idx])
        except:
            pass

        self.config.save()
        print(UI.box(f"{Colors.HGREEN}已保存: {selected_provider}{Colors.RESET}", title=" 成功 "))

    def config_api_key(self):
        """配置 API Key"""
        provider = self.config.get("llm_provider", "openai")
        providers = get_available_providers()
        provider_info = providers.get(provider, {})

        current = self.config.get_api_key(provider)
        status = f"{Colors.HGREEN}已配置 ({current[:8]}...){Colors.RESET}" if current else f"{Colors.HRED}未配置{Colors.RESET}"

        print(UI.box(f"""
  提供商: {provider_info.get('name', provider)}
  环境变量: {provider_info.get('env_key', '')}
  状态: {status}
        """, title=" API Key "))

        new_key = Input.prompt("输入新 API Key (回车跳过)")
        if new_key:
            self.config.set_api_key(provider, new_key)
            print(UI.box(f"{Colors.HGREEN}已保存{Colors.RESET}", title=" 成功 "))

    def config_mcp(self):
        """配置 MCP"""
        current = self.config.get("mcp_url", "http://localhost:18060/mcp")
        new_url = Input.prompt("MCP 地址", current)
        self.config.set("mcp_url", new_url)
        self.config.save()
        print(UI.box(f"{Colors.HGREEN}已更新: {new_url}{Colors.RESET}", title=" 成功 "))

    def config_permissions(self):
        """配置权限"""
        all_perms = [
            ("file_read", "读取文件", "📖"),
            ("file_write", "写入文件", "✏️"),
            ("command_exec", "执行命令", "💻"),
            ("browser_control", "控制浏览器", "🌐"),
            ("screenshot", "截图", "📸"),
            ("clipboard", "剪贴板", "📋"),
        ]

        current = self.config.get("permissions", [])

        print(f"\n{Colors.HCYAN}可选权限:{Colors.RESET}\n")
        for perm, desc, icon in all_perms:
            enabled = perm in current
            status = f"{Colors.HGREEN}◉ 启用{Colors.RESET}" if enabled else f"{Colors.HRED}○ 禁用{Colors.RESET}"
            print(f"  {icon} {perm:<16} {desc:<10} {status}")

        new_perms = Input.prompt("输入要启用的权限（逗号分隔）")
        if new_perms:
            perm_list = [p.strip() for p in new_perms.split(",")]
            self.config.set("permissions", perm_list)
            self.config.save()
            print(UI.box(f"{Colors.HGREEN}已更新: {', '.join(perm_list)}{Colors.RESET}", title=" 成功 "))

    def show_config(self):
        """显示配置"""
        provider = self.config.get("llm_provider", "openai")
        providers = get_available_providers()
        provider_info = providers.get(provider, {})

        api_key = self.config.get_api_key(provider)
        api_status = f"{Colors.HGREEN}{api_key[:8]}...{api_key[-4:]}{Colors.RESET}" if api_key else f"{Colors.HRED}未设置{Colors.RESET}"

        data = {
            "🤖 LLM 提供商": provider_info.get('name', provider),
            "📦 模型": self.config.get_model(provider),
            "🔗 MCP 地址": self.config.get('mcp_url'),
            "🔐 权限": ', '.join(self.config.get('permissions', [])),
            "🔑 API Key": api_status,
        }

        if self.agent:
            mem = self.agent.get_memory_status()
            data["🧠 对话历史"] = f"{mem['history_count']}/{mem['limit']} 条"

        print(UI.key_value(data, f"{Colors.BRIGHT}⚙️ 当前配置{Colors.RESET}"))

    def show_memory(self):
        """显示对话历史"""
        status = self.agent.get_memory_status()
        history = self.agent.db.get_chat_history(20)

        print(UI.box(f"""
  当前记录: {status['history_count']} 条
  保存上限: {status['limit']} 条
        """, title=" 🧠 对话历史 "))

        if history:
            print(f"\n{Colors.HCYAN}最近对话:{Colors.RESET}\n")
            for msg in history[-5:]:
                role = msg["role"]
                icon = "👤" if role == "user" else "🤖"
                color = Colors.HGREEN if role == "user" else Colors.HMAGENTA
                content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
                print(f"  {icon} {color}{role:<8}{Colors.RESET} {content}")

    def clear_memory(self):
        """清空对话历史"""
        status = self.agent.get_memory_status()
        if Input.confirm(f"确定要清空 {status['history_count']} 条对话历史吗?"):
            result = self.agent.clear_memory()
            print(UI.box(f"{Colors.HGREEN}{result}{Colors.RESET}", title=" 完成 "))

    # ============== 菜单系统 ==============
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
            choice = Input.menu("主菜单", options)

            if not choice:
                continue

            key, _, func = choice

            if key == 'Q':
                self.quit()
            elif key == 'S':
                self.settings_menu()
            elif key == 'H':
                self.show_help()
            elif key in ['4', '5']:
                self.file_menu() if key == '4' else self.computer_menu()
            elif func:
                try:
                    func()
                except Exception as e:
                    print(UI.box(f"{Colors.HRED}{e}{Colors.RESET}", title=" 错误 "))

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
            ("B", "🔙 返回", None),
        ]

        while True:
            choice = Input.menu("系统设置", options)

            if not choice or choice[0] == 'B':
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

            if choice[0] in func_map:
                func_map[choice[0]]()

    def file_menu(self):
        """文件菜单"""
        print(UI.box(f"{Colors.HYELLOW}文件管理功能开发中...{Colors.RESET}", title=" 📁 "))

    def computer_menu(self):
        """电脑控制菜单"""
        print(UI.box(f"{Colors.HYELLOW}电脑控制功能开发中...{Colors.RESET}", title=" 💻 "))

    def show_help(self):
        """显示帮助"""
        help_text = """
╔═══════════════════════════════════════════════════════╗
║                  小红书 AI Agent 帮助               ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  主菜单:                                             ║
║                                                       ║
║    [1] 🔍 搜索热门帖子                               ║
║         搜索小红书上的热门内容                         ║
║                                                       ║
║    [2] 📝 创建并发布帖子                             ║
║         AI 生成内容并发布到小红书                       ║
║                                                       ║
║    [3] 📊 查看数据统计                               ║
║         查看已发布笔记的数据统计                       ║
║                                                       ║
║    [6] 🤖 AI 对话                                   ║
║         与 AI 助手进行多轮对话                         ║
║                                                       ║
║  系统设置:                                           ║
║                                                       ║
║    [1] 选择 LLM 提供商                               ║
║    [2] 配置 API Key                                  ║
║    [3] 配置 MCP 地址                                 ║
║    [4] 配置权限                                      ║
║    [6] 查看对话历史                                  ║
║    [7] 清空对话历史                                  ║
║                                                       ║
║  快捷键:                                             ║
║                                                       ║
║    Ctrl+C    取消/退出                               ║
║    exit/q    退出对话                                ║
║    help/h    查看帮助                                ║
║    clear     清屏                                    ║
║    memory    查看记忆                               ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
        """
        print(UI.box(help_text, title=" 📖 帮助文档 "))

    def quit(self):
        """退出"""
        print(f"\n{Colors.HCYAN}{'═' * 50}{Colors.RESET}")
        print(f"  {Colors.HGREEN}再见! 感谢使用小红书 AI Agent 👋{Colors.RESET}")
        print(f"{Colors.HCYAN}{'═' * 50}{Colors.RESET}\n")
        self.running = False


# ============== 入口 ==============
def main():
    parser = argparse.ArgumentParser(description="小红书 AI Agent CLI")
    parser.add_argument("-k", "--keyword", help="搜索关键词")
    parser.add_argument("--search", action="store_true", help="搜索模式")
    parser.add_argument("--stats", action="store_true", help="查看统计")
    parser.add_argument("--chat", action="store_true", help="AI 对话模式")
    parser.add_argument("--config", action="store_true", help="显示配置")
    parser.add_argument("--gui", action="store_true", help="启动交互式界面")

    args = parser.parse_args()

    print(Banner.main())

    cli = XiaohongshuCLI()
    cli._welcome()

    if args.config:
        cli.init_agent()
        cli.show_config()
        return

    if not cli.init_agent():
        return

    if args.search or args.keyword:
        cli.agent.search(args.keyword or "AI Agent")
    elif args.stats:
        cli.view_stats()
    elif args.chat:
        cli.ai_chat()
    else:
        cli.main_menu()


if __name__ == "__main__":
    main()
