"""
搜索服务
"""
from typing import TYPE_CHECKING, List

from xiaohongshu_agent.domain import Post
from xiaohongshu_agent.services.constants import DEFAULT_SORT_BY

if TYPE_CHECKING:
    from xiaohongshu_agent import XiaohongshuAgent


def search_notes(agent: "XiaohongshuAgent", keyword: str, *, sort_by: str = DEFAULT_SORT_BY) -> List[Post]:
    """搜索笔记"""
    return agent.search(keyword, sort_by=sort_by)
