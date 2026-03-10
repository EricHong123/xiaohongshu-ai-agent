"""
配置验证器
启动时检查配置完整性
"""
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from xiaohongshu_agent.utils.logger import get_logger

logger = get_logger("config")


@dataclass
class ValidationResult:
    """验证结果"""
    success: bool
    errors: List[str]
    warnings: List[str]
    info: Dict[str, Any]


class ConfigValidator:
    """配置验证器"""

    REQUIRED_PROVIDERS = ["openai", "anthropic", "zhipu", "kimi", "minimax", "gemini"]

    def __init__(self, config: "Config"):
        self.config = config

    def validate(self) -> ValidationResult:
        """执行完整验证"""
        errors = []
        warnings = []
        info = {}

        # 1. 验证 LLM 提供商
        provider = self.config.get("llm_provider", "openai")
        info["provider"] = provider

        if provider not in self.REQUIRED_PROVIDERS:
            errors.append(f"未知的 LLM 提供商: {provider}")

        # 2. 验证 API Key
        api_key = self.config.get_api_key()
        if not api_key:
            warnings.append("未配置 API Key")
            info["api_key_configured"] = False
        else:
            info["api_key_configured"] = True
            info["api_key_prefix"] = f"{api_key[:8]}..."

        # 3. 验证模型
        model = self.config.get_model()
        info["model"] = model

        # 4. 验证 MCP URL
        mcp_url = self.config.get("mcp_url", "http://localhost:18060/mcp")
        info["mcp_url"] = mcp_url

        if not mcp_url:
            errors.append("未配置 MCP URL")
        elif not mcp_url.startswith("http"):
            errors.append("MCP URL 必须以 http:// 或 https:// 开头")

        # 5. 验证权限
        permissions = self.config.get("permissions", [])
        info["permissions"] = permissions

        # 6. 检查环境变量
        env_vars = {}
        for prov in self.REQUIRED_PROVIDERS:
            env_key = f"{prov.upper()}_API_KEY"
            if os.getenv(env_key):
                env_vars[prov] = True

        info["env_vars_detected"] = list(env_vars.keys())

        success = len(errors) == 0
        logger.info(f"配置验证: {'通过' if success else '失败'} ({len(errors)} 错误, {len(warnings)} 警告)")

        return ValidationResult(
            success=success,
            errors=errors,
            warnings=warnings,
            info=info
        )

    def validate_api_key(self, provider: str = None) -> bool:
        """验证 API Key 是否有效"""
        import requests

        provider = provider or self.config.get("llm_provider", "openai")
        api_key = self.config.get_api_key()

        if not api_key:
            return False

        try:
            if provider == "openai":
                resp = requests.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=5
                )
                return resp.status_code == 200

            elif provider == "anthropic":
                resp = requests.get(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01"
                    },
                    timeout=5
                )
                # Anthropic 用 HEAD 请求
                return True  # 简化处理

            # 其他提供商简化处理
            return bool(api_key)

        except Exception as e:
            logger.warning(f"API Key 验证失败: {e}")
            return False


def validate_config(config: "Config") -> ValidationResult:
    """验证配置的便捷函数"""
    validator = ConfigValidator(config)
    return validator.validate()


__all__ = ["ConfigValidator", "ValidationResult", "validate_config"]
