"""
健康检查模块
提供详细的系统健康状态
"""
from datetime import datetime
from typing import Dict, Any, Optional


def check_health(agent: Optional[Any]) -> Dict[str, Any]:
    """检查系统健康状态

    Args:
        agent: XiaohongshuAgent 实例

    Returns:
        健康状态字典
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }

    # 检查 Agent
    if agent is None:
        health_status["status"] = "degraded"
        health_status["checks"]["agent"] = {
            "status": "not_initialized",
            "message": "Agent 未初始化"
        }
    else:
        health_status["checks"]["agent"] = {
            "status": "ok",
            "provider": agent.provider.get_name() if agent.provider else None,
            "model": agent.provider.model if agent.provider else None,
        }

        # 检查数据库
        try:
            stats = agent.db.get_stats()
            health_status["checks"]["database"] = {
                "status": "ok",
                "stats": stats
            }
        except Exception as e:
            health_status["checks"]["database"] = {
                "status": "error",
                "message": str(e)
            }
            health_status["status"] = "degraded"

        # 检查 MCP 连接
        try:
            if agent.channel and hasattr(agent.channel, '_initialized'):
                health_status["checks"]["mcp"] = {
                    "status": "ok" if agent.channel._initialized else "not_connected",
                    "url": agent.channel.url if hasattr(agent.channel, 'url') else None,
                }
            else:
                health_status["checks"]["mcp"] = {
                    "status": "not_initialized"
                }
        except Exception as e:
            health_status["checks"]["mcp"] = {
                "status": "error",
                "message": str(e)
            }
            health_status["status"] = "degraded"

        # 检查 Memory
        try:
            memory_status = agent.get_memory_status()
            health_status["checks"]["memory"] = {
                "status": "ok",
                "count": memory_status.get("count", 0),
                "limit": memory_status.get("limit", 50),
            }
        except Exception as e:
            health_status["checks"]["memory"] = {
                "status": "error",
                "message": str(e)
            }

    # 检查依赖
    health_status["checks"]["dependencies"] = check_dependencies()

    # 计算 HTTP 状态码
    http_status = 200 if health_status["status"] == "healthy" else 503

    return health_status, http_status


def check_dependencies() -> Dict[str, str]:
    """检查依赖包状态"""
    deps = {}
    required = [
        ("flask", "flask"),
        ("openai", "openai"),
        ("anthropic", "anthropic"),
        ("requests", "requests"),
        ("loguru", "loguru"),
        ("tenacity", "tenacity"),
    ]

    for name, import_name in required:
        try:
            __import__(import_name)
            deps[name] = "ok"
        except ImportError:
            deps[name] = "not_installed"

    return deps


__all__ = ["check_health", "check_dependencies"]
