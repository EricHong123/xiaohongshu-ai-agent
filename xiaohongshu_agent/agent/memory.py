"""
对话记忆模块
"""
from typing import List, Dict, Any
from datetime import datetime

from xiaohongshu_agent.apps.xhs.services.constants import DEFAULT_MEMORY_LIMIT


class Memory:
    """对话记忆"""

    def __init__(self, db):
        self.db = db
        self.limit = DEFAULT_MEMORY_LIMIT

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
