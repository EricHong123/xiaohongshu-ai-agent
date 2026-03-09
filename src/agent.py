#!/usr/bin/env python3
"""
小红书 AI Agent - 主类 (简化版)
"""
import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import sqlite3
import requests


# ============== 配置 ==============
class LLMConfig:
    def __init__(self, provider="openai", api_key="", base_url=None, model="gpt-4"):
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = 0.7
        self.max_tokens = 2000


def get_llm_config():
    provider = os.getenv("LLM_PROVIDER", "openai")
    configs = {
        "openai": LLMConfig(provider="openai", api_key=os.getenv("OPENAI_API_KEY", ""), model="gpt-4"),
        "anthropic": LLMConfig(provider="anthropic", api_key=os.getenv("ANTHROPIC_API_KEY", ""), model="claude-sonnet-4-20250514"),
        "zhipu": LLMConfig(provider="zhipu", api_key=os.getenv("ZHIPU_API_KEY", ""), model="glm-4"),
        "minimax": LLMConfig(provider="minimax", api_key=os.getenv("MINIMAX_API_KEY", ""), model="abab6.5s-chat"),
        "kimi": LLMConfig(provider="kimi", api_key=os.getenv("KIMI_API_KEY", ""), model="kimi-flash-1.5"),
        "gemini": LLMConfig(provider="gemini", api_key=os.getenv("GEMINI_API_KEY", ""), model="gemini-2.0-flash"),
    }
    return configs.get(provider, configs["openai"])


# ============== LLM 适配器 ==============
class LLMAdapter:
    def __init__(self, config):
        self.config = config

    def chat(self, messages, **kwargs):
        return "LLM 功能需要安装对应库并配置 API Key"


class OpenAIAdapter(LLMAdapter):
    def __init__(self, config):
        super().__init__(config)

    def chat(self, messages, **kwargs):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.config.api_key)
            response = client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000),
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI 调用失败: {e}"


class AnthropicAdapter(LLMAdapter):
    def __init__(self, config):
        super().__init__(config)

    def chat(self, messages, **kwargs):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.config.api_key)
            system = messages[0]["content"] if messages[0]["role"] == "system" else ""
            user_msgs = [m for m in messages if m["role"] != "system"]
            response = client.messages.create(
                model=self.config.model,
                system=system,
                messages=user_msgs,
            )
            return response.content[0].text
        except Exception as e:
            return f"Anthropic 调用失败: {e}"


class ZhipuAdapter(LLMAdapter):
    def __init__(self, config):
        super().__init__(config)

    def chat(self, messages, **kwargs):
        try:
            headers = {"Authorization": f"Bearer {self.config.api_key}", "Content-Type": "application/json"}
            data = {"model": self.config.model, "messages": messages}
            resp = requests.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                headers=headers, json=data
            )
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"智谱调用失败: {e}"


class KimiAdapter(LLMAdapter):
    def __init__(self, config):
        super().__init__(config)

    def chat(self, messages, **kwargs):
        try:
            headers = {"Authorization": f"Bearer {self.config.api_key}", "Content-Type": "application/json"}
            data = {"model": self.config.model, "messages": messages}
            resp = requests.post(
                "https://api.moonshot.cn/v1/chat/completions",
                headers=headers, json=data
            )
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Kimi 调用失败: {e}"


def create_llm_adapter(config):
    adapters = {
        "openai": OpenAIAdapter,
        "anthropic": AnthropicAdapter,
        "zhipu": ZhipuAdapter,
        "kimi": KimiAdapter,
    }
    adapter_class = adapters.get(config.provider, LLMAdapter)
    return adapter_class(config)


# ============== RAG 系统 ==============
class Document:
    def __init__(self, id, content, metadata):
        self.id = id
        self.content = content
        self.metadata = metadata


