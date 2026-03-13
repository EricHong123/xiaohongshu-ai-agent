#!/usr/bin/env python3
"""
Gateway 服务器启动脚本
演示如何使用融合后的 Gateway 模块
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
    UnifiedMessage,
    AgentResponse,
    RoutingRules,
)


async def main():
    print("=" * 50)
    print("🚀 小红书 AI Gateway")
    print("=" * 50)

    # 1. 初始化核心组件
    session_manager = SessionManager({
        "maxHistory": 50,
        "maxAgeHours": 24,
    })
    print("✅ SessionManager 初始化完成")

    tool_gateway = ToolGateway({"enabled": True})
    register_builtin_tools(tool_gateway)
    print("✅ ToolGateway 初始化完成")

    agent_registry = AgentRegistry({
        "defaultAgent": "assistant",
        "routingMode": "keyword",
    })
    print("✅ AgentRegistry 初始化完成")

    # 2. 注册 Agent
    async def echo_handler(message, context):
        return AgentResponse(
            content=f"Echo: {message.content}",
            metadata={"handler": "echo"}
        )

    echo_agent = Agent(
        id="echo",
        name="Echo Agent",
        description="简单的回声 Agent",
        version="1.0.0",
        status=AgentStatus.ONLINE,
        capabilities=[],
        handler=echo_handler
    )
    agent_registry.register(echo_agent)

    async def assistant_handler(message, context):
        responses = {
            "hello": "你好！我是小红书 AI 助手",
            "help": "我可以帮你：生成内容、搜索热点、优化标题等",
            "bye": "再见！有问题随时找我"
        }
        content = message.content.lower()
        for key, value in responses.items():
            if key in content:
                return AgentResponse(content=value, metadata={"matched": key})
        return AgentResponse(
            content=f"收到: {message.content}，有什么可以帮你的？",
            metadata={"fallback": True}
        )

    assistant_agent = Agent(
        id="assistant",
        name="Assistant Agent",
        description="通用助手",
        version="1.0.0",
        status=AgentStatus.ONLINE,
        capabilities=[],
        routingRules=RoutingRules(keywords=["hello", "help", "bye"]),
        handler=assistant_handler
    )
    agent_registry.register(assistant_agent)

    # 3. 初始化编排器
    orchestrator = AgentOrchestrator(
        agent_registry,
        tool_gateway,
        session_manager,
        config={"autoDecompose": True}
    )
    orchestrator_agent = orchestrator.create_orchestrator_agent()
    agent_registry.register(orchestrator_agent)

    print("✅ Agent 注册完成")
    print("   - Echo Agent")
    print("   - Assistant Agent")
    print("   - Orchestrator Agent")

    # 4. 测试消息处理
    print("\n" + "=" * 50)
    print("📝 测试消息处理")
    print("=" * 50)

    # 测试 1: 路由到 Echo (默认)
    session = session_manager.create("test_user", "cli")
    message = UnifiedMessage(
        id="test_1",
        userId="test_user",
        channel="cli",
        content="Hello World",
        sessionId=session.id
    )

    response = await agent_registry.handle_message(
        message, session, session_manager, tool_gateway
    )
    print(f"\n👤 用户: {message.content}")
    print(f"🤖 Agent: {response['content']}")

    # 测试 2: 路由到 Assistant (关键词匹配)
    message2 = UnifiedMessage(
        id="test_2",
        userId="test_user",
        channel="cli",
        content="hello",
        sessionId=session.id
    )

    response2 = await agent_registry.handle_message(
        message2, session, session_manager, tool_gateway
    )
    print(f"\n👤 用户: {message2.content}")
    print(f"🤖 Agent: {response2['content']}")

    # 测试 3: 编排器
    print("\n" + "=" * 50)
    print("🎭 测试编排器")
    print("=" * 50)

    message3 = UnifiedMessage(
        id="test_3",
        userId="test_user",
        channel="cli",
        content="/orch 写代码并测试",
        sessionId=session.id
    )

    response3 = await agent_registry.handle_message(
        message3, session, session_manager, tool_gateway
    )
    print(f"\n👤 用户: {message3.content}")
    print(f"🤖 Agent: {response3['content']}")

    # 5. 统计
    print("\n" + "=" * 50)
    print("📊 统计信息")
    print("=" * 50)
    print(f"会话数: {session_manager.get_stats()}")
    print(f"Agent数: {agent_registry.get_stats()}")

    print("\n🎉 Gateway 测试完成!")
    print("\n📌 API 端点:")
    print("   POST /api/v1/messages  - 发送消息")
    print("   GET  /api/v1/sessions  - 获取会话列表")
    print("   GET  /api/v1/agents   - 获取 Agent 列表")
    print("   GET  /api/v1/tools    - 获取工具列表")
    print("   GET  /api/v1/stats    - 获取统计信息")
    print("   GET  /health          - 健康检查")


if __name__ == "__main__":
    asyncio.run(main())
