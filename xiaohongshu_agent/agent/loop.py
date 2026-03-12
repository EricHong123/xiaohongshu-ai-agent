"""
Agent 主循环
"""
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

from xiaohongshu_agent.providers import create_provider
from xiaohongshu_agent.storage import Database
from xiaohongshu_agent.integrations.xhs_mcp import XiaohongshuChannel
from xiaohongshu_agent.agent.context import Context
from xiaohongshu_agent.agent.memory import Memory
from xiaohongshu_agent.domain import Post, PublishResult
from xiaohongshu_agent.apps.xhs.services.knowledge import load_knowledge


class XiaohongshuAgent:
    """小红书 AI Agent 主类"""

    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4",
        api_key: str = "",
        base_url: str = "",
        mcp_url: str = "http://localhost:18060/mcp",
        db_path: str = "xiaohongshu_agent.db",
    ):
        # 初始化 LLM 提供商
        self.provider = create_provider(
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

        # 初始化数据库
        self.db = Database(db_path)

        # 初始化通道 (小红书 MCP)
        self.channel = XiaohongshuChannel(mcp_url)

        # 初始化上下文和记忆
        self.context = Context()
        self.memory = Memory(self.db)

        # 知识库
        self.knowledge = load_knowledge()

        print(f"✓ LLM: {provider}/{model}")
        print(f"✓ MCP: {mcp_url}")
        print(f"✓ 数据库: {db_path}")
        print(f"✓ 对话历史: {self.memory.count()} 条")

    def chat(self, message: str) -> str:
        """处理对话"""
        from xiaohongshu_agent.apps.xhs.usecases import chat

        return chat(self, message)

    def search(self, keyword: str, sort_by: str = "最多点赞") -> List[Post]:
        """搜索帖子"""
        return self.channel.search(keyword, sort_by)

    def publish(
        self, title: str, content: str, images: List[str], tags: List[str] | None = None
    ) -> PublishResult:
        """发布帖子"""
        return self.channel.publish(title, content, images, tags)

    def generate_content(self, keyword: str) -> Dict:
        """AI 生成内容"""
        from xiaohongshu_agent.apps.xhs.usecases import generate_content

        return generate_content(self, keyword)

    def get_stats(self) -> Dict:
        """获取统计"""
        return self.db.get_stats()

    def clear_memory(self):
        """清空记忆"""
        self.memory.clear()

    def get_memory_status(self) -> Dict:
        """获取记忆状态"""
        return {
            "count": self.memory.count(),
            "limit": 50,
        }
