"""
兼容层：旧路径 `xiaohongshu_agent.channels.xiaohongshu`

实现已迁移到 `xiaohongshu_agent.integrations.xhs_mcp.channel`。
"""

from xiaohongshu_agent.integrations.xhs_mcp.channel import MCPError, XiaohongshuChannel, retry_on_error

__all__ = ["XiaohongshuChannel", "MCPError", "retry_on_error"]
