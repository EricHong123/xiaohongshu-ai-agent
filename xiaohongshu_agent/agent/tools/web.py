"""
网页搜索工具
"""
import requests
from typing import Dict, Any, List
from urllib.parse import quote_plus

from xiaohongshu_agent.agent.tools.base import Tool, ToolResult
from xiaohongshu_agent.agent.tools.registry import register_tool
from xiaohongshu_agent.utils.logger import get_logger

logger = get_logger("tools.web")


@register_tool("web_search")
class WebSearchTool(Tool):
    """网页搜索工具"""

    name = "web_search"
    description = "搜索网页内容"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def execute(self, query: str = None, engine: str = "ddg", num_results: int = 5, **kwargs) -> ToolResult:
        """搜索网页"""
        if not query:
            return ToolResult(success=False, error="缺少搜索关键词")

        try:
            logger.info(f"搜索: {query} (引擎: {engine})")

            if engine == "ddg" or engine == "duckduckgo":
                results = self._search_duckduckgo(query, num_results)
            elif engine == "bing":
                results = self._search_bing(query, num_results)
            elif engine == "google":
                results = self._search_google(query, num_results)
            else:
                results = self._search_duckduckgo(query, num_results)

            logger.info(f"找到 {len(results)} 条结果")

            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "engine": engine,
                    "results": results,
                    "count": len(results)
                }
            )
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return ToolResult(success=False, error=str(e))

    def _search_duckduckgo(self, query: str, num: int) -> List[Dict]:
        """DuckDuckGo 搜索"""
        try:
            # 使用 DuckDuckGo HTML 搜索
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }

            resp = requests.get(url, headers=headers, timeout=self.timeout)
            resp.raise_for_status()

            # 简单解析
            results = []
            import re
            # 匹配结果
            pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, resp.text)

            for url, title in matches[:num]:
                results.append({
                    "title": title.strip(),
                    "url": url
                })

            return results
        except Exception as e:
            logger.warning(f"DuckDuckGo 搜索失败: {e}")
            return []

    def _search_bing(self, query: str, num: int) -> List[Dict]:
        """Bing 搜索 (简化版)"""
        # 需要 API Key，这里返回空列表
        logger.warning("Bing 搜索需要 API Key")
        return []

    def _search_google(self, query: str, num: int) -> List[Dict]:
        """Google 搜索 (简化版)"""
        # 需要 API Key，这里返回空列表
        logger.warning("Google 搜索需要 API Key")
        return []

    def get_schema(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "engine": {"type": "string", "description": "搜索引擎 (ddg/bing/google)"},
                    "num_results": {"type": "number", "description": "结果数量"}
                },
                "required": ["query"]
            }
        }


@register_tool("web_fetch")
class WebFetchTool(Tool):
    """网页抓取工具"""

    name = "web_fetch"
    description = "获取网页内容"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def execute(self, url: str = None, **kwargs) -> ToolResult:
        """抓取网页"""
        if not url:
            return ToolResult(success=False, error="缺少 URL")

        # URL 安全检查
        if not url.startswith(("http://", "https://")):
            return ToolResult(success=False, error="URL 必须以 http:// 或 https:// 开头")

        try:
            logger.info(f"抓取网页: {url}")

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }

            resp = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            resp.raise_for_status()

            # 获取最终 URL
            final_url = resp.url

            # 简单处理：截取前 5000 字符
            content = resp.text[:5000]

            logger.info(f"网页抓取成功: {len(content)} 字符")

            return ToolResult(
                success=True,
                data={
                    "url": final_url,
                    "status_code": resp.status_code,
                    "content": content,
                    "content_type": resp.headers.get("Content-Type", "")
                }
            )
        except Exception as e:
            logger.error(f"网页抓取失败: {e}")
            return ToolResult(success=False, error=str(e))

    def get_schema(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "网页 URL"}
                },
                "required": ["url"]
            }
        }
