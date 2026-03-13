"""
数据库模块
"""
import json
import hashlib
import sqlite3
from datetime import datetime
from typing import List, Dict, Any

from xiaohongshu_agent.domain import Stats

class Database:
    """SQLite 数据库"""

    def __init__(self, db_path: str = "xiaohongshu_agent.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        """初始化表"""
        cursor = self.conn.cursor()

        # 帖子表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                title TEXT,
                content TEXT,
                images TEXT,
                tags TEXT,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                collects INTEGER DEFAULT 0,
                created_at TEXT,
                published INTEGER DEFAULT 0,
                feed_id TEXT,
                xsec_token TEXT
            )
        """)

        # 评论表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id TEXT PRIMARY KEY,
                post_id TEXT,
                feed_id TEXT,
                content TEXT,
                user_id TEXT,
                nickname TEXT,
                created_at TEXT,
                replied INTEGER DEFAULT 0,
                reply_content TEXT
            )
        """)

        # 搜索结果表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_results (
                id TEXT PRIMARY KEY,
                keyword TEXT,
                title TEXT,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                collects INTEGER DEFAULT 0,
                fetched_at TEXT
            )
        """)

        # 知识库表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id TEXT PRIMARY KEY,
                content TEXT,
                category TEXT,
                tags TEXT,
                created_at TEXT
            )
        """)

        # 任务日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT,
                status TEXT,
                message TEXT,
                created_at TEXT
            )
        """)

        # 对话历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT,
                created_at TEXT
            )
        """)

        self.conn.commit()

    # ===== 对话历史 =====
    def add_chat_message(self, role: str, content: str):
        """添加对话消息"""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO chat_history (role, content, created_at) VALUES (?, ?, ?)",
            (role, content, now)
        )
        self.conn.commit()

    def get_chat_history(self, limit: int = 50) -> List[Dict]:
        """获取对话历史"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT role, content, created_at FROM chat_history ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        results = cursor.fetchall()
        return list(reversed([{"role": r[0], "content": r[1], "created_at": r[2]} for r in results]))

    def get_chat_history_count(self) -> int:
        """获取对话历史数量"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        return cursor.fetchone()[0]

    def clear_chat_history(self):
        """清空对话历史"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM chat_history")
        self.conn.commit()

    def cleanup_expired_chat_history(self, ttl_days: int = 30):
        """清理过期的对话历史

        Args:
            ttl_days: 保留天数，默认 30 天
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM chat_history WHERE created_at < datetime('now', '-' || ? || ' days')",
            (ttl_days,)
        )
        deleted = cursor.rowcount
        self.conn.commit()
        return deleted

    # ===== 帖子 =====
    def add_post(self, post: Dict):
        """添加帖子"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO posts
            (id, title, content, images, tags, likes, comments, collects, created_at, published, feed_id, xsec_token)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post.get("id"),
            post.get("title"),
            post.get("content"),
            post.get("images"),
            post.get("tags"),
            post.get("likes", 0),
            post.get("comments", 0),
            post.get("collects", 0),
            post.get("created_at"),
            int(post.get("published", False)),
            post.get("feed_id"),
            post.get("xsec_token")
        ))
        self.conn.commit()

    # ===== 搜索结果 =====
    def add_search_results(self, results: List[Dict]):
        """添加搜索结果"""
        cursor = self.conn.cursor()
        for r in results:
            cursor.execute("""
                INSERT OR REPLACE INTO search_results
                (id, keyword, title, likes, comments, collects, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                r.get("id"),
                r.get("keyword"),
                r.get("title"),
                r.get("likes", 0),
                r.get("comments", 0),
                r.get("collects", 0),
                r.get("fetched_at")
            ))
        self.conn.commit()

    # ===== 统计 =====
    def get_stats(self) -> Stats:
        """获取统计"""
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM posts WHERE published = 1")
        published = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(likes) FROM posts WHERE published = 1")
        total_likes = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(comments) FROM posts WHERE published = 1")
        total_comments = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM comments WHERE replied = 1")
        replied = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM knowledge")
        knowledge = cursor.fetchone()[0] or 0

        return Stats(
            published_posts=int(published),
            total_likes=int(total_likes),
            total_comments=int(total_comments),
            replied_comments=int(replied),
            knowledge_items=int(knowledge),
        )

    def close(self):
        """关闭连接"""
        self.conn.close()
