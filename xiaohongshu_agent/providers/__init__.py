"""
LLM 提供商模块
"""
from xiaohongshu_agent.providers.base import BaseProvider
from xiaohongshu_agent.providers.openai import OpenAIProvider
from xiaohongshu_agent.providers.anthropic import AnthropicProvider
from xiaohongshu_agent.providers.zhipu import ZhipuProvider
from xiaohongshu_agent.providers.kimi import KimiProvider
from xiaohongshu_agent.providers.minimax import MinimaxProvider
from xiaohongshu_agent.providers.gemini import GeminiProvider


PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "class": OpenAIProvider,
        "models": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ],
    },
    "anthropic": {
        "name": "Anthropic (Claude)",
        "class": AnthropicProvider,
        "models": [
            "claude-sonnet-4-20250514",
            "claude-sonnet-4-20250507",
            "claude-4-opus-20250514",
            "claude-4-sonnet-20250507",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ],
    },
    "zhipu": {
        "name": "智谱 GLM",
        "class": ZhipuProvider,
        "models": [
            "glm-4",
            "glm-4-flash",
            "glm-4-plus",
            "glm-3-turbo",
        ],
    },
    "kimi": {
        "name": "Kimi",
        "class": KimiProvider,
        "models": [
            "kimi-flash-1.5",
            "kimi-flash",
            "kimi-pro-1.5",
            "kimi-pro",
        ],
    },
    "minimax": {
        "name": "Minimax",
        "class": MinimaxProvider,
        "models": [
            "minimax-m2.5",
            "abab6.5s-chat",
            "abab6.5-chat",
            "abab5.5s-chat",
            "abab5.5-chat",
        ],
    },
    "gemini": {
        "name": "Google Gemini",
        "class": GeminiProvider,
        "models": [
            "gemini-2.0-flash",
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
        ],
    },
}


def create_provider(provider: str, api_key: str = "", base_url: str = "", model: str = "") -> BaseProvider:
    """创建 LLM 提供商"""
    provider_info = PROVIDERS.get(provider.lower())
    if not provider_info:
        provider_info = PROVIDERS["openai"]

    provider_class = provider_info["class"]
    return provider_class(api_key=api_key, base_url=base_url, model=model)


def get_available_providers() -> dict:
    """获取可用的提供商列表"""
    return PROVIDERS


__all__ = [
    "BaseProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "ZhipuProvider",
    "KimiProvider",
    "MinimaxProvider",
    "GeminiProvider",
    "create_provider",
    "get_available_providers",
]
