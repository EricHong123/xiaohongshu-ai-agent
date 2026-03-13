#!/usr/bin/env python3
"""
完整的 Gateway 服务器
包含：HTTP API + WebSocket + XiaohongshuAgent 集成
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
from xiaohongshu_agent.gateway.server.combined import CombinedServer


async def main():
    print("=" * 60)
    print("🚀 小红书 AI Gateway - 完整版")
    print("=" * 60)

    # 1. 初始化核心组件
    session_manager = SessionManager({
        "maxHistory": 50,
        "maxAgeHours": 24,
    })
    print("✅ SessionManager")

    tool_gateway = ToolGateway({"enabled": True})
    register_builtin_tools(tool_gateway)
    print("✅ ToolGateway")

    agent_registry = AgentRegistry({
        "defaultAgent": "assistant",
        "routingMode": "keyword",
    })
    print("✅ AgentRegistry")

    # 2. 注册基础 Agent
    async def echo_handler(message, context):
        return AgentResponse(content=f"Echo: {message.content}", metadata={})

    echo_agent = Agent(
        id="echo", name="Echo Agent", description="回声",
        status=AgentStatus.ONLINE, capabilities=[], handler=echo_handler
    )
    agent_registry.register(echo_agent)

    async def assistant_handler(message, context):
        content = message.content.lower()
        if "hello" in content or "你好" in content:
            return AgentResponse(content="你好！我是小红书 AI 助手", metadata={})
        if "help" in content or "帮助" in content:
            return AgentResponse(
                content="可用命令:\n- 生成:<主题> - AI 生成内容\n- 搜索:<关键词> - 搜索热门笔记\n- 统计 - 查看数据",
                metadata={}
            )
        return AgentResponse(
            content=f"收到: {message.content}",
            metadata={"fallback": True}
        )

    assistant_agent = Agent(
        id="assistant", name="Assistant Agent", description="通用助手",
        status=AgentStatus.ONLINE,
        capabilities=[],
        routingRules=RoutingRules(keywords=["hello", "help", "你好", "帮助"]),
        handler=assistant_handler
    )
    agent_registry.register(assistant_agent)

    # 3. 编排器
    orchestrator = AgentOrchestrator(
        agent_registry, tool_gateway, session_manager,
        config={"autoDecompose": True}
    )
    orchestrator_agent = orchestrator.create_orchestrator_agent()
    agent_registry.register(orchestrator_agent)

    # 4. 注册 Xiaohongshu Agent（模拟）
    async def xiaohongshu_handler(message, context):
        content = message.content

        if content.startswith("生成:"):
            topic = content[3:].strip()
            return AgentResponse(
                content=f"📝 已生成关于「{topic}」的笔记\n\n标题: {topic}的5个技巧\n\n内容: 分享5个实用技巧...\n\n#实用 #技巧 #{topic}",
                metadata={"type": "generate"}
            )

        if content.startswith("搜索:"):
            keyword = content[3:].strip()
            return AgentResponse(
                content=f"🔍 搜索「{keyword}」的结果:\n\n1. 笔记A (👍 1.2w)\n2. 笔记B (👍 8.5k)\n3. 笔记C (👍 3.2k)",
                metadata={"type": "search"}
            )

        if content == "统计":
            return AgentResponse(
                content="📊 数据统计\n\n- 已发布: 12篇\n- 点赞: 1,234\n- 评论: 567\n- 收藏: 890",
                metadata={"type": "stats"}
            )

        return AgentResponse(
            content=f"小红书助手收到: {content}\n\n输入「帮助」查看更多命令",
            metadata={}
        )

    xhs_agent = Agent(
        id="xiaohongshu", name="Xiaohongshu Agent", description="小红书运营助手",
        status=AgentStatus.ONLINE,
        capabilities=[
            type('Cap', (), {'name': 'generate', 'description': '生成笔记'})(),
            type('Cap', (), {'name': 'search', 'description': '搜索笔记'})(),
            type('Cap', (), {'name': 'stats', 'description': '数据统计'})(),
        ],
        routingRules=RoutingRules(keywords=["生成", "搜索", "统计", "小红书"]),
        handler=xiaohongshu_handler
    )
    agent_registry.register(xhs_agent)

    print("✅ Agent 注册完成")
    print("   - Echo Agent")
    print("   - Assistant Agent")
    print("   - Orchestrator Agent")
    print("   - Xiaohongshu Agent")

    # 5. 创建服务器
    server = CombinedServer(
        config={},
        session_manager=session_manager,
        agent_registry=agent_registry,
        tool_gateway=tool_gateway
    )

    # 6. 测试消息处理
    print("\n" + "=" * 60)
    print("📝 消息路由测试")
    print("=" * 60)

    session = session_manager.create("test_user", "cli")

    # 测试 1: Echo
    msg1 = UnifiedMessage(id="1", userId="test", channel="cli", content="test", sessionId=session.id)
    resp1 = await agent_registry.handle_message(msg1, session, session_manager, tool_gateway)
    print(f"\n[Echo] test → {resp1['content']}")

    # 测试 2: Assistant (关键词路由)
    msg2 = UnifiedMessage(id="2", userId="test", channel="cli", content="hello", sessionId=session.id)
    resp2 = await agent_registry.handle_message(msg2, session, session_manager, tool_gateway)
    print(f"[Assistant] hello → {resp2['content']}")

    # 测试 3: Xiaohongshu
    msg3 = UnifiedMessage(id="3", userId="test", channel="cli", content="生成:效率工具", sessionId=session.id)
    resp3 = await agent_registry.handle_message(msg3, session, session_manager, tool_gateway)
    print(f"[Xiaohongshu] 生成:效率工具 → {resp3['content'][:50]}...")

    # 测试 4: 搜索
    msg4 = UnifiedMessage(id="4", userId="test", channel="cli", content="搜索:护肤", sessionId=session.id)
    resp4 = await agent_registry.handle_message(msg4, session, session_manager, tool_gateway)
    print(f"[Xiaohongshu] 搜索:护肤 → {resp4['content'][:50]}...")

    # 7. 统计
    print("\n" + "=" * 60)
    print("📊 统计")
    print("=" * 60)
    print(f"会话: {session_manager.get_stats()}")
    print(f"Agent: {agent_registry.get_stats()['total']} 个")

    print("\n" + "=" * 60)
    print("🎉 Gateway 测试完成!")
    print("=" * 60)
    print("\n📌 API 端点:")
    print("   HTTP POST /api/v1/messages  - 发送消息")
    print("   HTTP GET  /api/v1/agents     - 获取 Agent 列表")
    print("   HTTP GET  /api/v1/tools      - 获取工具列表")
    print("   HTTP GET  /api/v1/stats      - 获取统计")
    print("   WS      /socket.io            - WebSocket")
    print("\n📌 测试命令:")
    print('   curl -X POST http://localhost:3001/api/v1/messages -d \'{"content":"hello"}\'')
    print("\n🚀 启动服务器请运行: server.run_full_gateway()")
    print("   (Ctrl+C 退出测试)")


if __name__ == "__main__":
    asyncio.run(main())
