"""
工具注册表
管理所有可用的工具
"""
from typing import Dict, Any, List, Type
from xiaohongshu_agent.utils.logger import get_logger

logger = get_logger("tools")


class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        self._tools: Dict[str, Type] = {}
        self._instances: Dict[str, Any] = {}

    def register(self, name: str, tool_class: Type):
        """注册工具"""
        self._tools[name] = tool_class
        logger.debug(f"注册工具: {name}")

    def get(self, name: str, **kwargs) -> Any:
        """获取工具实例"""
        if name not in self._tools:
            logger.warning(f"工具不存在: {name}")
            return None

        # 如果已有实例，直接返回
        if name in self._instances:
            return self._instances[name]

        # 创建新实例
        tool_class = self._tools[name]
        instance = tool_class(**kwargs)
        self._instances[name] = instance
        logger.debug(f"创建工具实例: {name}")
        return instance

    def list_tools(self) -> List[str]:
        """列出所有工具"""
        return list(self._tools.keys())

    def get_tool_schemas(self) -> List[Dict]:
        """获取所有工具的 schema"""
        schemas = []
        for name, tool_class in self._tools.items():
            instance = self.get(name)
            if instance:
                schemas.append(instance.get_schema())
        return schemas


# 全局注册表
registry = ToolRegistry()


def register_tool(name: str):
    """装饰器：注册工具"""
    def decorator(tool_class: Type):
        registry.register(name, tool_class)
        return tool_class
    return decorator


__all__ = ["ToolRegistry", "registry", "register_tool"]
