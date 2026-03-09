#!/usr/bin/env python3
"""
终端 UI - 交互式命令行界面
"""
import os
import sys
import json
import readline
from typing import Optional, List
from datetime import datetime


# ============== 颜色和样式 ==============
class Colors:
    """终端颜色"""
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"


# ============== 菜单系统 ==============
class Menu:
    """菜单系统"""

    def __init__(self, title: str, options: List[tuple] = None):
        self.title = title
        self.options = options or []
        self.running = True

    def add_option(self, key: str, desc: str, callback):
        """添加选项"""
        self.options.append((key, desc, callback))

    def show(self):
        """显示菜单"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{self.title.center(50)}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")

        for key, desc, _ in self.options:
            print(f"  {Colors.YELLOW}[{key}]{Colors.RESET} {desc}")

        print(f"{Colors.CYAN}{'=' * 50}{Colors.RESET}\n")

    def run(self):
        """运行菜单"""
        while self.running:
            self.show()
            choice = input(f"{Colors.GREEN}请选择 > {Colors.RESET}").strip()

            if choice.lower() == 'q' or choice.lower() == 'exit':
                self.running = False
                print(f"\n{Colors.CYAN}再见！👋{Colors.RESET}\n")
                break

            # 查找并执行回调
            for key, desc, callback in self.options:
                if choice == key:
                    try:
                        callback()
                    except Exception as e:
                        print(f"\n{Colors.RED}错误: {e}{Colors.RESET}")
                    break
            else:
                if choice:
                    print(f"\n{Colors.RED}无效选择，请重试{Colors.RESET}\n")


# ============== 交互式输入 ==============
def input_with_default(prompt: str, default: str = "") -> str:
    """带默认值的输入"""
    if default:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default
    return input(f"{prompt}: ").strip()


def confirm(prompt: str) -> bool:
    """确认提示"""
    while True:
        result = input(f"{prompt} (y/n): ").strip().lower()
        if result in ['y', 'yes', '是', '1']:
            return True
        elif result in ['n', 'no', '否', '0']:
            return False


def select_option(options: List[str], prompt: str = "请选择") -> int:
    """选择选项"""
    print(f"\n{prompt}:")
    for i, opt in enumerate(options, 1):
        print(f"  {Colors.YELLOW}[{i}]{Colors.RESET} {opt}")

    while True:
        try:
            choice = int(input(f"\n{prompt} > "))
            if 1 <= choice <= len(options):
                return choice - 1
        except ValueError:
            pass
        print(f"{Colors.RED}无效选择，请重试{Colors.RESET}")


# ============== 显示函数 ==============
def print_header(title: str):
    """打印标题"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}")
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print(f"{Colors.RESET}")


