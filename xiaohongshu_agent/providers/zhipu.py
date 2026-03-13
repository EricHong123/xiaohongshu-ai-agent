"""
智谱 GLM 提供商
支持重试机制
"""
import os
import logging
import requests
from typing import List, Dict, Any, Optional

from xiaohongshu_agent.providers.base import BaseProvider
from xiaohongshu_agent.providers.retry import RetryConfig, with_retry

logger = logging.getLogger(__name__)


class ZhipuProvider(BaseProvider):
    """智谱 GLM LLM 提供商"""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "",
        model: str = "glm-4",
        retry_config: Optional[RetryConfig] = None,
    ):
        super().__init__(api_key, base_url, model, retry_config)
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY", "")
        self.base_url = base_url or os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
        self.model = model or os.getenv("ZHIPU_MODEL", "glm-4")

    @with_retry(max_attempts=3, min_wait=2, max_wait=10)
    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """发送聊天请求（带重试）"""
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
            logger.error(f"智谱 API 调用失败: {e}")
            raise  # 让重试装饰器处理

    def get_name(self) -> str:
        return "智谱 GLM"
