"""
上下文管理
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Context:
    """对话上下文"""
    current_task: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def set(self, key: str, value: Any):
        """设置变量"""
        self.variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取变量"""
        return self.variables.get(key, default)

    def clear(self):
        """清空上下文"""
        self.variables.clear()
        self.current_task = None
