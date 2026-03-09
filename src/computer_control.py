#!/usr/bin/env python3
"""
电脑控制模块
提供安全的文件操作、命令执行、浏览器控制等功能
"""
import os
import sys
import json
import time
import shutil
import subprocess
import tempfile
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

# 安全模块
from security import SecurityManager, SecurityConfig


# ============== 文件操作 ==============
class FileController:
    """文件控制器"""

    def __init__(self, security: SecurityManager):
        self.security = security
        self.allowed_dirs = SecurityConfig.ALLOWED_DIRS

    def read_file(self, path: str) -> Dict[str, Any]:
        """读取文件"""
        if not self.security.check_file_read(path):
            return {"success": False, "error": "权限不足"}

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # 限制返回大小
            if len(content) > 50000:
                content = content[:50000] + "\n... (truncated)"

            return {
                "success": True,
                "content": content,
                "size": os.path.getsize(path),
                "modified": datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """写入文件"""
        if not self.security.check_file_write(path):
            return {"success": False, "error": "权限不足"}

        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            return {
                "success": True,
                "path": path,
                "size": len(content)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_directory(self, path: str = None) -> Dict[str, Any]:
        """列出目录内容"""
        if path is None:
            path = os.path.expanduser("~/Desktop")

        if not self.security.check_file_read(path):
            return {"success": False, "error": "权限不足"}

        try:
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                stat = os.stat(item_path)
                items.append({
                    "name": item,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "size": stat.st_size if os.path.isfile(item_path) else 0,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

            return {
                "success": True,
                "path": path,
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_directory(self, path: str) -> Dict[str, Any]:
        """创建目录"""
        if not self.security.check_file_write(path):
            return {"success": False, "error": "权限不足"}

        try:
            os.makedirs(path, exist_ok=True)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_file(self, path: str) -> Dict[str, Any]:
        """删除文件/目录"""
        if not self.security.check_file_write(path):
            return {"success": False, "error": "权限不足"}

        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def copy_file(self, src: str, dst: str) -> Dict[str, Any]:
        """复制文件"""
        if not self.security.check_file_read(src):
            return {"success": False, "error": "源文件权限不足"}
        if not self.security.check_file_write(dst):
            return {"success": False, "error": "目标文件权限不足"}

        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            return {"success": True, "src": src, "dst": dst}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def move_file(self, src: str, dst: str) -> Dict[str, Any]:
        """移动文件"""
        if not self.security.check_file_read(src):
            return {"success": False, "error": "源文件权限不足"}
        if not self.security.check_file_write(dst):
            return {"success": False, "error": "目标文件权限不足"}

        try:
            shutil.move(src, dst)
            return {"success": True, "src": src, "dst": dst}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============== 命令执行 ==============
class CommandController:
    """命令控制器"""

    def __init__(self, security: SecurityManager):
        self.security = security

    def execute(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """执行命令"""
        if not self.security.check_command(command):
            return {"success": False, "error": "命令不允许执行"}

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.path.expanduser("~/Desktop")
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout[:10000],  # 限制输出大小
                "stderr": result.stderr[:5000],
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "命令执行超时"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        info = {
            "platform": sys.platform,
            "python_version": sys.version,
            "cwd": os.getcwd(),
            "home": os.path.expanduser("~"),
            "user": os.getenv("USER", "unknown"),
        }

        # macOS 特定信息
        if sys.platform == "darwin":
            try:
                result = subprocess.run(
                    ["sw_vers"],
                    capture_output=True,
                    text=True
                )
                info["macos"] = result.stdout
            except:
                pass

        return {"success": True, "info": info}


# ============== 浏览器控制 ==============
class BrowserController:
    """浏览器控制器 (macOS)"""

    def __init__(self, security: SecurityManager):
        self.security = security

    def open_url(self, url: str) -> Dict[str, Any]:
        """打开 URL"""
        if not url.startswith(("http://", "https://")):
            return {"success": False, "error": "无效的 URL"}

        try:
            subprocess.run(["open", url], check=True)
            return {"success": True, "url": url}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_browsers(self) -> List[str]:
        """获取可用浏览器"""
        browsers = []
        for browser in ["Google Chrome", "Safari", "Firefox", "Microsoft Edge"]:
            app_path = f"/Applications/{browser}.app"
            if os.path.exists(app_path):
                browsers.append(browser)
        return browsers


# ============== 截图控制 ==============
class ScreenshotController:
    """截图控制器 (macOS)"""

    def __init__(self, security: SecurityManager):
        self.security = security

    def capture_screen(self, save_path: str = None) -> Dict[str, Any]:
        """截取屏幕"""
        if not self.security.permissions.has_permission("screenshot"):
            return {"success": False, "error": "没有截图权限"}

        if save_path is None:
            save_path = os.path.expanduser(f"~/Desktop/screenshot_{int(time.time())}.png")

        try:
            # 使用 macOS screencapture
            result = subprocess.run(
                ["screencapture", "-x", save_path],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "path": save_path,
                    "size": os.path.getsize(save_path)
                }
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============== 剪贴板控制 ==============
class ClipboardController:
    """剪贴板控制器"""

    def __init__(self, security: SecurityManager):
        self.security = security

    def read(self) -> Dict[str, Any]:
        """读取剪贴板"""
        if not self.security.permissions.has_permission("clipboard"):
            return {"success": False, "error": "没有剪贴板权限"}

        try:
            if sys.platform == "darwin":
                result = subprocess.run(
                    ["pbpaste"],
                    capture_output=True,
                    text=True
                )
                return {"success": True, "content": result.stdout}
            return {"success": False, "error": "不支持的平台"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write(self, content: str) -> Dict[str, Any]:
        """写入剪贴板"""
        if not self.security.permissions.has_permission("clipboard"):
            return {"success": False, "error": "没有剪贴板权限"}

        try:
            if sys.platform == "darwin":
                subprocess.run(
                    ["pbcopy"],
                    input=content,
                    text=True,
                    check=True
                )
                return {"success": True, "length": len(content)}
            return {"success": False, "error": "不支持的平台"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============== 通知控制 ==============
class NotificationController:
    """系统通知控制器"""

    def __init__(self, security: SecurityManager):
        self.security = security

    def send(self, title: str, message: str) -> Dict[str, Any]:
        """发送通知"""
        try:
            if sys.platform == "darwin":
                subprocess.run(
                    ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
                    check=True
                )
                return {"success": True}
            return {"success": False, "error": "不支持的平台"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def speak(self, text: str) -> Dict[str, Any]:
        """文字转语音"""
        try:
            if sys.platform == "darwin":
                subprocess.run(
                    ["say", text],
                    check=True,
                    timeout=30
                )
                return {"success": True}
            return {"success": False, "error": "不支持的平台"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============== 主控制器 ==============
class ComputerController:
    """电脑控制器 - 统一入口"""

    def __init__(self, enable_permissions: List[str] = None):
        # 初始化安全管理器
        self.security = SecurityManager()

        # 启用权限
        if enable_permissions:
            self.security.permissions.enable_permissions(enable_permissions)

        # 初始化各控制器
        self.file = FileController(self.security)
        self.command = CommandController(self.security)
        self.browser = BrowserController(self.security)
        self.screenshot = ScreenshotController(self.security)
        self.clipboard = ClipboardController(self.security)
        self.notification = NotificationController(self.security)

    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "permissions": self.security.permissions.get_permissions(),
            "allowed_dirs": SecurityConfig.ALLOWED_DIRS,
            "allowed_commands": SecurityConfig.ALLOWED_COMMANDS,
        }

    def enable_permissions(self, perms: List[str]):
        """启用权限"""
        self.security.permissions.enable_permissions(perms)

    def disable_permissions(self):
        """禁用所有权限"""
        self.security.permissions.disable_all()


# 测试
if __name__ == "__main__":
    print("🧪 测试电脑控制模块")
    print("=" * 50)

    # 创建控制器（启用所有权限用于测试）
    cc = ComputerController([
        "file_read", "file_write", "command_exec",
        "browser_control", "screenshot", "clipboard"
    ])

    # 测试状态
    print("\n[1] 状态")
    status = cc.get_status()
    print(f"   权限: {status['permissions']}")

    # 测试文件操作
    print("\n[2] 文件操作")
    result = cc.file.list_directory(os.path.expanduser("~/Desktop"))
    print(f"   桌面文件数: {result.get('count', 0)}")

    # 测试系统信息
    print("\n[3] 系统信息")
    info = cc.command.get_system_info()
    print(f"   平台: {info.get('info', {}).get('platform')}")
    print(f"   用户: {info.get('info', {}).get('user')}")

    # 测试浏览器
    print("\n[4] 浏览器")
    browsers = cc.browser.get_browsers()
    print(f"   可用浏览器: {browsers}")

    print("\n✅ 电脑控制模块测试完成")
