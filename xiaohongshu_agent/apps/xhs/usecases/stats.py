from __future__ import annotations

from typing import TYPE_CHECKING

from xiaohongshu_agent.domain import Stats

if TYPE_CHECKING:
    from xiaohongshu_agent import XiaohongshuAgent


def get_stats(agent: "XiaohongshuAgent") -> Stats:
    return agent.get_stats()

