"""
日志系统
使用 loguru 提供更好的日志体验
支持结构化日志和 JSON 输出
"""
import sys
import json
from pathlib import Path
from loguru import logger
from datetime import datetime
from typing import Optional, Any


# 日志级别映射
LOG_LEVELS = {
    "TRACE": 5,
    "DEBUG": 10,
    "INFO": 20,
    "SUCCESS": 25,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}


class StructuredLogger:
    """结构化日志包装器"""

    def __init__(self, name: str = None):
        self.name = name
        self._logger = logger.bind(name=name) if name else logger

    def _log(self, level: str, message: str, **kwargs: Any):
        """通用日志方法"""
        if kwargs:
            # 结构化日志
            extra = " | " + " | ".join(f"{k}={v}" for k, v in kwargs.items())
            getattr(self._logger, level.lower())(f"{message}{extra}")
        else:
            getattr(self._logger, level.lower())(message)

    def debug(self, message: str, **kwargs: Any):
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs: Any):
        self._log("INFO", message, **kwargs)

    def success(self, message: str, **kwargs: Any):
        self._log("SUCCESS", message, **kwargs)

    def warning(self, message: str, **kwargs: Any):
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs: Any):
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs: Any):
        self._log("CRITICAL", message, **kwargs)

    def bind(self, **kwargs: Any):
        """绑定上下文"""
        return self._logger.bind(**kwargs)


def setup_logger(
    log_file: str = None,
    level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "7 days",
    format: str = None,
    json_output: bool = False,
    console: bool = True,
):
    """
    设置日志系统

    Args:
        log_file: 日志文件路径，默认 logs/xiaohongshu_agent_{date}.log
        level: 日志级别
        rotation: 日志轮转大小
        retention: 日志保留时间
        format: 日志格式
        json_output: 是否输出 JSON 格式
        console: 是否输出到控制台
    """
    # 移除默认处理器
    logger.remove()

    # JSON 格式化函数
    def json_formatter(record: dict) -> str:
        """JSON 格式日志"""
        log_obj = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "message": record["message"],
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
        }
        # 添加 extra 字段
        if record.get("extra"):
            log_obj.update(record["extra"])
        return json.dumps(log_obj) + "\n"

    # 默认格式
    if format is None:
        if json_output:
            format = json_formatter
        else:
            format = (
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )

    # 控制台输出
    if console:
        logger.add(
            sys.stderr,
            level=level,
            format=format,
            colorize=not json_output
        )

    # 文件输出
    if log_file is None:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"xiaohongshu_agent_{datetime.now().strftime('%Y%m%d')}.log"

    logger.add(
        str(log_file),
        level=level,
        format=format,
        rotation=rotation,
        retention=retention,
        compression="zip",
        encoding="utf-8"
    )

    return logger


def get_logger(name: str = None) -> StructuredLogger:
    """
    获取日志器

    Args:
        name: 日志器名称

    Returns:
        StructuredLogger 实例
    """
    return StructuredLogger(name=name)


def get_raw_logger(name: str = None):
    """
    获取原始 logger（用于需要完整 logger 对象的情况）

    Args:
        name: 日志器名称

    Returns:
        logger 实例
    """
    if name:
        return logger.bind(name=name)
    return logger


# 默认日志配置
_default_logger = setup_logger(level="INFO")

__all__ = ["logger", "setup_logger", "get_logger", "get_raw_logger", "StructuredLogger"]
