"""
小红书 AI Agent
一个强大的小红书运营自动化框架
"""
__version__ = "2.0.0"
__author__ = "Eric Hong"

# 核心模块
from xiaohongshu_agent.agent.loop import XiaohongshuAgent
from xiaohongshu_agent.config import Config

# 服务层
from xiaohongshu_agent.services import (
    chat,
    search_notes,
    publish_note,
    get_stats,
    generate_content,
)

# Gateway (V2)
from xiaohongshu_agent.gateway import (
    SessionManager,
    AgentRegistry,
    ToolGateway,
    AgentOrchestrator,
    process_command,
)

__all__ = [
    # Core
    "XiaohongshuAgent",
    "Config",
    # Services
    "chat",
    "search_notes",
    "publish_note",
    "get_stats",
    "generate_content",
    # Gateway
    "SessionManager",
    "AgentRegistry",
    "ToolGateway",
    "AgentOrchestrator",
    "process_command",
    # Version
    "__version__",
]
