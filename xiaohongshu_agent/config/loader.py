"""
配置加载器
"""
import os
import json
from typing import Any, Dict, Optional
from pathlib import Path


# 提供商信息
PROVIDERS_INFO = {
    "openai": {
        "name": "OpenAI",
        "env_key": "OPENAI_API_KEY",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
        "default_model": "gpt-4o",
    },
    "anthropic": {
        "name": "Anthropic (Claude)",
        "env_key": "ANTHROPIC_API_KEY",
        "models": ["claude-sonnet-4-20250514", "claude-4-opus-20250514", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        "default_model": "claude-sonnet-4-20250514",
    },
    "zhipu": {
        "name": "智谱 GLM",
        "env_key": "ZHIPU_API_KEY",
        "models": ["glm-4", "glm-4-flash", "glm-4-plus", "glm-3-turbo"],
        "default_model": "glm-4",
    },
    "kimi": {
        "name": "Kimi",
        "env_key": "KIMI_API_KEY",
        "models": ["kimi-flash-1.5", "kimi-pro-1.5", "kimi-flash", "kimi-pro"],
        "default_model": "kimi-flash-1.5",
    },
    "minimax": {
        "name": "Minimax",
        "env_key": "MINIMAX_API_KEY",
        "models": ["minimax-m2.5", "abab6.5s-chat", "abab6.5-chat", "abab5.5s-chat", "abab5.5-chat"],
        "default_model": "minimax-m2.5",
    },
    "gemini": {
        "name": "Google Gemini",
        "env_key": "GEMINI_API_KEY",
        "models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.5-flash-8b"],
        "default_model": "gemini-2.0-flash",
    },
}


class Config:
    """配置类"""

    def __init__(self):
        self.config_file = Path.home() / ".xiaohongshu_agent" / "config.json"
        self.data: Dict[str, Any] = {}
        self._load()

    def _load(self):
        """加载配置"""
        # 默认配置
        self.data = {
            "llm_provider": os.getenv("LLM_PROVIDER", "openai"),
            "mcp_url": os.getenv("XIAOHONGSHU_MCP_URL", "http://localhost:18060/mcp"),
            "permissions": ["file_read", "browser_control", "clipboard"],
        }

        # 从文件加载
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    file_config = json.load(f)
                    self.data.update(file_config)
            except Exception as e:
                print(f"加载配置失败: {e}")

    def save(self):
        """保存配置"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置"""
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置"""
        self.data[key] = value

    def get_api_key(self) -> str:
        """获取 API Key"""
        provider = self.get("llm_provider", "openai")
        provider_info = PROVIDERS_INFO.get(provider, PROVIDERS_INFO["openai"])
        env_key = provider_info["env_key"]

        # 优先使用文件中的配置
        return self.data.get(f"{provider}_api_key") or os.getenv(env_key, "")

    def get_model(self) -> str:
        """获取模型"""
        provider = self.get("llm_provider", "openai")
        provider_info = PROVIDERS_INFO.get(provider, PROVIDERS_INFO["openai"])

        # 优先使用文件中的配置
        key = f"{provider}_model"
        return self.data.get(key) or provider_info.get("default_model", "gpt-4o")

    def get_available_providers(self) -> Dict:
        """获取可用的提供商列表"""
        return PROVIDERS_INFO

    def get_provider_models(self, provider: str = None) -> list:
        """获取提供商的所有模型"""
        if provider is None:
            provider = self.get("llm_provider", "openai")
        provider_info = PROVIDERS_INFO.get(provider, PROVIDERS_INFO["openai"])
        return provider_info.get("models", [])


def load_config() -> Config:
    """加载配置"""
    return Config()
