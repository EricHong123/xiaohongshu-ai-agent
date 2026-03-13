"""
内容生成服务
"""
import json
from typing import TYPE_CHECKING, Dict

from xiaohongshu_agent.services.prompts import build_generate_content_prompt

if TYPE_CHECKING:
    from xiaohongshu_agent import XiaohongshuAgent


def generate_content(agent: "XiaohongshuAgent", keyword: str) -> Dict:
    """
    基于搜索结果生成笔记内容

    返回格式:
    {"title": str, "content": str, "tags": list[str]}
    """
    posts = agent.search(keyword)

    if not posts:
        return {
            "title": f"{keyword} 深度解析",
            "content": f"关于 {keyword} 的分享...",
            "tags": [keyword, "科技", "干货"],
        }

    top_titles = "\n".join([f"- {p.title}" for p in posts[:3]])
    prompt = build_generate_content_prompt(top_titles)

    try:
        response = agent.provider.chat([{"role": "user", "content": prompt}])
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except Exception:
        pass

    return {
        "title": f"{keyword} 深度解析",
        "content": f"关于 {keyword} 的分享...",
        "tags": [keyword, "科技", "干货"],
    }
