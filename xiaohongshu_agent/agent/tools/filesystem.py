"""
文件系统工具
"""
import os
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

from xiaohongshu_agent.agent.tools.base import Tool, ToolResult
from xiaohongshu_agent.agent.tools.registry import register_tool
from xiaohongshu_agent.utils.logger import get_logger

logger = get_logger("tools.filesystem")


@register_tool("file_read")
class FileReadTool(Tool):
    """读取文件工具"""

    name = "file_read"
    description = "读取文件内容"

    def __init__(self, allowed_dirs: List[str] = None):
        self.allowed_dirs = allowed_dirs or [os.path.expanduser("~")]

    def execute(self, path: str = None, **kwargs) -> ToolResult:
        """读取文件"""
        if not path:
            return ToolResult(success=False, error="缺少文件路径")

        # 安全检查
        abs_path = os.path.abspath(os.path.expanduser(path))
        if not any(abs_path.startswith(d) for d in self.allowed_dirs):
            return ToolResult(success=False, error=f"不允许访问路径: {path}")

        try:
            if not os.path.exists(abs_path):
                return ToolResult(success=False, error=f"文件不存在: {path}")

            if not os.path.isfile(abs_path):
                return ToolResult(success=False, error=f"不是文件: {path}")

            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()

            size = os.path.getsize(abs_path)
            logger.info(f"读取文件: {path} ({size} bytes)")

            return ToolResult(
                success=True,
                data={
                    "path": abs_path,
                    "content": content,
                    "size": size,
                    "lines": len(content.splitlines())
                }
            )
        except Exception as e:
            logger.error(f"读取文件失败: {e}")
            return ToolResult(success=False, error=str(e))

    def get_schema(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"}
                },
                "required": ["path"]
            }
        }


@register_tool("file_write")
class FileWriteTool(Tool):
    """写入文件工具"""

    name = "file_write"
    description = "写入文件内容"

    def __init__(self, allowed_dirs: List[str] = None):
        self.allowed_dirs = allowed_dirs or [os.path.expanduser("~")]

    def execute(self, path: str = None, content: str = "", **kwargs) -> ToolResult:
        """写入文件"""
        if not path:
            return ToolResult(success=False, error="缺少文件路径")

        if not content:
            return ToolResult(success=False, error="缺少内容")

        # 安全检查
        abs_path = os.path.abspath(os.path.expanduser(path))
        if not any(abs_path.startswith(d) for d in self.allowed_dirs):
            return ToolResult(success=False, error=f"不允许访问路径: {path}")

        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)

            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)

            size = len(content.encode("utf-8"))
            logger.info(f"写入文件: {path} ({size} bytes)")

            return ToolResult(
                success=True,
                data={
                    "path": abs_path,
                    "size": size
                }
            )
        except Exception as e:
            logger.error(f"写入文件失败: {e}")
            return ToolResult(success=False, error=str(e))

    def get_schema(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "文件内容"}
                },
                "required": ["path", "content"]
            }
        }


@register_tool("list_directory")
class ListDirectoryTool(Tool):
    """列出目录工具"""

    name = "list_directory"
    description = "列出目录内容"

    def __init__(self, allowed_dirs: List[str] = None):
        self.allowed_dirs = allowed_dirs or [os.path.expanduser("~")]

    def execute(self, path: str = None, **kwargs) -> ToolResult:
        """列出目录"""
        target_path = os.path.expanduser(path) if path else os.path.expanduser("~")
        abs_path = os.path.abspath(target_path)

        # 安全检查
        if not any(abs_path.startswith(d) for d in self.allowed_dirs):
            return ToolResult(success=False, error=f"不允许访问路径: {path}")

        try:
            if not os.path.exists(abs_path):
                return ToolResult(success=False, error=f"目录不存在: {path}")

            if not os.path.isdir(abs_path):
                return ToolResult(success=False, error=f"不是目录: {path}")

            items = []
            for item in os.listdir(abs_path):
                item_path = os.path.join(abs_path, item)
                stat = os.stat(item_path)
                items.append({
                    "name": item,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })

            # 按类型和名称排序
            items.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))

            logger.info(f"列出目录: {abs_path} ({len(items)} 项)")

            return ToolResult(
                success=True,
                data={
                    "path": abs_path,
                    "items": items,
                    "count": len(items)
                }
            )
        except Exception as e:
            logger.error(f"列出目录失败: {e}")
            return ToolResult(success=False, error=str(e))

    def get_schema(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "目录路径"}
                }
            }
        }
