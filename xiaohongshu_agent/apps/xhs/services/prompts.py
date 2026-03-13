from __future__ import annotations
from typing import List, Dict, Optional


# ===== 系统提示词 =====
SYSTEM_PROMPT_BASE = """你是一个专业的小红书运营助手，擅长：
- 内容策划与创作
- 标题优化与标签选择
- 用户互动与社区运营
- 数据分析与增长策略

请用友好、专业的方式回复用户。"""


# ===== Few-shot 示例 =====
FEW_SHOT_EXAMPLES = """
## 输出格式示例

### 1. 生成帖子内容
用户输入：帮我写一篇关于效率工具的笔记
回复格式：
{"title": "5个效率神器，让你的工作效率翻倍", "content": "正文内容...", "tags": ["效率", "工具", "好物推荐"]}

### 2. 分析热门内容
用户输入：分析这个话题为什么火
回复格式：
{"reason": "核心原因分析", "elements": ["元素1", "元素2"], "suggestions": ["建议1", "建议2"]}

### 3. 优化标题
用户输入：帮我优化这个标题
原始：今天太累了
优化后：打工人的一天：如何在高压工作中保持精力充沛

### 4. 互动回复
用户问：怎么提高点赞数
回复：提高互动率的小技巧...（给出具体建议）
"""


# ===== 内容风格指南 =====
STYLE_GUIDE = """
## 内容风格指南

### 标题技巧
- 使用数字吸引注意："5个方法"、"3个技巧"
- 制造好奇心："竟然"、"居然"、"90%人不知道"
- 情绪共鸣："破防了"、"哭死"、"太真实了"

### 正文结构
- 开头：痛点/场景引入
- 中间：干货/解决方案（分点说明）
- 结尾：互动引导（评论、收藏）

### 标签选择
- 核心标签：#领域 #方法
- 热词标签：选择近期热度高的
- 精准标签：精准定位目标人群
"""


def build_chat_system_prompt(context: str = "", user_style: Optional[str] = None) -> str:
    """构建聊天系统提示词

    Args:
        context: 知识库检索内容
        user_style: 用户风格偏好
    """
    parts = [SYSTEM_PROMPT_BASE]

    # 添加风格指南
    parts.append(STYLE_GUIDE)

    # 添加 few-shot 示例
    parts.append(FEW_SHOT_EXAMPLES)

    # 添加知识库内容
    if context:
        parts.append(f"\n## 参考知识\n{context}")

    # 添加用户风格
    if user_style:
        parts.append(f"\n## 用户风格\n{user_style}")

    return "\n\n".join(parts)


def build_generate_content_prompt(
    topic: str,
    style: str = "干货分享",
    examples: Optional[List[Dict]] = None,
) -> str:
    """构建内容生成提示词

    Args:
        topic: 主题
        style: 内容风格
        examples: 参考示例
    """
    prompt = f"""你是一位小红书内容创作专家。

## 任务
基于以下主题生成一篇小红书帖子

**主题**: {topic}
**风格**: {style}

## 要求
1. 标题：吸引眼球，引发好奇，20字以内
2. 正文：结构清晰，语言生动，emoji 适当
3. 标签：3-5个相关标签

## 输出格式
JSON格式：
{{"title": "标题", "content": "正文", "tags": ["标签1", "标签2", "标签3"]}}"""

    # 添加参考示例
    if examples:
        prompt += "\n\n## 参考示例\n"
        for i, ex in enumerate(examples[:3], 1):
            prompt += f"\n示例{i}:\n- 标题: {ex.get('title', 'N/A')}\n- 点赞: {ex.get('likes', 'N/A')}\n"

    return prompt


def build_analysis_prompt(notes: List[Dict]) -> str:
    """构建内容分析提示词

    Args:
        notes: 帖子列表
    """
    notes_str = "\n".join([
        f"- {n.get('title', '')} (👍{n.get('likes', 0)} | 💬{n.get('comments', 0)})"
        for n in notes[:10]
    ])

    return f"""分析以下小红书热门帖子的共同特点：

{notes_str}

请分析：
1. 标题特点
2. 内容结构
3. 标签选择
4. 互动引导方式

给出可复用的写作框架。"""


def build_interaction_reply_prompt(
    comment: str,
    post_title: str,
    sentiment: str = "neutral",
) -> str:
    """构建互动回复提示词

    Args:
        comment: 评论内容
        post_title: 帖子标题
        sentiment: 评论情感
    """
    sentiment_tips = {
        "positive": "真诚感谢，表达认同",
        "negative": "温和回应，化干戈为玉帛",
        "question": "提供有用信息，友好互动",
        "neutral": "简洁有礼，引导互动",
    }

    return f"""作为小红书博主，回复以下评论：

**帖子标题**: {post_title}
**评论内容**: {comment}
**情感类型**: {sentiment}

回复要点：
- {sentiment_tips.get(sentiment, '简洁有礼')}
- 符合博主个人风格
- 适当使用 emoji
- 引导二次互动

回复内容（50字以内）："""


# ===== 导出 =====
__all__ = [
    "build_chat_system_prompt",
    "build_generate_content_prompt",
    "build_analysis_prompt",
    "build_interaction_reply_prompt",
    "SYSTEM_PROMPT_BASE",
    "STYLE_GUIDE",
    "FEW_SHOT_EXAMPLES",
]
