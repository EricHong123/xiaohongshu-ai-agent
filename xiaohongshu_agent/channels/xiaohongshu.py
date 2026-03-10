"""
小红书渠道
"""
import os
import json
from typing import List, Dict, Any, Optional
import requests


class XiaohongshuChannel:
    """小红书 MCP 渠道"""

    def __init__(self, mcp_url: str = "http://localhost:18060/mcp"):
        self.url = mcp_url

        # 创建不使用代理的 session
        self.session = requests.Session()
        # 禁用环境变量代理
        self.session.trust_env = False

        # 确保不使用代理
        self.session.proxies = {
            'http': None,
            'https': None
        }

        self.session_id = None

    def _call(self, method: str, tool_name: str = None, tool_args: dict = None) -> Dict:
        """调用 MCP"""
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

        # 直接请求，不使用代理
        resp = self.session.post(
            self.url,
            json=req,
            headers=headers,
            proxies={'http': None, 'https': None},
            timeout=30
        )

        if "Mcp-Session-Id" in resp.headers:
            self.session_id = resp.headers["Mcp-Session-Id"]

        return resp.json() if resp.status_code == 200 else {"error": resp.text}

    def _init(self):
        """初始化"""
        req = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "xiaohongshu_agent", "version": "1.1.0"}
            },
            "id": 1
        }

        headers = {"Content-Type": "application/json"}

        resp = self.session.post(
            self.url,
            json=req,
            headers=headers,
            proxies={'http': None, 'https': None},
            timeout=30
        )

        if "Mcp-Session-Id" in resp.headers:
            self.session_id = resp.headers["Mcp-Session-Id"]

    def check_login(self) -> Dict:
        """检查登录状态"""
        return self._call("tools/call", tool_name="check_login_status", tool_args={})

    def search(self, keyword: str, sort_by: str = "最多点赞", publish_time: str = "不限") -> List[Dict]:
        """搜索帖子"""
        result = self._call(
            "tools/call",
            tool_name="search_feeds",
            tool_args={
                "keyword": keyword,
                "filters": {"sort_by": sort_by, "publish_time": publish_time}
            }
        )

        if "result" in result:
            try:
                text = result["result"]["content"][0]["text"]
                data = json.loads(text)
                feeds = data.get("feeds", [])

                posts = []
                for feed in feeds:
                    card = feed.get("noteCard", {})
                    interact = card.get("interactInfo", {})
                    posts.append({
                        "id": feed.get("id"),
                        "title": card.get("displayTitle", ""),
                        "likes": int(interact.get("likedCount", "0") or 0),
                        "comments": int(interact.get("commentCount", "0") or 0),
                        "collects": int(interact.get("collectedCount", "0") or 0),
                    })
                return posts
            except Exception as e:
                print(f"搜索解析错误: {e}")

        return []

    def publish(self, title: str, content: str, images: List[str], tags: List[str] = None) -> Dict:
        """发布帖子"""
        args = {"title": title, "content": content, "images": images}
        if tags:
            args["tags"] = tags

        result = self._call("tools/call", tool_name="publish_content", tool_args=args)
        return result

    def get_feed_detail(self, feed_id: str, xsec_token: str) -> Dict:
        """获取帖子详情"""
        return self._call(
            "tools/call",
            tool_name="get_feed_detail",
            tool_args={"feed_id": feed_id, "xsec_token": xsec_token}
        )
