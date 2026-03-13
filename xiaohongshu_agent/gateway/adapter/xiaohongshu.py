"""
Gateway 与 XiaohongshuAgent 集成适配器
"""
import asyncio
from typing import Dict, Any, Optional, List

from xiaohongshu_agent.gateway.types import Agent, AgentStatus, AgentResponse, AgentContext
from xiaohongshu_agent.agent.memory import Memory
from xiaohongshu_agent.storage.database import Database


class XiaohongshuAgentAdapter:
    """XiaohongshuAgent 适配器 - 将现有 Agent 转换为 Gateway Agent"""

    def __init__(
        self,
        xiaohongshu_agent: Any,
        memory: Optional[Memory] = None
    ):
        self.agent = xiaohongshu_agent
        self.memory = memory

    async def handle_chat(self, message: Any, context: AgentContext) -> AgentResponse:
        """处理聊天消息"""
        try:
            # 调用原有的 chat 方法
            content = await asyncio.to_thread(self.agent.chat, message.content)

            return AgentResponse(
                content=content,
                metadata={
                    "provider": self.agent.provider.get_name() if self.agent.provider else None,
                    "model": self.agent.provider.model if self.agent.provider else None,
                }
            )
        except Exception as e:
            return AgentResponse(
                content=f"处理消息失败: {str(e)}",
                metadata={"error": str(e)}
            )

    async def handle_generate(self, keyword: str, context: AgentContext) -> AgentResponse:
        """处理内容生成"""
        try:
            result = await asyncio.to_thread(self.agent.generate_content, keyword)

            return AgentResponse(
                content=str(result),
                metadata={"keyword": keyword}
            )
        except Exception as e:
            return AgentResponse(
                content=f"生成失败: {str(e)}",
                metadata={"error": str(e)}
            )

    async def handle_search(self, keyword: str, context: AgentContext) -> AgentResponse:
        """处理搜索"""
        try:
            posts = await asyncio.to_thread(self.agent.search, keyword)

            # 格式化结果
            results = []
            for post in posts[:5]:
                results.append(f"📝 {post.title} (👍{post.likes})")

            content = "\n".join(results) if results else "未找到相关笔记"

            return AgentResponse(
                content=content,
                metadata={"keyword": keyword, "count": len(posts)}
            )
        except Exception as e:
            return AgentResponse(
                content=f"搜索失败: {str(e)}",
                metadata={"error": str(e)}
            )

    async def handle_stats(self, context: AgentContext) -> AgentResponse:
        """处理统计查询"""
        try:
            stats = await asyncio.to_thread(self.agent.get_stats)

            content = f"""📊 数据统计

- 已发布笔记: {stats.published_posts}
- 总点赞: {stats.total_likes}
- 总评论: {stats.total_comments}
- 已回复评论: {stats.replied_comments}
- 知识库条目: {stats.knowledge_items}"""

            return AgentResponse(content=content, metadata={})
        except Exception as e:
            return AgentResponse(
                content=f"获取统计失败: {str(e)}",
                metadata={"error": str(e)}
            )

    def to_gateway_agent(
        self,
        agent_id: str = "xiaohongshu",
        name: str = "Xiaohongshu Agent",
        description: str = "小红书 AI 运营助手"
    ) -> Agent:
        """转换为 Gateway Agent"""

        async def handler(message: Any, context: AgentContext) -> AgentResponse:
            content = message.content.lower()

            # 根据关键词路由到不同处理函数
            if content.startswith("生成:") or content.startswith("generate:"):
                keyword = content.replace("generate:", "").replace("生成:", "").strip()
                return await self.handle_generate(keyword, context)

            elif content.startswith("搜索:") or content.startswith("search:"):
                keyword = content.replace("search:", "").replace("搜索:", "").strip()
                return await self.handle_search(keyword, context)

            elif content in ["统计", "stats", "数据"]:
                return await self.handle_stats(context)

            else:
                # 默认走聊天
                return await self.handle_chat(message, context)

        return Agent(
            id=agent_id,
            name=name,
            description=description,
            version="1.0.0",
            status=AgentStatus.ONLINE,
            capabilities=[
                type('Cap', (), {'name': 'chat', 'description': '对话'})(),
                type('Cap', (), {'name': 'generate', 'description': '生成内容'})(),
                type('Cap', (), {'name': 'search', 'description': '搜索笔记'})(),
                type('Cap', (), {'name': 'stats', 'description': '数据统计'})(),
            ],
            handler=handler
        )


def create_xiaohongshu_gateway_agent(
    xiaohongshu_agent: Any,
    agent_id: str = "xiaohongshu"
) -> Agent:
    """创建小红书 Gateway Agent 的便捷函数"""
    adapter = XiaohongshuAgentAdapter(xiaohongshu_agent)
    return adapter.to_gateway_agent(agent_id)
