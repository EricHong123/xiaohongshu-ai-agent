"""
Anthropic (Claude) 提供商
支持重试机制
"""
import os
import logging
from typing import List, Dict, Any, Optional

from xiaohongshu_agent.providers.base import BaseProvider
from xiaohongshu_agent.providers.retry import RetryConfig, with_retry

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseProvider):
    """Anthropic Claude LLM 提供商"""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "",
        model: str = "claude-sonnet-4-20250514",
        retry_config: Optional[RetryConfig] = None,
    ):
        super().__init__(api_key, base_url, model, retry_config)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    @with_retry(max_attempts=3, min_wait=2, max_wait=10)
    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """发送聊天请求（带重试）"""
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
            logger.error(f"Anthropic API 调用失败: {e}")
            raise  # 让重试装饰器处理

    def get_name(self) -> str:
        return "Anthropic"
