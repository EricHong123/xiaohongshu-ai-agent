"""
Minimax 提供商
"""
import os
import requests
from typing import List, Dict, Any

from xiaohongshu_agent.providers.base import BaseProvider


class MinimaxProvider(BaseProvider):
    """Minimax LLM 提供商"""

    def __init__(self, api_key: str = "", base_url: str = "", model: str = "abab6.5s-chat"):
        super().__init__(api_key, base_url, model)
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY", "")
        self.base_url = base_url or os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
        self.model = model or os.getenv("MINIMAX_MODEL", "abab6.5s-chat")

    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """发送聊天请求"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # 转换消息格式
            processed_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    processed_messages.insert(0, {"role": "system", "content": msg["content"]})
                else:
                    processed_messages.append({"role": msg["role"], "content": msg["content"]})

            data = {
                "model": self.model,
                "messages": processed_messages,
                "temperature": 0.7,
                "max_tokens": 2000,
            }

            resp = requests.post(
                f"{self.base_url}/text/chatcompletion_v2",
                headers=headers,
                json=data,
                timeout=30
            )

            if resp.status_code == 200:
                result = resp.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"Minimax API 错误: {resp.status_code} - {resp.text}"

        except Exception as e:
            return f"Minimax 调用失败: {e}"

    def get_name(self) -> str:
        return "Minimax"
