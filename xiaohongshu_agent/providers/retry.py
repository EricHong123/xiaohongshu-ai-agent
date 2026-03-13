"""
LLM 提供商重试装饰器
提供指数退避重试机制，提高 API 调用可靠性
"""
import functools
import logging
import time
from typing import Callable, TypeVar, Any

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log,
)

logger = logging.getLogger(__name__)

# 可重试的异常类型
RETRY_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    OSError,
)

# 默认配置
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_MIN_WAIT = 1  # 最小等待 1 秒
DEFAULT_MAX_WAIT = 10  # 最大等待 10 秒
DEFAULT_MULTIPLIER = 2  # 指数退避倍数


def with_retry(
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    min_wait: int = DEFAULT_MIN_WAIT,
    max_wait: int = DEFAULT_MAX_WAIT,
    multiplier: int = DEFAULT_MULTIPLIER,
    retry_on: tuple = RETRY_EXCEPTIONS,
):
    """
    LLM 调用重试装饰器

    Args:
        max_attempts: 最大重试次数
        min_wait: 最小等待秒数
        max_wait: 最大等待秒数
        multiplier: 指数退避倍数
        retry_on: 需要重试的异常类型元组

    Example:
        @with_retry(max_attempts=3, min_wait=2, max_wait=10)
        def chat(self, messages):
            return self._call_api(messages)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 创建重试装饰器
            retry_decorator = retry(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential(
                    multiplier=multiplier,
                    min=min_wait,
                    max=max_wait,
                ),
                retry=retry_if_exception_type(retry_on),
                before_sleep=before_sleep_log(logger, logging.WARNING),
                after=after_log(logger, logging.INFO),
                reraise=True,
            )

            retry_func = retry_decorator(func)
            return retry_func(*args, **kwargs)

        return wrapper
    return decorator


class RetryConfig:
    """重试配置类"""

    def __init__(
        self,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        min_wait: int = DEFAULT_MIN_WAIT,
        max_wait: int = DEFAULT_MAX_WAIT,
        multiplier: int = DEFAULT_MULTIPLIER,
        enabled: bool = True,
    ):
        self.max_attempts = max_attempts
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.multiplier = multiplier
        self.enabled = enabled

    def to_dict(self) -> dict:
        return {
            "max_attempts": self.max_attempts,
            "min_wait": self.min_wait,
            "max_wait": self.max_wait,
            "multiplier": self.multiplier,
            "enabled": self.enabled,
        }


# 全局默认配置
DEFAULT_RETRY_CONFIG = RetryConfig()


def get_default_retry_config() -> RetryConfig:
    """获取默认重试配置"""
    return DEFAULT_RETRY_CONFIG
