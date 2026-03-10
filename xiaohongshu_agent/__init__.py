"""
小红书 AI Agent
一个强大的小红书运营自动化框架
"""
__version__ = "1.1.0"
__author__ = "Eric Hong"

from xiaohongshu_agent.agent.loop import XiaohongshuAgent
from xiaohongshu_agent.config import Config

__all__ = ["XiaohongshuAgent", "Config", "__version__"]