class InMemoryVectorDB:
    def __init__(self):
        self.documents = []

    def add_documents(self, documents):
        self.documents.extend(documents)

    def similarity_search(self, query, top_k=5):
        query_words = set(query.lower().split())
        scored = []
        for doc in self.documents:
            doc_words = set(doc.content.lower().split())
            overlap = len(query_words & doc_words)
            if overlap > 0:
                scored.append((overlap, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]


class RAGSystem:
    def __init__(self):
        self.vector_db = InMemoryVectorDB()
        self.knowledge_base = []

    def add_knowledge(self, content, metadata):
        doc_id = hashlib.md5(content.encode()).hexdigest()
        doc = Document(doc_id, content, metadata)
        self.knowledge_base.append(doc)
        self.vector_db.add_documents([doc])

    def retrieve(self, query, top_k=5):
        return self.vector_db.similarity_search(query, top_k)


# ============== 数据库 ==============
class Database:
    def __init__(self, db_path="xiaohongshu_agent.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY, title TEXT, content TEXT, images TEXT, tags TEXT,
                likes INTEGER DEFAULT 0, comments INTEGER DEFAULT 0, collects INTEGER DEFAULT 0,
                created_at TEXT, published INTEGER DEFAULT 0, feed_id TEXT, xsec_token TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id TEXT PRIMARY KEY, post_id TEXT, feed_id TEXT, content TEXT,
                user_id TEXT, nickname TEXT, created_at TEXT, replied INTEGER DEFAULT 0, reply_content TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_results (
                id TEXT PRIMARY KEY, keyword TEXT, title TEXT, likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0, collects INTEGER DEFAULT 0, fetched_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id TEXT PRIMARY KEY, content TEXT, category TEXT, tags TEXT, created_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT, task_type TEXT, status TEXT, message TEXT, created_at TEXT
            )
        """)
        # 对话历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT, created_at TEXT
            )
        """)
        self.conn.commit()

    def add_search_results(self, results):
        cursor = self.conn.cursor()
        for r in results:
            cursor.execute("""
                INSERT OR REPLACE INTO search_results (id, keyword, title, likes, comments, collects, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (r["id"], r["keyword"], r["title"], r["likes"], r["comments"], r["collects"], r.get("fetched_at", "")))
        self.conn.commit()

    def add_post(self, post):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO posts (id, title, content, images, tags, likes, comments, collects, created_at, published, feed_id, xsec_token)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (post.id, post.title, post.content, post.images, post.tags, post.likes, post.comments, post.collects, post.created_at, int(post.published), post.feed_id, post.xsec_token))
        self.conn.commit()

    def add_comment(self, comment):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO comments (id, post_id, feed_id, content, user_id, nickname, created_at, replied, reply_content)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (comment.id, comment.post_id, comment.feed_id, comment.content, comment.user_id, comment.nickname, comment.created_at, int(comment.replied), comment.reply_content))
        self.conn.commit()

    def get_unreplied_comments(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM comments WHERE replied = 0")
        return [dict(row) for row in cursor.fetchall()]

    def get_all_knowledge(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM knowledge")
        return [dict(row) for row in cursor.fetchall()]

    def add_knowledge(self, content, category="", tags=None):
        doc_id = hashlib.md5(content.encode()).hexdigest()
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("INSERT OR REPLACE INTO knowledge VALUES (?, ?, ?, ?, ?)",
                      (doc_id, content, category, json.dumps(tags or []), now))
        self.conn.commit()

    def add_log(self, task_type, status, message):
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("INSERT INTO task_logs (task_type, status, message, created_at) VALUES (?, ?, ?, ?)",
                      (task_type, status, message, now))
        self.conn.commit()

    # ============== 对话历史 (Memory) ==============
    def add_message(self, role: str, content: str):
        """添加对话消息到历史"""
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
        return [{"role": row[0], "content": row[1], "created_at": row[2]} for row in cursor.fetchall()]

    def clear_chat_history(self):
        """清空对话历史"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM chat_history")
        self.conn.commit()

    def get_chat_history_count(self) -> int:
        """获取历史消息数量"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        return cursor.fetchone()[0]

    def get_stats(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as c FROM posts WHERE published = 1")
        published = cursor.fetchone()["c"]
        cursor.execute("SELECT SUM(likes) as s FROM posts WHERE published = 1")
        total_likes = cursor.fetchone()["s"] or 0
        cursor.execute("SELECT SUM(comments) as s FROM posts WHERE published = 1")
        total_comments = cursor.fetchone()["s"] or 0
        cursor.execute("SELECT COUNT(*) as c FROM comments WHERE replied = 1")
        replied = cursor.fetchone()["c"]
        cursor.execute("SELECT COUNT(*) as c FROM knowledge")
        knowledge = cursor.fetchone()["c"]
        return {
            "published_posts": published,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "replied_comments": replied,
            "knowledge_items": knowledge
        }

    def close(self):
        self.conn.close()


class Post:
    def __init__(self, id, title, content, images, tags, created_at="", published=False, feed_id=None, xsec_token=None):
        self.id = id
        self.title = title
        self.content = content
        self.images = images
        self.tags = tags
        self.likes = 0
        self.comments = 0
        self.collects = 0
        self.created_at = created_at or datetime.now().isoformat()
        self.published = published
        self.feed_id = feed_id
        self.xsec_token = xsec_token


class Comment:
    def __init__(self, id, post_id, feed_id, content, user_id, nickname, created_at="", replied=False, reply_content=None):
        self.id = id
        self.post_id = post_id
        self.feed_id = feed_id
        self.content = content
        self.user_id = user_id
        self.nickname = nickname
        self.created_at = created_at or datetime.now().isoformat()
        self.replied = replied
        self.reply_content = reply_content


# ============== MCP 客户端 ==============
class XiaohongshuMCP:
    def __init__(self, url="http://localhost:18060/mcp"):
        self.url = url
        self.session = requests.Session()
        self.session.trust_env = False
        self.session_id = None

    def _get_session_id(self, headers):
        return headers.get("Mcp-Session-Id")

    def _init(self):
        req = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "agent", "version": "1.0"}},
            "id": 1
        }
        resp = self.session.post(self.url, json=req)
        self.session_id = self._get_session_id(resp.headers)

    def call(self, method, tool_name=None, tool_args=None):
        if not self.session_id:
            self._init()
        req = {
            "jsonrpc": "2.0",
            "method": method,
            "params": {"name": tool_name, "arguments": tool_args or {}},
            "id": 2
        }
        headers = {"Content-Type": "application/json"}
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        resp = self.session.post(self.url, json=req, headers=headers)
        new_session_id = self._get_session_id(resp.headers)
        if new_session_id and new_session_id != self.session_id:
            self.session_id = new_session_id
        return resp.json() if resp.status_code == 200 else {"error": resp.text}

    def check_login(self):
        return self.call("tools/call", tool_name="check_login_status", tool_args={})

    def search_feeds(self, keyword, sort_by="最多点赞", publish_time="不限"):
        return self.call("tools/call", tool_name="search_feeds", tool_args={
            "keyword": keyword, "filters": {"sort_by": sort_by, "publish_time": publish_time}
        })

    def publish_content(self, title, content, images, tags=None, schedule_at=None):
        args = {"title": title, "content": content, "images": images}
        if tags: args["tags"] = tags
        if schedule_at: args["schedule_at"] = schedule_at
        return self.call("tools/call", tool_name="publish_content", tool_args=args)

    def get_feed_detail(self, feed_id, xsec_token):
        return self.call("tools/call", tool_name="get_feed_detail", tool_args={"feed_id": feed_id, "xsec_token": xsec_token})

    def reply_comment(self, feed_id, xsec_token, comment_id, user_id, content):
        return self.call("tools/call", tool_name="reply_comment_in_feed", tool_args={
            "feed_id": feed_id, "xsec_token": xsec_token, "comment_id": comment_id, "user_id": user_id, "content": content
        })


# ============== 主 Agent 类 ==============
class XiaohongshuAgent:
    """小红书 AI Agent"""

    def __init__(self, llm_provider=None, db_path="xiaohongshu_agent.db", mcp_url="http://localhost:18060/mcp"):
        print("\n🤖 初始化 AI Agent...")

        self.config = get_llm_config()
        self.llm = create_llm_adapter(self.config)
        print(f"   ✅ LLM: {self.config.provider} ({self.config.model})")

        self.rag = RAGSystem()
        # 添加默认知识
        default_knowledge = [
            ("小红书标题技巧：使用数字+悬念+关键词，如'5个方法让你的笔记爆火'", "运营"),
            ("小红书热门时间段：早上7-9点，中午12-14点，晚上20-24点", "运营"),
            ("小红书标签选择：选择1-2个泛标签+2-3个精准标签", "内容"),
            ("AI Agent 是企业的数字化员工，可以自动化处理重复性工作", "AI"),
            ("企业搭建 AI Agent 的5个核心要素：明确场景、选择能力、构建知识库、设计工作流、持续优化", "AI"),
            ("高质量小红书内容的3个要素：利他性、真实性、情感共鸣", "内容"),
        ]
        for content, category in default_knowledge:
            self.rag.add_knowledge(content, {"category": category})
        print(f"   ✅ RAG 知识库: {len(self.rag.knowledge_base)} 条")

        self.db = Database(db_path)
        print(f"   ✅ 数据库: {db_path}")

        # 对话历史 (Memory)
        self.chat_history_limit = 50  # 最多保存50条对话
        history_count = self.db.get_chat_history_count()
        print(f"   ✅ 对话历史: {history_count} 条")

        self.mcp = XiaohongshuMCP(mcp_url)
        print(f"   ✅ MCP: {mcp_url}")

        self._check_login()

        print("\n🎉 AI Agent 初始化完成!\n")

    def _check_login(self):
        try:
            status = self.mcp.check_login()
            if "result" in status:
                text = status["result"]["content"][0]["text"]
                print(f"   ✅ {text}")
        except Exception as e:
            print(f"   ⚠️ 登录检查失败: {e}")

    def chat(self, message):
        if not self.llm:
            return "LLM 未正确配置"

        # 获取对话历史 (Memory)
        history = self.db.get_chat_history(self.chat_history_limit)
        # 反转顺序，最新的在后面
        history = list(reversed(history))

        # 构建 RAG 上下文
        context = self.rag.retrieve(message)
        system_prompt = "你是一个专业的小红书运营助手。"
        if context:
            context_text = "\n".join([f"[{i+1}] {doc.content}" for i, doc in enumerate(context[:3])])
            system_prompt += f"\n\n参考知识:\n{context_text}"

        # 构建消息列表: system + 历史对话 + 当前消息
        messages = [{"role": "system", "content": system_prompt}]

        # 添加历史对话
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # 添加当前消息
        messages.append({"role": "user", "content": message})

        # 调用 LLM
        response = self.llm.chat(messages)

        # 保存对话到历史 (用户和AI的消息都保存)
        self.db.add_message("user", message)
        self.db.add_message("assistant", response)

        return response

    def clear_memory(self):
        """清空对话历史"""
        self.db.clear_chat_history()
        return "对话历史已清空"

    def get_memory_status(self):
        """获取记忆状态"""
        count = self.db.get_chat_history_count()
        return {"history_count": count, "limit": self.chat_history_limit}

    def search(self, keyword, sort_by="最多点赞"):
        try:
            result = self.mcp.search_feeds(keyword, sort_by=sort_by)
            if "result" in result:
                text = result["result"]["content"][0]["text"]
                data = json.loads(text)
                feeds = data.get("feeds", [])
                posts = []
                now = datetime.now().isoformat()
                for feed in feeds:
                    card = feed.get("noteCard", {})
                    interact = card.get("interactInfo", {})
                    post = {
                        "id": feed.get("id"),
                        "keyword": keyword,
                        "title": card.get("displayTitle", ""),
                        "likes": int(interact.get("likedCount", "0") or 0),
                        "comments": int(interact.get("commentCount", "0") or 0),
                        "collects": int(interact.get("collectedCount", "0") or 0),
                        "fetched_at": now
                    }
                    posts.append(post)
                self.db.add_search_results(posts)
                return posts
        except Exception as e:
            print(f"搜索失败: {e}")
        return []

    def generate_content(self, keyword):
        posts = self.search(keyword)
        if not posts:
            return {"title": f"{keyword} 深度解析", "content": f"关于 {keyword} 的分享...", "tags": [keyword, "科技", "干货"]}
        top_titles = "\n".join([f"- {p['title']}" for p in posts[:3]])
        prompt = f"""基于以下小红书热门帖子标题：
{top_titles}

请帮我生成一篇新的小红书帖子内容，包括标题、正文、标签。JSON格式：
{{"title": "标题", "content": "正文", "tags": ["标签1", "标签2"]}}"""
        try:
            response = self.llm.chat([{"role": "user", "content": prompt}])
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        return {"title": f"{keyword} 深度解析", "content": f"关于 {keyword} 的分享...", "tags": [keyword, "科技", "干货"]}

    def publish(self, content, images):
        if not images:
            return {"success": False, "error": "需要图片"}
        try:
            result = self.mcp.publish_content(
                title=content.get("title", "")[:20],
                content=content.get("content", ""),
                images=images,
                tags=content.get("tags", [])
            )
            if "result" in result:
                post = Post(
                    id=hashlib.md5(str(datetime.now()).encode()).hexdigest(),
                    title=content.get("title", ""),
                    content=content.get("content", ""),
                    images=json.dumps(images),
                    tags=json.dumps(content.get("tags", [])),
                    created_at=datetime.now().isoformat(),
                    published=True
                )
                self.db.add_post(post)
                return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
        return {"success": False, "error": "发布失败"}

    def auto_reply_comments(self):
        return {"replied_count": 0, "message": "功能开发中"}

    def get_stats(self):
        return self.db.get_stats()

    def get_knowledge(self):
        return self.db.get_all_knowledge()

    def add_knowledge(self, content, category=""):
        return self.db.add_knowledge(content, category)

    def get_config(self):
        return {"provider": self.config.provider, "model": self.config.model}

    def test_llm(self, prompt="你好"):
        return self.llm.chat([{"role": "user", "content": prompt}])


# ============== CLI 接口 ==============
def main():
    import argparse
    parser = argparse.ArgumentParser(description="小红书 AI Agent")
    parser.add_argument("-k", "--keyword", help="搜索关键词")
    parser.add_argument("-i", "--images", help="图片路径")
    parser.add_argument("--publish", action="store_true", help="发布帖子")
    parser.add_argument("--stats", action="store_true", help="查看统计")
    parser.add_argument("--chat", action="store_true", help="对话模式")
    args = parser.parse_args()

    agent = XiaohongshuAgent()

    if args.keyword:
        posts = agent.search(args.keyword)
        print(f"\n找到 {len(posts)} 条结果:\n")
        for i, p in enumerate(posts[:10], 1):
            print(f"  {i}. {p['title'][:40]}... [赞:{p['likes']}] [评:{p['comments']}] [藏:{p['collects']}]")

    if args.publish and args.keyword:
        images = args.images.split(",") if args.images else []
        if images:
            content = agent.generate_content(args.keyword)
            result = agent.publish(content, images)
            print(f"\n发布结果: {result}")
        else:
            print("\n发布需要图片路径: --images /path/to/image.jpg")

    if args.stats:
        stats = agent.get_stats()
        print("\n📊 统计信息:")
        print(f"  已发布帖子: {stats['published_posts']}")
        print(f"  总点赞: {stats['total_likes']}")
        print(f"  总评论: {stats['total_comments']}")
        print(f"  已回复: {stats['replied_comments']}")
        print(f"  知识库: {stats['knowledge_items']}")

    if args.chat:
        print("\n🤖 对话模式 (输入 'exit' 退出)\n")
        while True:
            user_input = input("你: ").strip()
            if user_input.lower() in ['exit', 'q']:
                break
            if user_input:
                response = agent.chat(user_input)
                print(f"\nAI: {response}\n")


if __name__ == "__main__":
    main()
