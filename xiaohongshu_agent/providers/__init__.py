"""
LLM 提供商模块
"""
from xiaohongshu_agent.providers.base import BaseProvider
from xiaohongshu_agent.providers.retry import RetryConfig, get_default_retry_config
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
            # GPT-4.5
            "gpt-4.5-preview",
            # GPT-4o 系列
            "gpt-4o",
            "gpt-4o-2024-11-20",
            "gpt-4o-mini",
            "gpt-4o-mini-2024-07-18",
            # GPT-4 Turbo
            "gpt-4-turbo",
            "gpt-4-turbo-2024-04-09",
            # GPT-4
            "gpt-4",
            "gpt-4-32k",
            # o1 系列 (推理)
            "o1",
            "o1-mini",
            "o1-preview",
            "o3",
            "o3-mini",
            # GPT-3.5
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
        ],
    },
    "anthropic": {
        "name": "Anthropic (Claude)",
        "class": AnthropicProvider,
        "models": [
            # Claude 4.6 系列 (最新)
            "claude-opus-4-6-20251114",
            "claude-sonnet-4-6-20251114",
            "claude-4-opus-20250514",
            "claude-4-sonnet-20250514",
            "claude-4-haiku-20250514",
            # Claude 3.5 系列
            "claude-sonnet-3-5-20241022",
            "claude-sonnet-3-5-20240620",
            "claude-haiku-3-5-20240522",
            # Claude 3 系列
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ],
    },
    "zhipu": {
        "name": "智谱 GLM",
        "class": ZhipuProvider,
        "models": [
            # GLM-4 系列 (最新)
            "glm-4",
            "glm-4-flash",
            "glm-4-plus",
            "glm-4-air",
            "glm-4-airx",
            # GLM-4V 多模态
            "glm-4v",
            "glm-4v-flash",
            # GLM-3
            "glm-3-turbo",
        ],
    },
    "kimi": {
        "name": "Kimi (月之暗面)",
        "class": KimiProvider,
        "models": [
            # Kimi k2 系列 (最新)
            "kimi-k2",
            "kimi-k2-fast",
            # Kimi 1.5 系列
            "kimi-1.5",
            "kimi-1.5-flash",
            "kimi-1.5-flash-8k",
            "kimi-1.5-pro",
            # Kimi VL 多模态
            "kimi-vl",
            "kimi-vl-flash",
            # Kimi 原有
            "kimi-flash-1.5",
            "kimi-flash",
            "kimi-pro-1.5",
            "kimi-pro",
        ],
    },
    "minimax": {
        "name": "Minimax (海螺)",
        "class": MinimaxProvider,
        "models": [
            # M2.5 系列 (最新)
            "minimax-m2.5",
            "minimax-m2.5-fast",
            "minimax-m2",
            "minimax-m2-mini",
            # 原有
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
            # Gemini 2.5 系列 (最新)
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.5-flash-preview-05-20",
            # Gemini 2.0 系列
            "gemini-2.0-flash",
            "gemini-2.0-flash-exp",
            "gemini-2.0-pro",
            # Gemini 1.5 系列
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
        ],
    },
    "deepseek": {
        "name": "DeepSeek",
        "class": "deepseek.DeepSeekProvider",
        "models": [
            "deepseek-chat",
            "deepseek-coder",
            "deepseek-reasoner",
        ],
    },
    "qwen": {
        "name": "通义千问 (阿里)",
        "class": "qwen.QwenProvider",
        "models": [
            "qwen-2.5",
            "qwen-2.5-flash",
            "qwen-2.5-coder",
            "qwen-2.5-math",
            "qwen-vl-max",
            "qwen-vl-plus",
            "qwen-turbo",
            "qwen-plus",
        ],
    },
    "doubao": {
        "name": "豆包 (字节)",
        "class": "doubao.DoubaoProvider",
        "models": [
            "doubao-pro-32k",
            "doubao-pro-4k",
            "doubao-lite-32k",
            "doubao-lite-4k",
            "doubao-vision-pro",
        ],
    },
    "step": {
        "name": "阶跃星辰",
        "class": "step.StepProvider",
        "models": [
            "step-1",
            "step-1-flash",
            "step-1v",
            "step-2",
        ],
    },
    "spark": {
        "name": "讯飞星火",
        "class": "spark.SparkProvider",
        "models": [
            "spark-4.0",
            "spark-3.5",
            "spark-3.0",
            "spark-v3.5",
        ],
    },
    "tencent": {
        "name": "腾讯混元",
        "class": "tencent.TencentProvider",
        "models": [
            "hunyuan-pro",
            "hunyuan-standard",
            "hunyuan-flash",
            "hunyuan-vision",
        ],
    },
}


def create_provider(provider: str, api_key: str = "", base_url: str = "", model: str = "") -> BaseProvider:
    """创建 LLM 提供商"""
    provider_info = PROVIDERS.get(provider.lower())
    if not provider_info:
        provider_info = PROVIDERS["openai"]

    provider_class = provider_info["class"]

    # 如果是字符串(延迟导入),则动态导入
    if isinstance(provider_class, str):
        module_path, class_name = provider_class.rsplit(".", 1)
        import importlib
        module = importlib.import_module(f"xiaohongshu_agent.providers.{module_path}")
        provider_class = getattr(module, class_name)

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
