#!/usr/bin/env python3
"""
小红书 AI Agent 系统配置
支持多种 LLM 提供商
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
import os


# ============== LLM 提供商配置 ==============
@dataclass
class LLMConfig:
    """LLM 配置"""
    provider: str  # openai, anthropic, zhipu, minimax, kimi, gemini
    api_key: str
    base_url: Optional[str] = None
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000


# 默认配置 - 从环境变量读取
def get_llm_config() -> LLMConfig:
    """获取 LLM 配置"""
    provider = os.getenv("LLM_PROVIDER", "openai")

    configs = {
        "openai": LLMConfig(
            provider="openai",
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
        ),
        "anthropic": LLMConfig(
            provider="anthropic",
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        ),
        "zhipu": LLMConfig(
            provider="zhipu",
            api_key=os.getenv("ZHIPU_API_KEY", ""),
            base_url=os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
            model=os.getenv("ZHIPU_MODEL", "glm-4"),
        ),
        "minimax": LLMConfig(
            provider="minimax",
            api_key=os.getenv("MINIMAX_API_KEY", ""),
            base_url=os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1"),
            model=os.getenv("MINIMAX_MODEL", "abab6.5s-chat"),
        ),
        "kimi": LLMConfig(
            provider="kimi",
            api_key=os.getenv("KIMI_API_KEY", ""),
            base_url=os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1"),
            model=os.getenv("KIMI_MODEL", "kimi-flash-1.5"),
        ),
        "gemini": LLMConfig(
            provider="gemini",
            api_key=os.getenv("GEMINI_API_KEY", ""),
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        ),
    }

    return configs.get(provider, configs["openai"])


# ============== 数据库配置 ==============
@dataclass
class DatabaseConfig:
    """数据库配置"""
    type: str = "sqlite"  # sqlite, postgres, mysql
    host: str = "localhost"
    port: int = 5432
    database: str = "xiaohongshu_agent"
    user: str = ""
    password: str = ""

    @property
    def url(self) -> str:
        if self.type == "sqlite":
            return f"sqlite:///{self.database}.db"
        elif self.type == "postgres":
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        return ""


# ============== RAG 配置 ==============
@dataclass
class RAGConfig:
    """RAG 配置"""
    vector_db: str = "chroma"  # chroma, faiss, milvus, qdrant
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5


# ============== MCP 配置 ==============
@dataclass
class MCPConfig:
    """MCP 配置"""
    xiaohongshu_url: str = "http://localhost:18060/mcp"
