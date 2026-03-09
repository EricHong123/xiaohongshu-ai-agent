#!/usr/bin/env python3
"""
增强版小红书 AI Agent
集成安全控制和电脑控制功能
"""
import json
import os
import sys
import argparse
from typing import Dict, Any, List, Optional

# 导入模块
from agent import XiaohongshuAgent
from security import SecurityManager, PermissionManager
from computer_control import ComputerController


# ============== 增强 Agent ==============
class EnhancedAgent(XiaohongshuAgent):
    """增强版 Agent - 集成电脑控制"""

    def __init__(self, enable_permissions: List[str] = None, **kwargs):
        # 初始化父类
        super().__init__(**kwargs)

        # 初始化安全控制
        self.security = SecurityManager()

        # 初始化电脑控制
        self.computer = ComputerController(enable_permissions or [])

        print(f"\n🔐 安全模块已加载")
        print(f"   权限: {self.computer.get_status()['permissions']}")

    # ============== 电脑控制接口 ==============
    def list_files(self, path: str = None) -> Dict:
        """列出文件"""
        return self.computer.file.list_directory(path)

    def read_file(self, path: str) -> Dict:
        """读取文件"""
        return self.computer.file.read_file(path)

    def write_file(self, path: str, content: str) -> Dict:
        """写入文件"""
        return self.computer.file.write_file(path)

    def create_folder(self, path: str) -> Dict:
        """创建文件夹"""
        return self.computer.file.create_directory(path)

    def delete_file(self, path: str) -> Dict:
        """删除文件"""
        return self.computer.file.delete_file(path)

    def execute_command(self, command: str) -> Dict:
        """执行命令"""
        return self.computer.command.execute(command)

    def get_system_info(self) -> Dict:
        """获取系统信息"""
        return self.computer.command.get_system_info()

    def open_browser(self, url: str) -> Dict:
        """打开浏览器"""
        return self.computer.browser.open_url(url)

    def take_screenshot(self, path: str = None) -> Dict:
        """截图"""
        return self.computer.screenshot.capture_screen(path)

    def read_clipboard(self) -> Dict:
        """读剪贴板"""
        return self.computer.clipboard.read()

    def write_clipboard(self, content: str) -> Dict:
        """写剪贴板"""
        return self.computer.clipboard.write(content)

    def send_notification(self, title: str, message: str) -> Dict:
        """发送通知"""
        return self.computer.notification.send(title, message)

    def speak(self, text: str) -> Dict:
        """语音播报"""
        return self.computer.notification.speak(text)

    def enable_permissions(self, perms: List[str]):
        """启用权限"""
        self.computer.enable_permissions(perms)
        self.computer.security.permissions.enable_permissions(perms)

    def get_permissions(self) -> Dict:
        """获取权限状态"""
        return self.computer.get_status()


# ============== 自然语言解析 ==============
def parse_command(text: str) -> Dict[str, Any]:
    """解析自然语言命令"""
    text = text.lower()

    # 文件操作
    if "列出" in text and ("文件" in text or "桌面" in text):
        path = os.path.expanduser("~/Desktop")
        if "下载" in text:
            path = os.path.expanduser("~/Downloads")
        return {"action": "list_files", "path": path}

    if "读取" in text and "文件" in text:
        # 提取文件路径
        parts = text.replace("读取", "").replace("文件", "").strip()
        return {"action": "read_file", "path": parts}

    if "创建" in text and "文件夹" in text:
        parts = text.replace("创建", "").replace("文件夹", "").strip()
        return {"action": "create_folder", "path": parts}

    if "删除" in text and "文件" in text:
        parts = text.replace("删除", "").replace("文件", "").strip()
        return {"action": "delete_file", "path": parts}

    # 命令执行
    if "执行" in text or "运行" in text:
        cmd = text.replace("执行", "").replace("运行", "").strip()
        return {"action": "execute_command", "command": cmd}

    # 浏览器
    if "打开" in text and ("浏览器" in text or "网页" in text or "网站" in text):
        url = text.replace("打开", "").replace("浏览器", "").replace("网页", "").replace("网站", "").strip()
        if not url.startswith("http"):
            url = "https://" + url
        return {"action": "open_browser", "url": url}

    # 截图
    if "截屏" in text or "截图" in text:
        return {"action": "screenshot"}

    # 剪贴板
    if "复制" in text:
        return {"action": "read_clipboard"}
    if "粘贴" in text:
        return {"action": "write_clipboard"}

    # 通知
    if "通知" in text or "提醒" in text:
        return {"action": "send_notification", "message": text}

    # 语音
    if "朗读" in text or "播报" in text or "说话" in text:
        return {"action": "speak", "text": text}

    # 系统信息
    if "系统信息" in text or "电脑信息" in text:
        return {"action": "get_system_info"}

    return {"action": "unknown", "text": text}


