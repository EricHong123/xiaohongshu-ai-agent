"""
对话记忆模块
"""
from typing import List, Dict, Any
from datetime import datetime

from xiaohongshu_agent.apps.xhs.services.constants import DEFAULT_MEMORY_LIMIT, DEFAULT_MEMORY_TTL_DAYS


class Memory:
    """对话记忆"""

    def __init__(self, db, limit: int = DEFAULT_MEMORY_LIMIT, ttl_days: int = DEFAULT_MEMORY_TTL_DAYS):
        self.db = db
        self.limit = limit
        self.ttl_days = ttl_days

    def add_message(self, role: str, content: str):
        """添加消息"""
        self.db.add_chat_message(role, content)

    def get_history(self, limit: int = DEFAULT_MEMORY_LIMIT) -> List[Dict]:
        """获取历史"""
        return self.db.get_chat_history(limit)

    def count(self) -> int:
        """获取消息数量"""
        return self.db.get_chat_history_count()

    def clear(self):
        """清空记忆"""
        self.db.clear_chat_history()

    def cleanup_expired(self) -> int:
        """清理过期的对话记忆

        Returns:
            删除的消息数量
        """
        return self.db.cleanup_expired_chat_history(self.ttl_days)

    def get_status(self) -> Dict:
        """获取记忆状态"""
        return {
            "count": self.count(),
            "limit": self.limit,
            "ttl_days": self.ttl_days,
        }
