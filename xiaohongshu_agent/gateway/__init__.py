"""
AI Agent Gateway - 网关模块

将 ai-agent-gateway 的核心功能移植到 Python 项目中
"""
from xiaohongshu_agent.gateway.types import (
    Agent,
    AgentStatus,
    AgentResponse,
    AgentContext,
    Capability,
    RoutingRules,
    Session,
    SessionContext,
    UnifiedMessage,
    GatewayConfig,
    Tool,
    ToolResult,
    MessageRole,
)

from xiaohongshu_agent.gateway.core import (
    SessionManager,
    AgentRegistry,
    ToolGateway,
    AgentOrchestrator,
    register_builtin_tools,
)

from xiaohongshu_agent.gateway.commands import (
    Command,
    CommandRegistry,
    get_command_registry,
    process_command,
)

__version__ = "1.0.0"

__all__ = [
    # Types
    "Agent",
    "AgentStatus",
    "AgentResponse",
    "AgentContext",
    "Capability",
    "RoutingRules",
    "Session",
    "SessionContext",
    "UnifiedMessage",
    "GatewayConfig",
    "Tool",
    "ToolResult",
    "MessageRole",
    # Core
    "SessionManager",
    "AgentRegistry",
    "ToolGateway",
    "AgentOrchestrator",
    "register_builtin_tools",
    # Commands
    "Command",
    "CommandRegistry",
    "get_command_registry",
    "process_command",
]