# ============== CLI 接口 ==============
def main():
    parser = argparse.ArgumentParser(description="增强版小红书 AI Agent")
    parser.add_argument("-k", "--keyword", help="搜索关键词")
    parser.add_argument("-i", "--images", help="图片路径")
    parser.add_argument("--publish", action="store_true", help="发布帖子")
    parser.add_argument("--stats", action="store_true", help="查看统计")
    parser.add_argument("--chat", action="store_true", help="对话模式")

    # 电脑控制选项
    parser.add_argument("--permissions", nargs="+", default=[],
                       help="启用权限: file_read, file_write, command_exec, browser_control, screenshot, clipboard")
    parser.add_argument("--list-files", metavar="PATH", help="列出目录文件")
    parser.add_argument("--read-file", metavar="PATH", help="读取文件")
    parser.add_argument("--write-file", nargs=2, metavar=("PATH", "CONTENT"), help="写入文件")
    parser.add_argument("--command", "-c", metavar="CMD", help="执行命令")
    parser.add_argument("--open-url", metavar="URL", help="打开URL")
    parser.add_argument("--screenshot", action="store_true", help="截图")
    parser.add_argument("--clipboard-read", action="store_true", help="读剪贴板")
    parser.add_argument("--clipboard-write", metavar="TEXT", help="写剪贴板")
    parser.add_argument("--notify", nargs=2, metavar=("TITLE", "MESSAGE"), help="发送通知")
    parser.add_argument("--speak", metavar="TEXT", help="语音播报")
    parser.add_argument("--system-info", action="store_true", help="系统信息")

    args = parser.parse_args()

    # 创建 Agent
    permissions = args.permissions or ["file_read", "browser_control", "clipboard"]
    agent = EnhancedAgent(enable_permissions=permissions)

    # 执行操作
    if args.keyword:
        posts = agent.search(args.keyword)
        print(f"\n找到 {len(posts)} 条结果:\n")
        for i, p in enumerate(posts[:10], 1):
            print(f"  {i}. {p['title'][:40]}... [赞:{p['likes']}] [评:{p['comments']}] [藏:{p['collects']}]")

    if args.publish and args.keyword:
        images = args.images.split(",") if args.images else []
        if images:
            content = agent.generate_content(args.keyword)
            result = agent.publish(content, images)
            print(f"\n发布结果: {result}")

    if args.stats:
        stats = agent.get_stats()
        print("\n📊 统计信息:")
        print(f"  已发布帖子: {stats['published_posts']}")
        print(f"  总点赞: {stats['total_likes']}")
        print(f"  总评论: {stats['total_comments']}")
        print(f"  知识库: {stats['knowledge_items']}")

    # 电脑控制操作
    if args.list_files:
        result = agent.list_files(args.list_files)
        print(f"\n📁 {result.get('path', '')}")
        if result.get("success"):
            for item in result.get("items", [])[:20]:
                icon = "📁" if item["type"] == "directory" else "📄"
                print(f"  {icon} {item['name']}")
        else:
            print(f"  错误: {result.get('error')}")

    if args.read_file:
        result = agent.read_file(args.read_file)
        if result.get("success"):
            print(f"\n📄 文件内容 ({result.get('size')} bytes):")
            print(result.get("content", "")[:2000])
        else:
            print(f"\n错误: {result.get('error')}")

    if args.write_file:
        path, content = args.write_file
        result = agent.write_file(path, content)
        print(f"\n{'✅' if result.get('success') else '❌'} {result}")

    if args.command:
        result = agent.execute_command(args.command)
        print(f"\n📟 命令输出:")
        if result.get("success"):
            print(result.get("stdout", "")[:1000])
        else:
            print(f"错误: {result.get('error')}")

    if args.open_url:
        result = agent.open_browser(args.open_url)
        print(f"\n{'✅' if result.get('success') else '❌'} {result}")

    if args.screenshot:
        result = agent.take_screenshot()
        print(f"\n{'✅' if result.get('success') else '❌'} 截图: {result.get('path')}")

    if args.clipboard_read:
        result = agent.read_clipboard()
        print(f"\n📋 剪贴板内容: {result.get('content', '')[:500]}")

    if args.clipboard_write:
        result = agent.write_clipboard(args.clipboard_write)
        print(f"\n{'✅' if result.get('success') else '❌'} {result}")

    if args.notify:
        title, message = args.notify
        result = agent.send_notification(title, message)
        print(f"\n{'✅' if result.get('success') else '❌'} {result}")

    if args.speak:
        result = agent.speak(args.speak)
        print(f"\n{'✅' if result.get('success') else '❌'} {result}")

    if args.system_info:
        result = agent.get_system_info()
        info = result.get("info", {})
        print("\n💻 系统信息:")
        print(f"  平台: {info.get('platform')}")
        print(f"  Python: {info.get('python_version', '')[:20]}")
        print(f"  用户: {info.get('user')}")
        print(f"  当前目录: {info.get('cwd')}")
        print(f"\n🔐 权限状态:")
        perms = agent.get_permissions()["permissions"]
        for p, v in perms.items():
            print(f"  {p}: {'✅' if v else '❌'}")

    # 对话模式
    if args.chat:
        print("\n🤖 对话模式 (输入 'exit' 退出)")
        print("   可以执行电脑操作，如：")
        print("   - '列出桌面文件'")
        print("   - '打开 https://baidu.com'")
        print("   - '截屏'")
        print("   - '读取剪贴板'")
        print("   - '系统信息'\n")

        while True:
            user_input = input("你: ").strip()
            if user_input.lower() in ['exit', 'q']:
                break
            if not user_input:
                continue

            # 解析命令
            cmd = parse_command(user_input)
            action = cmd.get("action")

            if action == "unknown":
                # 使用 AI 处理
                response = agent.chat(user_input)
                print(f"\nAI: {response}\n")
            elif action == "list_files":
                result = agent.list_files(cmd.get("path"))
                print(f"\n文件: {result.get('count', 0)} 个")
            elif action == "read_file":
                result = agent.read_file(cmd.get("path"))
                print(f"\n内容: {result.get('content', '')[:500]}")
            elif action == "create_folder":
                result = agent.create_folder(cmd.get("path"))
                print(f"\n{'✅' if result.get('success') else '❌'} {result}")
            elif action == "delete_file":
                result = agent.delete_file(cmd.get("path"))
                print(f"\n{'✅' if result.get('success') else '❌'} {result}")
            elif action == "execute_command":
                result = agent.execute_command(cmd.get("command"))
                print(f"\n{result.get('stdout', '')[:500]}")
            elif action == "open_browser":
                result = agent.open_browser(cmd.get("url"))
                print(f"\n{'✅' if result.get('success') else '❌'}")
            elif action == "screenshot":
                result = agent.take_screenshot()
                print(f"\n{'✅' if result.get('success') else '❌'} 截图保存到: {result.get('path')}")
            elif action == "read_clipboard":
                result = agent.read_clipboard()
                print(f"\n{result.get('content', '')[:200]}")
            elif action == "write_clipboard":
                result = agent.write_clipboard(user_input.replace("粘贴", "").strip())
                print(f"\n{'✅' if result.get('success') else '❌'}")
            elif action == "send_notification":
                result = agent.send_notification("AI Agent", cmd.get("message", user_input))
                print(f"\n{'✅' if result.get('success') else '❌'}")
            elif action == "speak":
                result = agent.speak(user_input.replace("朗读", "").replace("播报", "").strip())
                print(f"\n{'✅' if result.get('success') else '❌'}")
            elif action == "get_system_info":
                result = agent.get_system_info()
                print(f"\n{result}")


if __name__ == "__main__":
    main()
