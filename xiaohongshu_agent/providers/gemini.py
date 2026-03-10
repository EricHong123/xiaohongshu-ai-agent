"""
Google Gemini 提供商
"""
import os
import requests
from typing import List, Dict, Any

from xiaohongshu_agent.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    """Google Gemini LLM 提供商"""

    def __init__(self, api_key: str = "", base_url: str = "", model: str = "gemini-2.0-flash"):
        super().__init__(api_key, base_url, model)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.base_url = base_url or os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """发送聊天请求"""
        try:
            # 提取 system 和 user 消息
            system_content = ""
            user_content = ""

            for msg in messages:
                if msg["role"] == "system":
                    system_content = msg["content"]
                elif msg["role"] == "user":
                    user_content = msg["content"]

            # 构建 prompt
            if system_content:
                full_prompt = f"{system_content}\n\n用户: {user_content}"
            else:
                full_prompt = user_content

            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{
                    "parts": [{"text": full_prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2000,
                }
            }

            resp = requests.post(url, headers=headers, json=data, timeout=30)

            if resp.status_code == 200:
                result = resp.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return f"Gemini API 错误: {resp.status_code} - {resp.text}"

        except Exception as e:
            return f"Gemini 调用失败: {e}"

    def get_name(self) -> str:
        return "Google Gemini"
