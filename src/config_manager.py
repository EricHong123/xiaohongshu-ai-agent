#!/usr/bin/env python3
"""
配置管理模块
API Key 和模型配置
"""
import os
import json
from pathlib import Path


# ============== 配置文件 ==============
class ConfigManager:
    """配置管理器"""

    def __init__(self, config_file: str = None):
        if config_file is None:
            home = os.path.expanduser("~")
            self.config_dir = os.path.join(home, ".xiaohongshu_agent")
        else:
            self.config_dir = os.path.dirname(config_file)

        self.config_file = os.path.join(self.config_dir, "config.json")

        # 确保目录存在
        os.makedirs(self.config_dir, exist_ok=True)

        # 默认配置
        self.default_config = {
            "llm_provider": "openai",
            "model": "",
            "mcp_url": "http://localhost:18060/mcp",
            "permissions": ["file_read", "browser_control", "clipboard"]
        }

        self.config = self.load()

    def load(self) -> dict:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    # 合并默认配置
                    return {**self.default_config, **config}
            except:
                pass
        return self.default_config.copy()

    def save(self):
        """保存配置"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        # 设置权限
        os.chmod(self.config_file, 0o600)

    def get(self, key: str, default=None):
        """获取配置"""
        return self.config.get(key, default)

    def set(self, key: str, value):
        """设置配置"""
        self.config[key] = value

    def get_all(self) -> dict:
        """获取所有配置"""
        return self.config.copy()

    # ============== API Key 管理 ==============
    def get_api_key(self, provider: str = None) -> str:
        """获取 API Key"""
        if provider is None:
            provider = self.config.get("llm_provider", "openai")

        # 先从环境变量获取
        env_key = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(env_key)

        if api_key:
            return api_key

        # 从配置文件获取
        return self.config.get(f"{provider}_api_key", "")

    def set_api_key(self, provider: str, api_key: str):
        """设置 API Key"""
        self.config[f"{provider}_api_key"] = api_key
        self.save()

    # ============== 模型配置 ==============
    def get_model(self, provider: str = None) -> str:
        """获取模型"""
        if provider is None:
            provider = self.config.get("llm_provider", "openai")

        model = self.config.get(f"{provider}_model", "")

        # 默认模型
        defaults = {
            "openai": "gpt-4o",
            "anthropic": "claude-sonnet-4-20250514",
            "zhipu": "glm-4",
            "minimax": "abab6.5s-chat",
            "kimi": "kimi-flash-1.5",
            "gemini": "gemini-2.0-flash",
        }

        return model or defaults.get(provider, "gpt-4")

    def set_model(self, provider: str, model: str):
        """设置模型"""
        self.config[f"{provider}_model"] = model
        self.config["llm_provider"] = provider
        self.save()


# ============== 可用模型列表 ==============
def get_available_providers() -> dict:
    """获取可用的 LLM 提供商"""
    return {
        "openai": {
            "name": "OpenAI",
            "models": ["gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "env_key": "OPENAI_API_KEY",
            "default_model": "gpt-4o"
        },
        "anthropic": {
            "name": "Anthropic (Claude)",
            "models": ["claude-opus-4-6", "claude-sonnet-4-20250514", "claude-haiku-4-5"],
            "env_key": "ANTHROPIC_API_KEY",
            "default_model": "claude-sonnet-4-20250514"
        },
        "zhipu": {
            "name": "智谱 GLM",
            "models": ["glm-4", "glm-4-flash", "glm-4-plus", "glm-3-turbo"],
            "env_key": "ZHIPU_API_KEY",
            "default_model": "glm-4"
        },
        "minimax": {
            "name": "Minimax",
            "models": ["abab6.5s-chat", "abab6.5g-chat", "abab5.5s-chat"],
            "env_key": "MINIMAX_API_KEY",
            "default_model": "abab6.5s-chat"
        },
        "kimi": {
            "name": "Kimi (月之暗面)",
            "models": ["kimi-flash-1.5", "kimi-flash", "kimi-plus"],
            "env_key": "KIMI_API_KEY",
            "default_model": "kimi-flash-1.5"
        },
        "gemini": {
            "name": "Google Gemini",
            "models": ["gemini-2.0-flash", "gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
            "env_key": "GEMINI_API_KEY",
            "default_model": "gemini-2.0-flash"
        },
    }


# ============== 测试 ==============
if __name__ == "__main__":
    cm = ConfigManager()

    print("🧪 测试配置管理")
    print("=" * 50)

    # 测试配置
    print("\n[1] 当前配置:")
    print(f"   提供商: {cm.get('llm_provider')}")
    print(f"   MCP: {cm.get('mcp_url')}")

    # 测试提供商
    print("\n[2] 可用提供商:")
    providers = get_available_providers()
    for key, info in providers.items():
        print(f"   {key}: {info['name']}")
        print(f"      模型: {', '.join(info['models'][:3])}...")
