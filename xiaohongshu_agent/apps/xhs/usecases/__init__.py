"""
Xiaohongshu usecases: thin business layer callable by CLI/Web/API.
"""

from .chat import chat
from .content import generate_content
from .publish import publish_post
from .search import search_posts
from .stats import get_stats

__all__ = ["search_posts", "publish_post", "get_stats", "generate_content", "chat"]

