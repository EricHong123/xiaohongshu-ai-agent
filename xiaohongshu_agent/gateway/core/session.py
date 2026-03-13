"""
会话管理器
参考 ai-agent-gateway/src/core/session.ts
"""
import uuid
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import asdict

from xiaohongshu_agent.gateway.types import Session, SessionContext, UnifiedMessage


class SessionManager:
    """会话管理器"""

    def __init__(
        self,
        config: Optional[Dict] = None,
        logger: Optional[Any] = None
    ):
        self.config = config or {}
        self.logger = logger
        self.sessions: Dict[str, Session] = {}

        # 配置项
        self.max_history = self.config.get("maxHistory", 50)
        self.max_age_hours = self.config.get("maxAgeHours", 24)
        self.context_window = self.config.get("contextWindow", 10)

    def create(self, user_id: str, channel: str, session_id: Optional[str] = None) -> Session:
        """创建会话"""
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]

        session = Session(
            id=session_id or str(uuid.uuid4()),
            userId=user_id,
            channel=channel,
            context=SessionContext(),
            createdAt=datetime.now(),
            updatedAt=datetime.now()
        )

        self.sessions[session.id] = session
        self._log("info", "Session created", session_id=session.id, user_id=user_id)
        return session

    def get(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self.sessions.get(session_id)

    def update(self, session_id: str, updates: Dict) -> bool:
        """更新会话"""
        session = self.sessions.get(session_id)
        if not session:
            return False

        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)

        session.updatedAt = datetime.now()
        return True

    def add_message(self, session_id: str, role: str, content: str) -> bool:
        """添加消息到会话"""
        session = self.sessions.get(session_id)
        if not session:
            return False

        session.context.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # 截断历史
        if len(session.context.messages) > self.max_history:
            session.context.messages = session.context.messages[-self.max_history:]

        session.updatedAt = datetime.now()
        return True

    def get_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """获取会话历史"""
        session = self.sessions.get(session_id)
        if not session:
            return []

        limit = limit or self.context_window
        return session.context.messages[-limit:]

    def delete(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._log("info", "Session deleted", session_id=session_id)
            return True
        return False

    def cleanup(self) -> int:
        """清理过期会话"""
        now = datetime.now()
        expired = []

        for session_id, session in self.sessions.items():
            age = now - session.updatedAt
            if age > timedelta(hours=self.max_age_hours):
                expired.append(session_id)

        for session_id in expired:
            del self.sessions[session_id]

        if expired:
            self._log("info", "Sessions cleaned", count=len(expired))

        return len(expired)

    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "total": len(self.sessions),
            "by_channel": self._count_by_channel(),
            "oldest_session": self._get_oldest(),
        }

    def _count_by_channel(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for session in self.sessions.values():
            counts[session.channel] = counts.get(session.channel, 0) + 1
        return counts

    def _get_oldest(self) -> Optional[str]:
        if not self.sessions:
            return None
        oldest = min(self.sessions.values(), key=lambda s: s.createdAt)
        return oldest.id

    def _log(self, level: str, message: str, **kwargs):
        if self.logger:
            getattr(self.logger, level)(message, **kwargs)
