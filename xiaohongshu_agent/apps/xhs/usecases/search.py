from __future__ import annotations

from typing import TYPE_CHECKING, List

from xiaohongshu_agent.domain import Post
from xiaohongshu_agent.apps.xhs.services.constants import DEFAULT_SORT_BY

if TYPE_CHECKING:
    from xiaohongshu_agent import XiaohongshuAgent


def search_posts(agent: "XiaohongshuAgent", keyword: str, *, sort_by: str = DEFAULT_SORT_BY) -> List[Post]:
    return agent.search(keyword, sort_by=sort_by)

