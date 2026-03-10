"""
Anthropic (Claude) 提供商
"""
import os
from typing import List, Dict, Any

from xiaohongshu_agent.providers.base import BaseProvider


class AnthropicProvider(BaseProvider):
    """Anthropic Claude LLM 提供商"""

    def __init__(self, api_key: str = "", base_url: str = "", model: str = "claude-sonnet-4-20250514"):
        super().__init__(api_key, base_url, model)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """发送聊天请求"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            system = messages[0]["content"] if messages and messages[0]["role"] == "system" else ""
            user_msgs = [m for m in messages if m["role"] != "system"]

            response = client.messages.create(
                model=self.model,
                system=system,
                messages=user_msgs,
            )
            return response.content[0].text
        except Exception as e:
            return f"Anthropic 调用失败: {e}"

    def get_name(self) -> str:
        return "Anthropic"
