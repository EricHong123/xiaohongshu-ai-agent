"""
腾讯混元 (Tencent Hunyuan) 提供商
"""
import os
import requests
from typing import List, Dict, Any

from xiaohongshu_agent.providers.base import BaseProvider


class TencentProvider(BaseProvider):
    """腾讯混元 LLM 提供商"""

    def __init__(self, api_key: str = "", base_url: str = "", model: str = "hunyuan-pro"):
        super().__init__(api_key, base_url, model)
        self.api_key = api_key or os.getenv("TENCENT_API_KEY", "")
        self.secret_id = os.getenv("TENCENT_SECRET_ID", "")
        self.secret_key = os.getenv("TENCENT_SECRET_KEY", "")
        self.model = model or os.getenv("TENCENT_MODEL", "hunyuan-pro")

    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """发送聊天请求"""
        try:
            # 腾讯混元使用腾讯云SDK或直接调用API
            # 这里使用直接调用API的方式

            headers = {
                "Content-Type": "application/json"
            }

            # 转换为腾讯混元格式
            # messages 需要反转,最新的在最后
            msgs = []
            for msg in messages:
                role = msg.get("role", "user")
                if role == "system":
                    role = "system"
                msgs.append({
                    "role": role,
                    "content": msg.get("content", "")
                })

            data = {
                "model": self.model,
                "messages": msgs,
                "stream": False
            }

            # 使用腾讯云CAM签名或API Key
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            # 腾讯混元API地址
            base_url = "hunyuan.tencentcloudapi.com"

            resp = requests.post(
                f"https://{base_url}",
                headers=headers,
                json=data,
                timeout=30
            )

            result = resp.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")

        except Exception as e:
            return f"腾讯混元 调用失败: {e}"

    def get_name(self) -> str:
        return "腾讯混元"