def print_success(msg: str):
    """打印成功消息"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")


def print_error(msg: str):
    """打印错误消息"""
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")


def print_warning(msg: str):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")


def print_info(msg: str):
    """打印信息"""
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")


def print_table(headers: List[str], rows: List[List[str]]):
    """打印表格"""
    # 计算列宽
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    # 打印表头
    print()
    for i, h in enumerate(headers):
        print(f"  {h.ljust(col_widths[i])}", end=" | ")
    print()

    # 分隔线
    for w in col_widths:
        print("-" * (w + 2), end="-+-")
    print()

    # 打印数据
    for row in rows:
        for i, cell in enumerate(row):
            print(f"  {str(cell).ljust(col_widths[i])}", end=" | ")
        print()
    print()


def print_dict(data: dict, indent: int = 2):
    """打印字典"""
    for key, value in data.items():
        print(f"{' ' * indent}{Colors.YELLOW}{key}:{Colors.RESET} {value}")


# ============== 进度条 ==============
def progress_bar(current: int, total: int, prefix: str = "", length: int = 40):
    """显示进度条"""
    percent = current / total
    filled = int(length * percent)
    bar = "█" * filled + "░" * (length - filled)

    sys.stdout.write(f"\r{prefix} [{bar}] {percent * 100:.1f}% ")
    sys.stdout.flush()

    if current >= total:
        print()


# ============== 分页显示 ==============
def paginate(items: List, page_size: int = 10, formatter=None):
    """分页显示"""
    total_pages = (len(items) + page_size - 1) // page_size
    current_page = 1

    while True:
        start = (current_page - 1) * page_size
        end = start + page_size
        page_items = items[start:end]

        print(f"\n{Colors.CYAN}--- 第 {current_page}/{total_pages} 页 ---{Colors.RESET}\n")

        for i, item in enumerate(page_items, start + 1):
            if formatter:
                formatter(i, item)
            else:
                print(f"  {i}. {item}")

        if current_page >= total_pages:
            break

        print(f"\n{Colors.YELLOW}[N] 下一页 [P] 上一页 [Q] 退出{Colors.RESET}")
        choice = input("选择 > ").strip().lower()

        if choice == 'n' and current_page < total_pages:
            current_page += 1
        elif choice == 'p' and current_page > 1:
            current_page -= 1
        elif choice == 'q':
            break


# ============== AI 对话界面 ==============
class TerminalChat:
    """终端对话界面"""

    def __init__(self, agent):
        self.agent = agent
        self.history = []

    def run(self):
        """运行对话"""
        print_header("🤖 AI Agent 对话模式")
        print("输入您的需求，按 Enter 发送")
        print("输入 'exit' 或 'q' 退出对话")
        print("输入 'clear' 清除历史\n")

        while True:
            try:
                user_input = input(f"\n{Colors.GREEN}你: {Colors.RESET}").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'q', 'quit']:
                    print(f"\n{Colors.CYAN}再见！👋{Colors.RESET}\n")
                    break

                if user_input.lower() == 'clear':
                    self.history = []
                    print(f"{Colors.YELLOW}历史已清除{Colors.RESET}")
                    continue

                # 添加到历史
                self.history.append({"role": "user", "content": user_input})

                # 调用 AI
                print(f"\n{Colors.CYAN}AI: {Colors.RESET}思考中...")

                response = self.agent.chat(user_input)

                # 显示响应
                print(f"\n{Colors.CYAN}AI:{Colors.RESET} {response}")

                # 添加到历史
                self.history.append({"role": "assistant", "content": response})

            except KeyboardInterrupt:
                print(f"\n\n{Colors.CYAN}再见！👋{Colors.RESET}\n")
                break
            except Exception as e:
                print(f"\n{Colors.RED}错误: {e}{Colors.RESET}")


# ============== 主界面 ==============
class AgentInterface:
    """Agent 主界面"""

    def __init__(self, agent):
        self.agent = agent

    def main_menu(self):
        """主菜单"""
        menu = Menu("🤖 小红书 AI Agent 系统", [
            ("1", "🔍 搜索热门帖子", self.search_posts),
            ("2", "📝 生成内容并发布", self.create_and_publish),
            ("3", "💬 自动回复评论", self.auto_reply),
            ("4", "📊 查看数据统计", self.show_stats),
            ("5", "💾 知识库管理", self.manage_knowledge),
            ("6", "⚙️ 设置", self.settings),
            ("7", "🧪 测试 LLM", self.test_llm),
            ("Q", "退出", lambda: sys.exit(0)),
        ])
        menu.run()

    def search_posts(self):
        """搜索帖子"""
        print_header("🔍 搜索热门帖子")

        keyword = input_with_default("请输入搜索关键词", "AI Agent")

        print(f"\n{Colors.CYAN}搜索中...{Colors.RESET}")
        results = self.agent.search(keyword)

        if results:
            print(f"\n{Colors.GREEN}找到 {len(results)} 条结果:{Colors.RESET}\n")
            for i, post in enumerate(results[:10], 1):
                title = post.get("title", "无标题")[:40]
                likes = post.get("likes", 0)
                comments = post.get("comments", 0)
                collects = post.get("collects", 0)
                print(f"  {i}. {title}")
                print(f"     👍 {likes} | 💬 {comments} | ⭐ {collects}")
                print()
        else:
            print(f"{Colors.YELLOW}未找到结果{Colors.RESET}")

    def create_and_publish(self):
        """创建并发布"""
        print_header("📝 生成内容并发布")

        keyword = input_with_default("请输入主题关键词", "AI Agent")

        # 获取图片
        images_input = input_with_default("请输入图片路径（逗号分隔，可留空）", "")
        images = [img.strip() for img in images_input.split(",") if img.strip()]

        print(f"\n{Colors.CYAN}生成内容...{Colors.RESET}")
        content = self.agent.generate_content(keyword)

        if content:
            print(f"\n{Colors.GREEN}生成内容:{Colors.RESET}")
            print(f"\n标题: {content.get('title')}")
            print(f"\n内容: {content.get('content')[:200]}...")
            print(f"\n标签: {' '.join(['#' + t for t in content.get('tags', [])])}")

            if images and confirm("\n确认发布？"):

                result = self.agent.publish(content, images)

                if result.get("success"):
                    print_success("发布成功！")
                else:
                    print_error(f"发布失败: {result.get('error')}")
            else:
                print_warning("已保存内容草稿")

    def auto_reply(self):
        """自动回复"""
        print_header("💬 自动回复评论")

        if confirm("确认执行自动回复？"):

            print(f"\n{Colors.CYAN}获取评论并回复...{Colors.RESET}")

            result = self.agent.auto_reply_comments()

            if result.get("replied_count", 0) > 0:
                print_success(f"已回复 {result.get('replied_count')} 条评论")
            else:
                print_warning("没有需要回复的评论")

    def show_stats(self):
        """显示统计"""
        print_header("📊 数据统计")

        stats = self.agent.get_stats()

        print()
        print(f"  {Colors.CYAN}已发布帖子:{Colors.RESET} {stats.get('published_posts', 0)} 篇")
        print(f"  {Colors.CYAN}总点赞数:{Colors.RESET} {stats.get('total_likes', 0)}")
        print(f"  {Colors.CYAN}总评论数:{Colors.RESET} {stats.get('total_comments', 0)}")
        print(f"  {Colors.CYAN}已回复评论:{Colors.RESET} {stats.get('replied_comments', 0)}")
        print(f"  {Colors.CYAN}知识库条目:{Colors.RESET} {stats.get('knowledge_items', 0)}")
        print()

    def manage_knowledge(self):
        """知识库管理"""
        print_header("💾 知识库管理")

        menu = Menu("知识库管理", [
            ("1", "查看知识库", self.view_knowledge),
            ("2", "添加知识", self.add_knowledge),
            ("3", "导出知识库", self.export_knowledge),
            ("4", "导入知识库", self.import_knowledge),
            ("B", "返回主菜单", lambda: None),
        ])
        menu.run()

    def view_knowledge(self):
        """查看知识库"""
        knowledge = self.agent.get_knowledge()

        if knowledge:
            print(f"\n{Colors.GREEN}知识库共有 {len(knowledge)} 条:{Colors.RESET}\n")
            for i, item in enumerate(knowledge, 1):
                print(f"  {i}. [{item.get('category', '未分类')}] {item.get('content')[:60]}...")
        else:
            print_warning("知识库为空")

    def add_knowledge(self):
        """添加知识"""
        content = input("请输入知识内容: ").strip()

        if content:
            category = input_with_default("分类", "通用")

            if self.agent.add_knowledge(content, category):
                print_success("知识添加成功")
            else:
                print_error("知识添加失败")

    def export_knowledge(self):
        """导出知识库"""
        path = input_with_default("导出路径", "knowledge_export.json")

        if self.agent.export_knowledge(path):
            print_success(f"已导出到 {path}")
        else:
            print_error("导出失败")

    def import_knowledge(self):
        """导入知识库"""
        path = input_with_default("导入路径", "knowledge.json")

        if self.agent.import_knowledge(path):
            print_success("导入成功")
        else:
            print_error("导入失败")

    def settings(self):
        """设置"""
        print_header("⚙️ 设置")

        menu = Menu("设置", [
            ("1", "切换 LLM 提供商", self.switch_llm_provider),
            ("2", "配置 API Key", self.config_api_key),
            ("3", "查看当前配置", self.show_config),
            ("B", "返回主菜单", lambda: None),
        ])
        menu.run()

    def switch_llm_provider(self):
        """切换 LLM 提供商"""
        providers = ["OpenAI", "Anthropic", "智谱GLM", "Minimax", "Kimi", "Gemini"]
        choice = select_option(providers, "选择 LLM 提供商")

        provider_names = ["openai", "anthropic", "zhipu", "minimax", "kimi", "gemini"]
        selected = provider_names[choice]

        if self.agent.switch_llm_provider(selected):
            print_success(f"已切换到 {providers[choice]}")
        else:
            print_error("切换失败，请检查 API Key")

    def config_api_key(self):
        """配置 API Key"""
        print("\n当前支持以下环境变量配置:")
        print("  OPENAI_API_KEY")
        print("  ANTHROPIC_API_KEY")
        print("  ZHIPU_API_KEY")
        print("  MINIMAX_API_KEY")
        print("  KIMI_API_KEY")
        print("  GEMINI_API_KEY")
        print(f"\n请在终端中设置环境变量，例如:")
        print(f"  export OPENAI_API_KEY=your_key_here")

    def show_config(self):
        """显示当前配置"""
        config = self.agent.get_config()

        print()
        print(f"  {Colors.CYAN}LLM 提供商:{Colors.RESET} {config.get('provider')}")
        print(f"  {Colors.CYAN}模型:{Colors.RESET} {config.get('model')}")
        print(f"  {Colors.CYAN}MCP 地址:{Colors.RESET} {config.get('mcp_url')}")
        print()

    def test_llm(self):
        """测试 LLM"""
        print_header("🧪 测试 LLM")

        test_prompt = input_with_default("输入测试内容", "你好，请介绍一下你自己")

        print(f"\n{Colors.CYAN}调用 LLM...{Colors.RESET}\n")

        response = self.agent.test_llm(test_prompt)

        print(f"{Colors.GREEN}回复:{Colors.RESET}")
        print(response)


# ============== 入口点 ==============
def create_interface(agent):
    """创建界面"""
    return AgentInterface(agent)


if __name__ == "__main__":
    # 测试界面
    print("🧪 测试终端界面")
    print("=" * 50)

    print_success("成功消息测试")
    print_error("错误消息测试")
    print_warning("警告消息测试")
    print_info("信息消息测试")

    print("\n✅ 界面测试完成")
