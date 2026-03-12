"""
Agent bootstrap: load config and build a ready-to-use XiaohongshuAgent.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from xiaohongshu_agent import XiaohongshuAgent
from xiaohongshu_agent.config import load_config


@dataclass(frozen=True)
class AgentWiring:
    provider: str
    model: str
    api_key: str
    mcp_url: str


def build_agent(
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    mcp_url: Optional[str] = None,
) -> XiaohongshuAgent:
    """
    Build agent from config + overrides.

    Behavior should remain identical to the previous CLI wiring:
    - load config
    - optionally export provider API key env var for downstream libs
    - construct XiaohongshuAgent(provider/model/api_key/mcp_url)
    """

    cfg = load_config()

    resolved_provider = provider or cfg.get("llm_provider", "openai")
    resolved_model = model or cfg.get_model()
    resolved_api_key = api_key if api_key is not None else cfg.get_api_key()
    resolved_mcp_url = mcp_url or cfg.get("mcp_url", "http://localhost:18060/mcp")

    if resolved_api_key:
        os.environ[f"{resolved_provider.upper()}_API_KEY"] = resolved_api_key

    return XiaohongshuAgent(
        provider=resolved_provider,
        model=resolved_model,
        api_key=resolved_api_key,
        mcp_url=resolved_mcp_url,
    )


def resolve_wiring() -> AgentWiring:
    """Expose resolved wiring for debugging/printing without constructing the agent."""
    cfg = load_config()
    provider = cfg.get("llm_provider", "openai")
    return AgentWiring(
        provider=provider,
        model=cfg.get_model(),
        api_key=cfg.get_api_key(),
        mcp_url=cfg.get("mcp_url", "http://localhost:18060/mcp"),
    )

