"""
LLM 提供商基类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar

from xiaohongshu_agent.providers.retry import (
    RetryConfig,
    get_default_retry_config,
    with_retry,
)

T = TypeVar('T')


class BaseProvider(ABC):
    """LLM 提供商基类"""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "",
        model: str = "",
        retry_config: Optional[RetryConfig] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.retry_config = retry_config or get_default_retry_config()

    @abstractmethod
    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """发送聊天请求"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """获取提供商名称"""
        pass

    def _create_retry_decorator(self, max_attempts: Optional[int] = None):
        """创建重试装饰器"""
        config = self.retry_config
        if not config.enabled:
            return lambda f: f

        return with_retry(
            max_attempts=max_attempts or config.max_attempts,
            min_wait=config.min_wait,
            max_wait=config.max_wait,
            multiplier=config.multiplier,
        )

    def get_retry_info(self) -> dict:
        """获取重试配置信息"""
        return {
            "enabled": self.retry_config.enabled,
            "max_attempts": self.retry_config.max_attempts,
            "min_wait": self.retry_config.min_wait,
            "max_wait": self.retry_config.max_wait,
        }
