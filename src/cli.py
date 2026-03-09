#!/usr/bin/env python3
"""
小红书 AI Agent CLI
交互式命令行界面
"""
import os
import sys
import json
import time
import argparse
from typing import Optional, Dict, Any, List

# 导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.enhanced_agent import EnhancedAgent
from src.config_manager import ConfigManager, get_available_providers


# ============== 颜色 ==============
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"


# ============== 界面 ==============
def print_banner():
    """打印横幅"""
    print(f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       🤖 小红书 AI Agent CLI v1.0                          ║
║                                                              ║
║       支持: 搜索 | 发布 | 电脑控制 | AI 对话                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{Colors.RESET}
    """)


def print_menu(title: str, options: List[tuple]):
    """打印菜单"""
    print(f"\n{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{title.center(60)}{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")

    for key, desc, _ in options:
        print(f"  {Colors.YELLOW}[{key}]{Colors.RESET}  {desc}")

    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")


def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")


def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")


def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")


def input_text(prompt: str, default: str = "") -> str:
    """带默认值的输入"""
    if default:
        result = input(f"{Colors.CYAN}{prompt}{Colors.RESET} [{default}]: ").strip()
        return result if result else default
    return input(f"{Colors.CYAN}{prompt}{Colors.RESET}: ").strip()


def input_password(prompt: str) -> str:
    """密码输入"""
    import getpass
    return getpass.getpass(f"{Colors.CYAN}{prompt}{Colors.RESET}: ")


def confirm(prompt: str) -> bool:
    """确认"""
    while True:
        result = input(f"{Colors.YELLOW}{prompt} (y/n): {Colors.RESET}").strip().lower()
        if result in ['y', 'yes', '是', '1']:
            return True
        elif result in ['n', 'no', '否', '0']:
            return False


# ============== CLI ==============
class XiaohongshuCLI:
    """小红书 CLI"""

    def __init__(self):
        self.config = ConfigManager()
        self.agent: Optional[EnhancedAgent] = None
        self.running = True

    def init_agent(self):
        """初始化 Agent"""
        print_info("初始化 Agent...")

        # 获取配置
        provider = self.config.get("llm_provider", "openai")
        model = self.config.get_model(provider)
        mcp_url = self.config.get("mcp_url", "http://localhost:18060/mcp")

        # 设置环境变量
        api_key = self.config.get_api_key(provider)
        if api_key:
            os.environ[f"{provider.upper()}_API_KEY"] = api_key
            os.environ["LLM_PROVIDER"] = provider

        try:
            self.agent = EnhancedAgent(
                mcp_url=mcp_url,
                enable_permissions=self.config.get("permissions", ["file_read", "browser_control", "clipboard"])
            )
            print_success("Agent 初始化完成")
            print(f"   提供商: {provider}")
            print(f"   模型: {model}")
            return True
        except Exception as e:
            print_error(f"初始化失败: {e}")
            return False

    # ============== 配置功能 ==============
    def config_provider(self):
        """配置 LLM 提供商"""
        print(f"\n{Colors.CYAN}选择 LLM 提供商:{Colors.RESET}\n")

        providers = get_available_providers()
        for i, (key, info) in enumerate(providers.items(), 1):
            current = " ✓" if key == self.config.get("llm_provider") else ""
            print(f"  {Colors.YELLOW}{i}.{Colors.RESET} {info['name']}{current}")

        print()

        try:
            choice = int(input_text("选择提供商", "1"))
            provider_keys = list(providers.keys())
            if 1 <= choice <= len(provider_keys):
                selected_provider = provider_keys[choice - 1]
                self.config.set("llm_provider", selected_provider)

                # 选择模型
                print(f"\n{Colors.CYAN}选择模型:{Colors.RESET}\n")
                models = providers[selected_provider]["models"]
                for i, model in enumerate(models, 1):
                    print(f"  {Colors.YELLOW}{i}.{Colors.RESET} {model}")

                model_choice = int(input_text("选择模型", "1"))
                if 1 <= model_choice <= len(models):
                    selected_model = models[model_choice - 1]
                    self.config.set_model(selected_provider, selected_model)

                self.config.save()
                print_success(f"已保存配置: {selected_provider} - {selected_model}")
            else:
                print_error("无效选择")
        except ValueError:
            print_error("请输入数字")

    def config_api_key(self):
        """配置 API Key"""
        providers = get_available_providers()
        provider = self.config.get("llm_provider", "openai")
        provider_info = providers.get(provider, {})

        print(f"\n{Colors.CYAN}配置 API Key{Colors.RESET}")
        print(f"  当前提供商: {provider_info.get('name', provider)}")
        print(f"  环境变量: {provider_info.get('env_key', '')}")
        print()

        # 显示当前状态
        current_key = self.config.get_api_key(provider)
        if current_key:
            masked = current_key[:8] + "..." + current_key[-4:] if len(current_key) > 12 else "***"
            print(f"  当前: {masked}")
        else:
            env_key = provider_info.get("env_key", "")
            if os.getenv(env_key):
                print(f"  当前: 已设置 (环境变量)")
            else:
                print(f"  当前: {Colors.RED}未设置{Colors.RESET}")

        print()

        # 输入新 Key
        print("  输入新的 API Key (直接回车跳过):")
        new_key = input("  > ").strip()

        if new_key:
            self.config.set_api_key(provider, new_key)
            print_success("API Key 已保存")
        else:
            print_info("保留原配置")

    def config_mcp(self):
        """配置 MCP"""
        current = self.config.get("mcp_url", "http://localhost:18060/mcp")
        print(f"\n{Colors.CYAN}配置 MCP 地址{Colors.RESET}")
        print(f"  当前: {current}")

        new_url = input_text("新地址", current)
        self.config.set("mcp_url", new_url)
        self.config.save()
        print_success("MCP 地址已保存")

    def config_permissions(self):
        """配置权限"""
        print(f"\n{Colors.CYAN}配置权限{Colors.RESET}\n")

        all_perms = [
            ("file_read", "读取文件"),
            ("file_write", "写入文件"),
            ("command_exec", "执行命令"),
            ("browser_control", "控制浏览器"),
            ("screenshot", "截图"),
            ("clipboard", "剪贴板"),
        ]

        current_perms = self.config.get("permissions", [])

        for perm, desc in all_perms:
            enabled = perm in current_perms
            status = f"{Colors.GREEN}✓{Colors.RESET}" if enabled else f"{Colors.RED}✗{Colors.RESET}"
            print(f"  {status} {perm:<20} {desc}")

        print("\n  输入要启用的权限（逗号分隔）:")
        new_perms = input("  > ").strip()

        if new_perms:
            perm_list = [p.strip() for p in new_perms.split(",")]
            self.config.set("permissions", perm_list)
            self.config.save()
            print_success("权限已保存")

    def show_config(self):
        """显示当前配置"""
        provider = self.config.get("llm_provider", "openai")
        providers = get_available_providers()
        provider_info = providers.get(provider, {})

        print(f"\n{Colors.CYAN}📋 当前配置{Colors.RESET}")
        print(f"  LLM 提供商:  {provider_info.get('name', provider)}")
        print(f"  模型:        {self.config.get_model(provider)}")
        print(f"  MCP 地址:    {self.config.get('mcp_url')}")
        print(f"  权限:        {', '.join(self.config.get('permissions', []))}")

        # API Key 状态
        api_key = self.config.get_api_key(provider)
        env_key = provider_info.get("env_key", "")

        if api_key:
            print(f"  API Key:     {api_key[:8]}...{api_key[-4:]}")
        elif os.getenv(env_key):
            print(f"  API Key:     (环境变量)")
        else:
            print(f"  API Key:     {Colors.RED}未设置{Colors.RESET}")

    # ============== 小红书功能 ==============
    def search_posts(self):
        """搜索帖子"""
        keyword = input_text("搜索关键词", "AI Agent")
        if not keyword:
            return

        print_info(f"搜索中: {keyword}...")
        posts = self.agent.search(keyword)

        if posts:
            print(f"\n{Colors.GREEN}找到 {len(posts)} 条结果:{Colors.RESET}\n")
            for i, p in enumerate(posts[:10], 1):
                title = p.get("title", "无标题")[:35]
                likes = p.get("likes", 0)
                comments = p.get("comments", 0)
                collects = p.get("collects", 0)
                print(f"  {Colors.CYAN}{i:2}.{Colors.RESET} {title}...")
                print(f"      👍 {likes}  💬 {comments}  ⭐ {collects}")
                print()
        else:
            print_error("未找到结果")

    def create_post(self):
        """创建并发布帖子"""
        keyword = input_text("帖子主题", "AI Agent")

        images_input = input_text("图片路径（逗号分隔）", "")
        images = [img.strip() for img in images_input.split(",") if img.strip()]

        if not images:
            print_error("需要图片才能发布")
            return

        print_info("生成内容...")
        content = self.agent.generate_content(keyword)

        print(f"\n{Colors.GREEN}生成内容:{Colors.RESET}")
        print(f"  标题: {content.get('title')}")
        print(f"  标签: {' '.join(['#' + t for t in content.get('tags', [])])}")

        if confirm("\n确认发布?"):
            result = self.agent.publish(content, images)
            if result.get("success"):
                print_success("发布成功!")
            else:
                print_error(f"发布失败: {result.get('error')}")

    def view_stats(self):
        """查看统计"""
        stats = self.agent.get_stats()

        print(f"\n{Colors.CYAN}📊 数据统计{Colors.RESET}")
        print(f"  已发布帖子: {stats.get('published_posts', 0)}")
        print(f"  总点赞数:   {stats.get('total_likes', 0)}")
        print(f"  总评论数:   {stats.get('total_comments', 0)}")
        print(f"  已回复:     {stats.get('replied_comments', 0)}")
        print(f"  知识库:     {stats.get('knowledge_items', 0)}")

    # ============== 电脑控制功能 ==============
    def list_files(self):
        """列文件"""
        path = input_text("目录路径", os.path.expanduser("~/Desktop"))

        result = self.agent.list_files(path)

        if result.get("success"):
            items = result.get("items", [])
            print(f"\n{Colors.CYAN}📁 {result.get('path')}{Colors.RESET}")
            print(f"  共 {len(items)} 个项目\n")

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

    def execute_command(self):
        """执行命令"""
        if not self.agent.computer.security.permissions.has_permission("command_exec"):
            print_error("没有命令执行权限")
            return

        command = input_text("命令")

        print_info("执行中...")
        result = self.agent.execute_command(command)

        if result.get("success"):
            print(f"\n{Colors.GREEN}输出:{Colors.RESET}")
            print(result.get("stdout", "")[:2000])
        else:
            print_error(f"错误: {result.get('error')}")

    def open_browser(self):
        """打开浏览器"""
        url = input_text("网址", "https://www.xiaohongshu.com")

        result = self.agent.open_browser(url)

        if result.get("success"):
            print_success(f"已打开: {url}")
        else:
            print_error(f"错误: {result.get('error')}")

    def take_screenshot(self):
        """截图"""
        result = self.agent.take_screenshot()

        if result.get("success"):
            print_success(f"截图保存到: {result.get('path')}")
        else:
            print_error(f"错误: {result.get('error')}")

    def clipboard_oper(self, write: bool = False):
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
                print(f"\n{Colors.CYAN}剪贴板内容:{Colors.RESET}")
                print(result.get("content", "")[:500])
        else:
            print_error(f"错误: {result.get('error')}")

    def send_notification(self):
        """发送通知"""
        title = input_text("标题", "AI Agent")
        message = input_text("消息内容")

        result = self.agent.send_notification(title, message)

        if result.get("success"):
            print_success("通知已发送")
        else:
            print_error(f"错误: {result.get('error')}")

    def speak_text(self):
        """语音播报"""
        text = input_text("要朗读的内容")

        result = self.agent.speak(text)

        if result.get("success"):
            print_success("正在朗读...")
        else:
            print_error(f"错误: {result.get('error')}")

    def system_info(self):
        """系统信息"""
        result = self.agent.get_system_info()
        info = result.get("info", {})

        print(f"\n{Colors.CYAN}💻 系统信息{Colors.RESET}")
        print(f"  平台:     {info.get('platform')}")
        print(f"  Python:  {info.get('python_version', '')[:15]}")
        print(f"  用户:     {info.get('user')}")
        print(f"  当前目录: {info.get('cwd')}")

        perms = self.agent.get_permissions()["permissions"]
        print(f"\n{Colors.CYAN}🔐 权限状态{Colors.RESET}")
        for p, v in perms.items():
            status = f"{Colors.GREEN}✓{Colors.RESET}" if v else f"{Colors.RED}✗{Colors.RESET}"
            print(f"  {p:<20} {status}")

    # ============== AI 对话 ==============
    def ai_chat(self):
        """AI 对话"""
        print(f"\n{Colors.MAGENTA}🤖 AI 对话模式{Colors.RESET}")
        print("  输入内容让 AI 帮你处理")
        print("  输入 'exit' 或 'q' 退出\n")

        while True:
            try:
                user_input = input(f"{Colors.GREEN}你>{Colors.RESET} ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'q', 'quit']:
                    break

                response = self.agent.chat(user_input)

                print(f"\n{Colors.CYAN}AI:{Colors.RESET} {response}\n")

            except KeyboardInterrupt:
                print()
                break
            except Exception as e:
                print_error(f"错误: {e}")

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
            ("S", "⚙️ 设置", self.settings_menu),
            ("Q", "🚪 退出", self.quit),
        ]

        while self.running:
            print_menu("主菜单", options)
            choice = input(f"\n{Colors.GREEN}请选择 > {Colors.RESET}").strip().upper()

            if choice == 'Q':
                self.quit()
            elif choice == 'S':
                self.settings_menu()
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
            else:
                for key, _, func in options:
                    if choice == key and func:
                        try:
                            func()
                        except Exception as e:
                            print_error(f"错误: {e}")

    def read_file(self):
        """读文件"""
        path = input_text("文件路径")
        result = self.agent.read_file(path)

        if result.get("success"):
            print(f"\n{Colors.CYAN}📄 {path}{Colors.RESET}")
            print(f"  大小: {result.get('size')} bytes\n")
            content = result.get("content", "")
            lines = content.split("\n")
            for i, line in enumerate(lines[:50]):
                print(f"  {i+1:4}: {line[:80]}")
            if len(lines) > 50:
                print(f"\n  ... 共 {len(lines)} 行")
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
            else:
                for key, _, func in options:
                    if choice == key and func:
                        try:
                            func()
                        except Exception as e:
                            print_error(f"错误: {e}")

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
            elif choice == '1':
                self.config_provider()
            elif choice == '2':
                self.config_api_key()
            elif choice == '3':
                self.config_mcp()
            elif choice == '4':
                self.config_permissions()
            elif choice == '5':
                self.show_config()
            elif choice == '6':
                self.show_memory()
            elif choice == '7':
                self.clear_memory()

    def show_memory(self):
        """显示对话历史"""
        status = self.agent.get_memory_status()
        print(f"\n{Colors.CYAN}🧠 对话历史{Colors.RESET}")
        print(f"  当前记录: {status['history_count']} 条")
        print(f"  保存上限: {status['limit']} 条")

        history = self.agent.db.get_chat_history(20)
        if history:
            print(f"\n{Colors.CYAN}最近对话:{Colors.RESET}")
            for i, msg in enumerate(history[-10:], 1):
                role_icon = "👤" if msg["role"] == "user" else "🤖"
                content = msg["content"][:80] + "..." if len(msg["content"]) > 80 else msg["content"]
                print(f"  {role_icon} {msg['role']}: {content}")
        else:
            print(f"\n  暂无对话历史")

    def clear_memory(self):
        """清空对话历史"""
        if confirm("确定要清空所有对话历史吗？"):
            result = self.agent.clear_memory()
            print_success(result)

    def quit(self):
        """退出"""
        print(f"\n{Colors.CYAN}再见! 👋{Colors.RESET}\n")
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

    print_banner()

    # 创建 CLI
    cli = XiaohongshuCLI()

    # 显示配置
    if args.config:
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
