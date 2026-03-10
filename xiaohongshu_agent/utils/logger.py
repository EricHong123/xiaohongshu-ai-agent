"""
日志系统
使用 loguru 提供更好的日志体验
"""
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime


def setup_logger(
    log_file: str = None,
    level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "7 days",
    format: str = None
):
    """
    设置日志系统

    Args:
        log_file: 日志文件路径，默认 logs/xiaohongshu_agent_{date}.log
        level: 日志级别
        rotation: 日志轮转大小
        retention: 日志保留时间
        format: 日志格式
    """
    # 移除默认处理器
    logger.remove()

    # 默认格式
    if format is None:
        format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    # 控制台输出
    logger.add(
        sys.stderr,
        level=level,
        format=format,
        colorize=True
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


def get_logger(name: str = None):
    """
    获取日志器

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

__all__ = ["logger", "setup_logger", "get_logger"]
