"""
配置加载器
"""
import os
import json
from typing import Any, Dict pathlib import Path


class Config:
    """配置类"""

    def __, Optional
frominit__(self):
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
        env_keys = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "zhipu": "ZHIPU_API_KEY",
            "kimi": "KIMI_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "minimax": "MINIMAX_API_KEY",
        }
        key = env_keys.get(provider, "OPENAI_API_KEY")
        return self.data.get(f"{provider}_api_key") or os.getenv(key, "")

    def get_model(self) -> str:
        """获取模型"""
        provider = self.get("llm_provider", "openai")
        models = {
            "openai": "gpt-4",
            "anthropic": "claude-sonnet-4-20250514",
            "zhipu": "glm-4",
            "kimi": "kimi-flash-1.5",
            "gemini": "gemini-2.0-flash",
            "minimax": "abab6.5s-chat",
        }
        key = f"{provider}_model"
        return self.data.get(key) or models.get(provider, "gpt-4")


def load_config() -> Config:
    """加载配置"""
    return Config()
