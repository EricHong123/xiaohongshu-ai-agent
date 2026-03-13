"""
Gateway 类型定义
"""
from typing import Any, Callable, Dict, List, Optional, Protocol, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Agent 状态"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"


class MessageRole(str, Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Capability:
    """Agent 能力"""
    name: str
    description: str


@dataclass
class RoutingRules:
    """路由规则"""
    keywords: Optional[List[str]] = None
    users: Optional[List[str]] = None
    channels: Optional[List[str]] = None


# Agent 处理函数类型
AgentHandler = Callable[["UnifiedMessage", "AgentContext"], "AgentResponse"]


@dataclass
class Agent:
    """Agent 定义"""
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    status: AgentStatus = AgentStatus.OFFLINE
    capabilities: List[Capability] = field(default_factory=list)
    routingRules: Optional[RoutingRules] = None
    handler: Optional[AgentHandler] = None


@dataclass
class AgentResponse:
    """Agent 响应"""
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentContext:
    """Agent 执行上下文"""
    session: "Session"
    sessionManager: "SessionManager"
    toolGateway: "ToolGateway"
    logger: Any


@dataclass
class UnifiedMessage:
    """统一消息格式"""
    id: str
    userId: str
    channel: str
    content: str
    sessionId: Optional[str] = None
    role: MessageRole = MessageRole.USER
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Session:
    """会话"""
    id: str
    userId: str
    channel: str
    agentId: Optional[str] = None
    context: "SessionContext" = field(default_factory=lambda: SessionContext())
    createdAt: datetime = field(default_factory=datetime.now)
    updatedAt: datetime = field(default_factory=datetime.now)


@dataclass
class SessionContext:
    """会话上下文"""
    messages: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GatewayConfig:
    """网关配置"""
    server: Dict[str, Any] = field(default_factory=dict)
    session: Dict[str, Any] = field(default_factory=dict)
    agents: Dict[str, Any] = field(default_factory=dict)
    tools: Dict[str, Any] = field(default_factory=dict)
    logger: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Tool:
    """工具定义"""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    data: Any = None
    error: Optional[str] = None


# 类型别名
ToolHandler = Callable[[Dict[str, Any]], ToolResult]
