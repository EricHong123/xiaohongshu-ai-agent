"""
通义千问 (Qwen) 提供商 - 阿里云
"""
import os
import requests
from typing import List, Dict, Any

from xiaohongshu_agent.providers.base import BaseProvider


class QwenProvider(BaseProvider):
    """通义千问 LLM 提供商"""

    def __init__(self, api_key: str = "", base_url: str = "", model: str = "qwen-turbo"):
        super().__init__(api_key, base_url, model)
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY", "")  # 阿里云用 dashscope
        self.base_url = base_url or os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.model = model or os.getenv("QWEN_MODEL", "qwen-turbo")

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
            return f"通义千问 调用失败: {e}"

    def get_name(self) -> str:
        return "通义千问"
