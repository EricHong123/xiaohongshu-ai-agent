"""
工具模块
"""
# 导入所有工具以触发注册
from xiaohongshu_agent.agent.tools.base import Tool, ToolResult
from xiaohongshu_agent.agent.tools.registry import ToolRegistry, registry, register_tool

# 导入工具实现
from xiaohongshu_agent.agent.tools import filesystem
from xiaohongshu_agent.agent.tools import shell
from xiaohongshu_agent.agent.tools import web

__all__ = [
    "Tool",
    "ToolResult",
    "ToolRegistry",
    "registry",
    "register_tool",
]
