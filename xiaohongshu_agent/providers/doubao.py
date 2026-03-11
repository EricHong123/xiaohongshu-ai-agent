"""
豆包 (Doubao) 提供商 - 字节跳动
"""
import os
import requests
from typing import List, Dict, Any

from xiaohongshu_agent.providers.base import BaseProvider


class DoubaoProvider(BaseProvider):
    """豆包 LLM 提供商 - 字节跳动"""

    def __init__(self, api_key: str = "", base_url: str = "", model: str = "doubao-pro-32k"):
        super().__init__(api_key, base_url, model)
        self.api_key = api_key or os.getenv("DOUBAO_API_KEY", "")
        self.base_url = base_url or os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        self.model = model or os.getenv("DOUBAO_MODEL", "doubao-pro-32k")

    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """发送聊天请求"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "messages": messages
            }

            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            result = resp.json()
            return result["choices"][0]["message"]["content"]

        except Exception as e:
            return f"豆包 调用失败: {e}"

    def get_name(self) -> str:
        return "豆包"
