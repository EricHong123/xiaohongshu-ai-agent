"""
LLM 提供商基类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseProvider(ABC):
    """LLM 提供商基类"""

    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    @abstractmethod
    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """发送聊天请求"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """获取提供商名称"""
        pass
