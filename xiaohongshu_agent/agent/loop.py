"""
Agent 主循环
"""
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

from xiaohongshu_agent.providers import create_provider
from xiaohongshu_agent.storage import Database
from xiaohongshu_agent.channels.xiaohongshu import XiaohongshuChannel
from xiaohongshu_agent.agent.context import Context
from xiaohongshu_agent.agent.memory import Memory


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
        self.knowledge = self._load_knowledge()

        print(f"✓ LLM: {provider}/{model}")
        print(f"✓ MCP: {mcp_url}")
        print(f"✓ 数据库: {db_path}")
        print(f"✓ 对话历史: {self.memory.count()} 条")

    def _load_knowledge(self) -> List[Dict]:
        """加载内置知识"""
        return [
            {"content": "小红书标题技巧：使用数字+悬念+关键词，如'5个方法让你的笔记爆火'", "category": "运营"},
            {"content": "小红书热门时间段：早上7-9点，中午12-14点，晚上20-24点", "category": "运营"},
            {"content": "小红书标签选择：选择1-2个泛标签+2-3个精准标签", "category": "内容"},
            {"content": "AI Agent 是企业的数字化员工，可以自动化处理重复性工作", "category": "AI"},
            {"content": "企业搭建 AI Agent 的5个核心要素：明确场景、选择能力、构建知识库、设计工作流、持续优化", "category": "AI"},
            {"content": "高质量小红书内容的3个要素：利他性、真实性、情感共鸣", "category": "内容"},
        ]

    def chat(self, message: str) -> str:
        """处理对话"""
        # 获取对话历史
        history = self.memory.get_history()

        # 检索知识
        context = self._retrieve_knowledge(message)

        # 构建提示词
        system_prompt = self._build_prompt(context)
        messages = [{"role": "system", "content": system_prompt}]

        # 添加历史
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # 添加当前消息
        messages.append({"role": "user", "content": message})

        # 调用 LLM
        response = self.provider.chat(messages)

        # 保存对话
        self.memory.add_message("user", message)
        self.memory.add_message("assistant", response)

        return response

    def _retrieve_knowledge(self, query: str) -> str:
        """检索知识库"""
        # 简单的关键词匹配
        results = []
        query_words = set(query.lower().split())

        for item in self.knowledge:
            content_words = set(item["content"].lower().split())
            overlap = len(query_words & content_words)
            if overlap > 0:
                results.append((overlap, item["content"]))

        results.sort(key=lambda x: x[0], reverse=True)
        return "\n".join([r[1] for r in results[:3]])

    def _build_prompt(self, context: str) -> str:
        """构建提示词"""
        prompt = "你是一个专业的小红书运营助手。"
        if context:
            prompt += f"\n\n参考知识:\n{context}"
        return prompt

    def search(self, keyword: str, sort_by: str = "最多点赞") -> List[Dict]:
        """搜索帖子"""
        return self.channel.search(keyword, sort_by)

    def publish(self, title: str, content: str, images: List[str], tags: List[str] = None) -> Dict:
        """发布帖子"""
        return self.channel.publish(title, content, images, tags)

    def generate_content(self, keyword: str) -> Dict:
        """AI 生成内容"""
        posts = self.search(keyword)

        if not posts:
            return {
                "title": f"{keyword} 深度解析",
                "content": f"关于 {keyword} 的分享...",
                "tags": [keyword, "科技", "干货"]
            }

        # 基于热门内容生成
        top_titles = "\n".join([f"- {p['title']}" for p in posts[:3]])
        prompt = f"""基于以下小红书热门帖子标题：
{top_titles}

请帮我生成一篇新的小红书帖子内容，包括标题、正文、标签。JSON格式：
{{"title": "标题", "content": "正文", "tags": ["标签1", "标签2"]}}"""

        try:
            response = self.provider.chat([{"role": "user", "content": prompt}])
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass

        return {
            "title": f"{keyword} 深度解析",
            "content": f"关于 {keyword} 的分享...",
            "tags": [keyword, "科技", "干货"]
        }

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
