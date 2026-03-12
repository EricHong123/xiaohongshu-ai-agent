"""
配置验证器
启动时检查配置完整性
"""
import os
from typing import Any, Dict, List, Optional
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
        """执行纯本地验证（不触网）"""
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
            # 不记录任何可用于回溯的 Key 片段
            info["api_key_prefix"] = "***"

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
        """
        验证 API Key 是否有效（可能触发外部请求）。

        为了避免在启动时误触网，建议优先使用 `validate()`，
        只有在需要“连通性/有效性”检查时再显式调用本方法或 `validate_connectivity()`。
        """
        provider = provider or self.config.get("llm_provider", "openai")
        api_key = self.config.get_api_key()

        if not api_key:
            return False

        try:
            from xiaohongshu_agent.config.api_key_validator import validate_api_key

            result = validate_api_key(provider=provider, api_key=api_key)
            return result.ok
        except Exception as e:
            logger.warning(f"API Key 验证失败: {e}")
            return False

    def validate_connectivity(self, provider: str = None) -> ValidationResult:
        """
        外部连通性/有效性验证（可能触发外部请求）。

        - 当前仅检查 API Key 是否“看起来可用/可连通”
        - 不会被 `validate()` 自动调用，需显式调用
        """
        errors: List[str] = []
        warnings: List[str] = []
        info: Dict[str, Any] = {}

        provider = provider or self.config.get("llm_provider", "openai")
        info["provider"] = provider

        api_key = self.config.get_api_key()
        info["api_key_configured"] = bool(api_key)

        if not api_key:
            warnings.append("未配置 API Key")
            return ValidationResult(success=True, errors=errors, warnings=warnings, info=info)

        ok = self.validate_api_key(provider=provider)
        info["api_key_valid"] = ok
        if not ok:
            errors.append("API Key 验证失败或不可用")

        return ValidationResult(success=len(errors) == 0, errors=errors, warnings=warnings, info=info)


def validate_config(config: "Config") -> ValidationResult:
    """验证配置的便捷函数"""
    validator = ConfigValidator(config)
    return validator.validate()


def validate_connectivity(config: "Config", provider: str = None) -> ValidationResult:
    """外部连通性验证的便捷函数（可能触发外部请求）"""
    validator = ConfigValidator(config)
    return validator.validate_connectivity(provider=provider)


__all__ = ["ConfigValidator", "ValidationResult", "validate_config", "validate_connectivity"]
