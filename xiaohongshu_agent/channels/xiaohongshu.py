"""
小红书渠道 - 优化版
- 无代理直连
- 重试机制
- 超时处理
- 详细日志
"""
import os
import json
import time
from typing import List, Dict, Any, Optional
from functools import wraps
import requests

from xiaohongshu_agent.utils.logger import get_logger

logger = get_logger("mcp")


def retry_on_error(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟（秒）
        backoff: 延迟倍数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"{func.__name__} 失败 (尝试 {attempt + 1}/{max_retries}): {e}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"{func.__name__} 重试 {max_retries} 次后仍然失败: {e}")

            raise last_exception

        return wrapper
    return decorator


class MCPError(Exception):
    """MCP 相关错误"""
    def __init__(self, message: str, code: str = None, details: Any = None):
        super().__init__(message)
        self.code = code
        self.details = details


class XiaohongshuChannel:
    """小红书 MCP 渠道 - 优化版"""

    def __init__(
        self,
        mcp_url: str = "http://localhost:18060/mcp",
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        self.url = mcp_url
        self.timeout = timeout
        self.max_retries = max_retries

        # 创建不使用代理的 session
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.proxies = {'http': None, 'https': None}

        self.session_id = None
        self._initialized = False

        logger.info(f"初始化 MCP 渠道: {mcp_url}")

    @retry_on_error(max_retries=3, delay=1.0)
    def _init(self):
        """初始化 MCP 连接"""
        if self._initialized:
            return

        logger.debug("初始化 MCP 连接...")

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

        try:
            resp = self._send_request(req)
            if "result" in resp:
                self._initialized = True
                server_info = resp.get("result", {}).get("serverInfo", {})
                logger.info(
                    f"MCP 连接成功: {server_info.get('name')} v{server_info.get('version')}"
                )
            else:
                logger.warning(f"MCP 初始化响应异常: {resp}")
        except Exception as e:
            logger.error(f"MCP 初始化失败: {e}")
            raise MCPError(f"MCP 初始化失败: {e}", code="INIT_FAILED")

    def _send_request(self, req: Dict, timeout: float = None) -> Dict:
        """发送请求"""
        timeout = timeout or self.timeout

        headers = {"Content-Type": "application/json"}
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        try:
            resp = self.session.post(
                self.url,
                json=req,
                headers=headers,
                proxies={'http': None, 'https': None},
                timeout=timeout
            )

            # 处理 session ID
            if "Mcp-Session-Id" in resp.headers:
                self.session_id = resp.headers["Mcp-Session-Id"]

            if resp.status_code == 200:
                result = resp.json()
                if "error" in result:
                    error = result["error"]
                    logger.error(f"MCP 错误: {error}")
                    raise MCPError(
                        error.get("message", "未知错误"),
                        code=error.get("code"),
                        details=error
                    )
                return result
            else:
                logger.error(f"MCP HTTP 错误: {resp.status_code} - {resp.text}")
                raise MCPError(f"HTTP {resp.status_code}: {resp.text}", code="HTTP_ERROR")

        except requests.exceptions.Timeout:
            logger.error(f"MCP 请求超时 ({timeout}s)")
            raise MCPError(f"请求超时", code="TIMEOUT")
        except requests.exceptions.ConnectionError:
            logger.error(f"MCP 连接失败: {self.url}")
            raise MCPError(f"连接失败: {self.url}", code="CONNECTION_ERROR")
        except Exception as e:
            logger.error(f"MCP 请求异常: {e}")
            raise MCPError(f"请求异常: {e}", code="REQUEST_ERROR")

    def _call(self, method: str, tool_name: str = None, tool_args: dict = None) -> Dict:
        """调用 MCP 方法"""
        # 确保已初始化
        if not self._initialized:
            self._init()

        req = {
            "jsonrpc": "2.0",
            "method": method,
            "params": {"name": tool_name, "arguments": tool_args or {}},
            "id": 2
        }

        logger.debug(f"MCP 调用: {method} ({tool_name})")

        try:
            result = self._send_request(req)
            logger.debug(f"MCP 响应成功")
            return result
        except MCPError:
            raise
        except Exception as e:
            logger.error(f"MCP 调用异常: {e}")
            raise MCPError(f"调用失败: {e}", code="CALL_FAILED")

    def check_login(self) -> Dict:
        """检查登录状态"""
        logger.info("检查小红书登录状态...")
        try:
            result = self._call("tools/call", tool_name="check_login_status", tool_args={})
            if "result" in result:
                text = result["result"]["content"][0]["text"]
                logger.info(f"登录状态: {text}")
                return {"success": True, "message": text}
            return {"success": False, "message": "无法获取登录状态"}
        except MCPError as e:
            logger.error(f"检查登录失败: {e}")
            return {"success": False, "message": str(e)}

    def search(
        self,
        keyword: str,
        sort_by: str = "最多点赞",
        publish_time: str = "不限"
    ) -> List[Dict]:
        """搜索帖子"""
        logger.info(f"搜索帖子: {keyword} (排序: {sort_by})")

        try:
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

                    logger.info(f"找到 {len(posts)} 条帖子")
                    return posts
                except json.JSONDecodeError as e:
                    logger.error(f"解析搜索结果失败: {e}")
                    return []
                except Exception as e:
                    logger.error(f"处理搜索结果失败: {e}")
                    return []

            return []
        except MCPError as e:
            logger.error(f"搜索失败: {e}")
            return []

    def publish(
        self,
        title: str,
        content: str,
        images: List[str],
        tags: List[str] = None
    ) -> Dict:
        """发布帖子"""
        logger.info(f"发布帖子: {title[:20]}...")

        args = {"title": title, "content": content, "images": images}
        if tags:
            args["tags"] = tags

        try:
            result = self._call("tools/call", tool_name="publish_content", tool_args=args)

            if "result" in result:
                logger.info("发布成功!")
                return {"success": True, "result": result}
            return {"success": False, "error": "发布失败"}

        except MCPError as e:
            logger.error(f"发布失败: {e}")
            return {"success": False, "error": str(e)}

    def get_feed_detail(self, feed_id: str, xsec_token: str) -> Dict:
        """获取帖子详情"""
        return self._call(
            "tools/call",
            tool_name="get_feed_detail",
            tool_args={"feed_id": feed_id, "xsec_token": xsec_token}
        )

    def close(self):
        """关闭连接"""
        if self.session:
            self.session.close()
            logger.info("MCP 连接已关闭")
