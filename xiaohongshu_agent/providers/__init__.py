"""
LLM 提供商模块
"""
from xiaohongshu_agent.providers.base import BaseProvider
from xiaohongshu_agent.providers.openai import OpenAIProvider
from xiaohongshu_agent.providers.anthropic import AnthropicProvider
from xiaohongshu_agent.providers.zhipu import ZhipuProvider
from xiaohongshu_agent.providers.kimi import KimiProvider


PROVIDERS = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "zhipu": ZhipuProvider,
    "kimi": KimiProvider,
}


def create_provider(provider: str, api_key: str = "", base_url: str = "", model: str = "") -> BaseProvider:
    """创建 LLM 提供商"""
    provider_class = PROVIDERS.get(provider.lower(), OpenAIProvider)
    return provider_class(api_key=api_key, base_url=base_url, model=model)


__all__ = [
    "BaseProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "ZhipuProvider",
    "KimiProvider",
    "create_provider",
]
