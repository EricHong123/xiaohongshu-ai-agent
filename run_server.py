#!/usr/bin/env python3
"""
启动 Gateway HTTP/WebSocket 服务器
"""
import asyncio
from xiaohongshu_agent.gateway import (
    SessionManager,
    AgentRegistry,
    ToolGateway,
    AgentOrchestrator,
    register_builtin_tools,
    Agent,
    AgentStatus,
    AgentResponse,
    RoutingRules,
)
from xiaohongshu_agent.gateway.server.combined import CombinedServer


def create_gateway_server():
    """创建并配置 Gateway 服务器"""

    # 核心组件
    session_manager = SessionManager({"maxHistory": 50, "maxAgeHours": 24})
    tool_gateway = ToolGateway({"enabled": True})
    register_builtin_tools(tool_gateway)
    agent_registry = AgentRegistry({"defaultAgent": "assistant", "routingMode": "keyword"})

    # Echo Agent
    async def echo_handler(message, context):
        return AgentResponse(content=f"Echo: {message.content}", metadata={})

    agent_registry.register(Agent(
        id="echo", name="Echo Agent", description="回声",
        status=AgentStatus.ONLINE, handler=echo_handler
    ))

    # Assistant Agent
    async def assistant_handler(message, context):
        content = message.content.lower()
        if "hello" in content:
            return AgentResponse(content="你好！我是小红书 AI 助手", metadata={})
        if "help" in content:
            return AgentResponse(content="帮助: 你可以发送各种消息", metadata={})
        return AgentResponse(content=f"收到: {message.content}", metadata={})

    agent_registry.register(Agent(
        id="assistant", name="Assistant Agent", description="通用助手",
        status=AgentStatus.ONLINE,
        routingRules=RoutingRules(keywords=["hello", "help"]),
        handler=assistant_handler
    ))

    # Orchestrator
    orchestrator = AgentOrchestrator(
        agent_registry, tool_gateway, session_manager,
        config={"autoDecompose": True}
    )
    agent_registry.register(orchestrator.create_orchestrator_agent())

    # Xiaohongshu Agent
    async def xhs_handler(message, context):
        content = message.content
        if content.startswith("生成:"):
            topic = content[3:].strip()
            return AgentResponse(
                content=f"📝 关于「{topic}」的笔记\n\n标题: {topic}的5个技巧\n内容: ...",
                metadata={"type": "generate"}
            )
        if content.startswith("搜索:"):
            return AgentResponse(content="🔍 搜索结果...", metadata={"type": "search"})
        if content == "统计":
            return AgentResponse(content="📊 数据统计", metadata={"type": "stats"})
        return AgentResponse(content=f"小红书助手: {content}", metadata={})

    agent_registry.register(Agent(
        id="xiaohongshu", name="Xiaohongshu Agent", description="小红书运营助手",
        status=AgentStatus.ONLINE,
        routingRules=RoutingRules(keywords=["生成", "搜索", "统计"]),
        handler=xhs_handler
    ))

    # 创建服务器
    server = CombinedServer(
        config={},
        session_manager=session_manager,
        agent_registry=agent_registry,
        tool_gateway=tool_gateway
    )

    return server


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 启动 Gateway 服务器")
    print("=" * 50)

    server = create_gateway_server()
    server.run(http_port=3000, ws_port=3001)
