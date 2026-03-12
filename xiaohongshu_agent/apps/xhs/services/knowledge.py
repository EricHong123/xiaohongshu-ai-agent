from __future__ import annotations

from typing import Dict, List

from xiaohongshu_agent.apps.xhs.services.prompts import build_chat_system_prompt

def load_knowledge() -> List[Dict[str, str]]:
    return [
        {"content": "小红书标题技巧：使用数字+悬念+关键词，如'5个方法让你的笔记爆火'", "category": "运营"},
        {"content": "小红书热门时间段：早上7-9点，中午12-14点，晚上20-24点", "category": "运营"},
        {"content": "小红书标签选择：选择1-2个泛标签+2-3个精准标签", "category": "内容"},
        {"content": "AI Agent 是企业的数字化员工，可以自动化处理重复性工作", "category": "AI"},
        {
            "content": "企业搭建 AI Agent 的5个核心要素：明确场景、选择能力、构建知识库、设计工作流、持续优化",
            "category": "AI",
        },
        {"content": "高质量小红书内容的3个要素：利他性、真实性、情感共鸣", "category": "内容"},
    ]


def retrieve_knowledge(knowledge: List[Dict[str, str]], query: str) -> str:
    results: List[tuple[int, str]] = []
    query_words = set(query.lower().split())

    for item in knowledge or []:
        content = (item.get("content") or "").strip()
        if not content:
            continue
        content_words = set(content.lower().split())
        overlap = len(query_words & content_words)
        if overlap > 0:
            results.append((overlap, content))

    results.sort(key=lambda x: x[0], reverse=True)
    return "\n".join([r[1] for r in results[:3]])


def build_system_prompt(context: str) -> str:
    # Backward compatible name; delegates to prompts service.
    return build_chat_system_prompt(context)

