from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Post:
    id: str | None
    title: str
    likes: int = 0
    comments: int = 0
    collects: int = 0


@dataclass(frozen=True, slots=True)
class PublishResult:
    success: bool
    error: str | None = None
    raw: object | None = None


@dataclass(frozen=True, slots=True)
class Stats:
    published_posts: int = 0
    total_likes: int = 0
    total_comments: int = 0
    replied_comments: int = 0
    knowledge_items: int = 0

