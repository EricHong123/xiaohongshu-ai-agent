from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

from xiaohongshu_agent.apps.xhs.services.knowledge import retrieve_knowledge
from xiaohongshu_agent.apps.xhs.services.prompts import build_chat_system_prompt

if TYPE_CHECKING:
    from xiaohongshu_agent import XiaohongshuAgent


def chat(agent: "XiaohongshuAgent", message: str) -> str:
    history = agent.memory.get_history()
    context = retrieve_knowledge(getattr(agent, "knowledge", []) or [], message)

    system_prompt = build_chat_system_prompt(context)
    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    response = agent.provider.chat(messages)

    agent.memory.add_message("user", message)
    agent.memory.add_message("assistant", response)
    return response

