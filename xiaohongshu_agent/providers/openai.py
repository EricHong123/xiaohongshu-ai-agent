"""
OpenAI 提供商
"""
import os
from typing import List, Dict, Any

from xiaohongshu_agent.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    """OpenAI LLM 提供商"""

    def __init__(self, api_key: str = "", base_url: str = "", model: str = "gpt-4"):
        super().__init__(api_key, base_url, model)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4")

    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """发送聊天请求"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI 调用失败: {e}"

    def get_name(self) -> str:
        return "OpenAI"
