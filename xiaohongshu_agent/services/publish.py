"""
发布服务
"""
from typing import TYPE_CHECKING, List, Optional

from xiaohongshu_agent.domain import PublishResult

if TYPE_CHECKING:
    from xiaohongshu_agent import XiaohongshuAgent


def publish_note(
    agent: "XiaohongshuAgent",
    *,
    title: str,
    content: str,
    images: List[str],
    tags: Optional[List[str]] = None,
) -> PublishResult:
    """发布笔记"""
    return agent.publish(title, content, images, tags)
