"""
智谱 GLM 提供商
"""
import os
import requests
from typing import List, Dict, Any

from xiaohongshu_agent.providers.base import BaseProvider


class ZhipuProvider(BaseProvider):
    """智谱 GLM LLM 提供商"""

    def __init__(self, api_key: str = "", base_url: str = "", model: str = "glm-4"):
        super().__init__(api_key, base_url, model)
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY", "")
        self.base_url = base_url or os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
        self.model = model or os.getenv("ZHIPU_MODEL", "glm-4")

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
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"智谱调用失败: {e}"

    def get_name(self) -> str:
        return "智谱 GLM"
