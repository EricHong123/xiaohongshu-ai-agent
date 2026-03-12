from __future__ import annotations


def build_chat_system_prompt(context: str) -> str:
    prompt = "你是一个专业的小红书运营助手。"
    if context:
        prompt += f"\n\n参考知识:\n{context}"
    return prompt


def build_generate_content_prompt(top_titles: str) -> str:
    return f"""基于以下小红书热门帖子标题：
{top_titles}

请帮我生成一篇新的小红书帖子内容，包括标题、正文、标签。JSON格式：
{{"title": "标题", "content": "正文", "tags": ["标签1", "标签2"]}}"""

