#!/usr/bin/env python3
"""
Gateway 命令测试
"""
import asyncio
from xiaohongshu_agent.gateway import (
    SessionManager,
    AgentRegistry,
    ToolGateway,
    process_command,
    AgentResponse,
    UnifiedMessage,
)


async def test_commands():
    print("=" * 60)
    print("🚀 Gateway 命令系统测试")
    print("=" * 60)

    # 测试各种命令
    test_cases = [
        # 基础命令
        "/help",
        "/status",

        # XHS 命令
        "/xhs",
        "/xhs start",
        "/xhs login",
        "/xhs publish 测试内容",
        "/xhs search 护肤",
        "/xhs stats",
        "/xhs doctor",

        # Doctor 命令
        "/doctor",
        "/doctor fix",
        "/doctor check database",

        # Gateway 命令
        "/gateway",
        "/gateway config",

        # 工具命令
        "/tool list",

        # 会话命令
        "/session list",

        # 配置命令
        "/config show",

        # Orchestrator
        "/orch 写代码并测试",
    ]

    for cmd in test_cases:
        print(f"\n🔹 {cmd}")
        result = process_command(cmd)
        if result:
            # 截断显示
            content = result.content[:100] + "..." if len(result.content) > 100 else result.content
            print(f"   → {content.replace(chr(10), ' ')}")
        else:
            print("   → (传递给 Agent)")

    print("\n" + "=" * 60)
    print("✅ 命令测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_commands())
