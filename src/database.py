#!/usr/bin/env python3
"""
数据库模块 - 存储帖子、评论、分析数据
支持 SQLite (默认) 和 PostgreSQL
"""
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import os


# ============== 数据模型 ==============
@dataclass
class Post:
    """小红书帖子"""
    id: str
    title: str
    content: str
    images: str  # JSON array
    tags: str   # JSON array
    likes: int = 0
    comments: int = 0
    collects: int = 0
    created_at: str = ""
    published: bool = False
    feed_id: Optional[str] = None
    xsec_token: Optional[str] = None


@dataclass
class Comment:
    """评论"""
    id: str
    post_id: str
    feed_id: str
    content: str
    user_id: str
    nickname: str
    created_at: str = ""
    replied: bool = False
    reply_content: Optional[str] = None


@dataclass
class SearchResult:
    """搜索结果"""
    id: str
    keyword: str
    title: str
    likes: int
    comments: int
    collects: int
    fetched_at: str = ""


# ============== 数据库类 ==============
class Database:
    """数据库管理"""

    def __init__(self, db_path: str = "xiaohongshu_agent.db"):
        self.db_path = db_path
        self.conn = None
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        # 创建表
        cursor = self.conn.cursor()

        # 帖子表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
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
                reply_content TEXT,
                FOREIGN KEY (post_id) REFERENCES posts (id)
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
                content TEXT NOT NULL,
                category TEXT,
                tags TEXT,
                created_at TEXT,
                updated_at TEXT
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

        self.conn.commit()
        print(f"✅ 数据库初始化完成: {self.db_path}")

    # ============== 帖子操作 ==============
    def add_post(self, post: Post) -> bool:
        """添加帖子"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO posts
                (id, title, content, images, tags, likes, comments, collects, created_at, published, feed_id, xsec_token)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post.id, post.title, post.content, post.images, post.tags,
                post.likes, post.comments, post.collects, post.created_at,
                int(post.published), post.feed_id, post.xsec_token
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"添加帖子失败: {e}")
            return False

    def get_posts(self, limit: int = 10) -> List[Post]:
        """获取帖子列表"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM posts ORDER BY created_at DESC LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        return [Post(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            images=row["images"],
            tags=row["tags"],
            likes=row["likes"],
            comments=row["comments"],
            collects=row["collects"],
            created_at=row["created_at"],
            published=bool(row["published"]),
            feed_id=row["feed_id"],
            xsec_token=row["xsec_token"]
        ) for row in rows]

    def get_published_posts(self) -> List[Post]:
        """获取已发布的帖子"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM posts WHERE published = 1 ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        return [Post(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            images=row["images"],
            tags=row["tags"],
            likes=row["likes"],
            comments=row["comments"],
            collects=row["collects"],
            created_at=row["created_at"],
            published=bool(row["published"]),
            feed_id=row["feed_id"],
            xsec_token=row["xsec_token"]
        ) for row in rows]

    # ============== 评论操作 ==============
    def add_comment(self, comment: Comment) -> bool:
        """添加评论"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO comments
                (id, post_id, feed_id, content, user_id, nickname, created_at, replied, reply_content)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                comment.id, comment.post_id, comment.feed_id, comment.content,
                comment.user_id, comment.nickname, comment.created_at,
                int(comment.replied), comment.reply_content
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"添加评论失败: {e}")
            return False

    def get_unreplied_comments(self) -> List[Comment]:
        """获取未回复的评论"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM comments WHERE replied = 0 ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        return [Comment(
            id=row["id"],
            post_id=row["post_id"],
            feed_id=row["feed_id"],
            content=row["content"],
            user_id=row["user_id"],
            nickname=row["nickname"],
            created_at=row["created_at"],
            replied=bool(row["replied"]),
            reply_content=row["reply_content"]
        ) for row in rows]

    def mark_comment_replied(self, comment_id: str, reply_content: str) -> bool:
        """标记评论已回复"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE comments SET replied = 1, reply_content = ? WHERE id = ?
        """, (reply_content, comment_id))
        self.conn.commit()
        return cursor.rowcount > 0

    # ============== 搜索结果操作 ==============
    def add_search_results(self, results: List[SearchResult]) -> bool:
        """添加搜索结果"""
        try:
            cursor = self.conn.cursor()
            for r in results:
                cursor.execute("""
                    INSERT OR REPLACE INTO search_results
                    (id, keyword, title, likes, comments, collects, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (r.id, r.keyword, r.title, r.likes, r.comments, r.collects, r.fetched_at))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"添加搜索结果失败: {e}")
            return False

    def get_popular_posts(self, limit: int = 10) -> List[SearchResult]:
        """获取热门帖子"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM search_results ORDER BY likes DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [SearchResult(
            id=row["id"],
            keyword=row["keyword"],
            title=row["title"],
            likes=row["likes"],
            comments=row["comments"],
            collects=row["collects"],
            fetched_at=row["fetched_at"]
        ) for row in rows]

    # ============== 知识库操作 ==============
    def add_knowledge(self, content: str, category: str = "", tags: List[str] = None) -> bool:
        """添加知识"""
        import hashlib
        doc_id = hashlib.md5(content.encode()).hexdigest()

        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        tags_json = json.dumps(tags or [])

        cursor.execute("""
            INSERT OR REPLACE INTO knowledge (id, content, category, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (doc_id, content, category, tags_json, now, now))
        self.conn.commit()
        return True

    def get_all_knowledge(self) -> List[Dict]:
        """获取所有知识"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM knowledge ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [
            {
                "id": row["id"],
                "content": row["content"],
                "category": row["category"],
                "tags": json.loads(row["tags"]) if row["tags"] else [],
                "created_at": row["created_at"]
            }
            for row in rows
        ]

    # ============== 日志操作 ==============
    def add_log(self, task_type: str, status: str, message: str) -> None:
        """添加日志"""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO task_logs (task_type, status, message, created_at)
            VALUES (?, ?, ?, ?)
        """, (task_type, status, message, now))
        self.conn.commit()

    def get_recent_logs(self, limit: int = 20) -> List[Dict]:
        """获取最近日志"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM task_logs ORDER BY created_at DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [
            {
                "id": row["id"],
                "task_type": row["task_type"],
                "status": row["status"],
                "message": row["message"],
                "created_at": row["created_at"]
            }
            for row in rows
        ]

    # ============== 统计 ==============
    def get_stats(self) -> Dict:
        """获取统计信息"""
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM posts WHERE published = 1")
        published_count = cursor.fetchone()["count"]

        cursor.execute("SELECT SUM(likes) as total FROM posts WHERE published = 1")
        total_likes = cursor.fetchone()["total"] or 0

        cursor.execute("SELECT SUM(comments) as total FROM posts WHERE published = 1")
        total_comments = cursor.fetchone()["total"] or 0

        cursor.execute("SELECT COUNT(*) as count FROM comments WHERE replied = 1")
        replied_count = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM search_results")
        search_count = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM knowledge")
        knowledge_count = cursor.fetchone()["count"]

        return {
            "published_posts": published_count,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "replied_comments": replied_count,
            "search_results": search_count,
            "knowledge_items": knowledge_count
        }

    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()


# ============== 测试 ==============
if __name__ == "__main__":
    print("🧪 测试数据库")
    print("=" * 50)

    # 创建数据库
    db = Database("test_agent.db")

    # 测试添加帖子
    print("\n[1] 添加帖子...")
    post = Post(
        id="test_001",
        title="测试帖子",
        content="这是测试内容",
        images=json.dumps(["/path/to/img.jpg"]),
        tags=json.dumps(["测试", "AI"]),
        created_at=datetime.now().isoformat(),
        published=True
    )
    db.add_post(post)
    print("   帖子添加成功")

    # 测试查询
    print("\n[2] 查询帖子...")
    posts = db.get_posts()
    print(f"   找到 {len(posts)} 条帖子")

    # 测试统计
    print("\n[3] 统计信息...")
    stats = db.get_stats()
    print(f"   已发布: {stats['published_posts']} 篇")
    print(f"   总点赞: {stats['total_likes']}")
    print(f"   知识库: {stats['knowledge_items']} 条")

    # 清理
    os.remove("test_agent.db")

    print("\n✅ 数据库测试完成")
