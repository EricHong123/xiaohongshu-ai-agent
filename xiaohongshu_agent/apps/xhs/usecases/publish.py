from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from xiaohongshu_agent.domain import PublishResult

if TYPE_CHECKING:
    from xiaohongshu_agent import XiaohongshuAgent


def publish_post(
    agent: "XiaohongshuAgent",
    *,
    title: str,
    content: str,
    images: List[str],
    tags: Optional[List[str]] = None,
) -> PublishResult:
    return agent.publish(title, content, images, tags)

