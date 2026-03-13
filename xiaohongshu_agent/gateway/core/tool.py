"""
工具网关
参考 ai-agent-gateway/src/core/tool.ts
"""
from typing import Dict, List, Any, Optional, Callable

from xiaohongshu_agent.gateway.types import Tool, ToolResult


class ToolGateway:
    """工具网关 - 统一代理工具调用"""

    def __init__(
        self,
        config: Optional[Dict] = None,
        logger: Optional[Any] = None
    ):
        self.config = config or {}
        self.logger = logger
        self.tools: Dict[str, Tool] = {}
        self.handlers: Dict[str, Callable] = {}

        # 配置项
        self.enabled = self.config.get("enabled", True)
        self.rate_limit = self.config.get("rateLimit", 100)

    def register(self, definition: Dict) -> None:
        """注册工具"""
        tool = Tool(
            name=definition.get("name", ""),
            description=definition.get("description", ""),
            parameters=definition.get("parameters", {})
        )
        self.tools[tool.name] = tool
        self._log("info", "Tool registered", tool_name=tool.name)

    def register_handler(self, name: str, handler: Callable) -> None:
        """注册工具处理函数"""
        self.handlers[name] = handler

    def unregister(self, name: str) -> bool:
        """注销工具"""
        if name in self.tools:
            del self.tools[name]
            if name in self.handlers:
                del self.handlers[name]
            self._log("info", "Tool unregistered", tool_name=name)
            return True
        return False

    def get(self, name: str) -> Optional[Tool]:
        """获取工具定义"""
        return self.tools.get(name)

    def get_all(self) -> List[Tool]:
        """获取所有工具"""
        return list(self.tools.values())

    def get_tool_list(self) -> List[Dict]:
        """获取工具列表（兼容格式）"""
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters
            }
            for t in self.tools.values()
        ]

    def has(self, name: str) -> bool:
        """检查工具是否存在"""
        return name in self.tools and name in self.handlers

    async def call(
        self,
        name: str,
        params: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """调用工具"""
        if not self.enabled:
            return {"success": False, "error": "Tool gateway disabled"}

        if name not in self.handlers:
            return {"success": False, "error": f"Tool not found: {name}"}

        handler = self.handlers[name]

        try:
            # 如果是异步函数
            if hasattr(handler, '__call__'):
                import inspect
                if inspect.iscoroutinefunction(handler):
                    result = await handler(params, context)
                else:
                    result = handler(params, context)
            else:
                result = handler(params, context)

            self._log("info", "Tool called", tool_name=name, success=True)
            return result

        except Exception as e:
            self._log("error", "Tool call failed", tool_name=name, error=str(e))
            return {"success": False, "error": str(e)}

    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "total": len(self.tools),
            "enabled": self.enabled,
            "rate_limit": self.rate_limit,
            "tools": list(self.tools.keys())
        }

    def _log(self, level: str, message: str, **kwargs):
        if self.logger:
            getattr(self.logger, level)(message, **kwargs)


# 内置工具：echo
def echo_handler(params: Dict, context: Any) -> Dict:
    """Echo 工具"""
    return {
        "success": True,
        "echo": params.get("message", "")
    }


# 注册内置工具
def register_builtin_tools(gateway: ToolGateway) -> None:
    """注册内置工具"""
    gateway.register({
        "name": "echo",
        "description": "Echo back the input",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        }
    })
    gateway.register_handler("echo", echo_handler)
