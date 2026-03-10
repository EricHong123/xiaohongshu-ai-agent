"""
Shell 工具
执行系统命令
"""
import subprocess
from typing import Dict, Any, List

from xiaohongshu_agent.agent.tools.base import Tool, ToolResult
from xiaohongshu_agent.agent.tools.registry import register_tool
from xiaohongshu_agent.utils.logger import get_logger

logger = get_logger("tools.shell")


# 危险命令黑名单
DANGEROUS_COMMANDS = [
    "rm -rf /",
    "mkfs",
    "dd if=",
    ">:",
    "chmod 777 /",
    "chown -R",
]


def is_command_safe(command: str) -> bool:
    """检查命令是否安全"""
    cmd_lower = command.lower()
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous in cmd_lower:
            return False
    return True


@register_tool("shell_execute")
class ShellExecuteTool(Tool):
    """Shell 命令执行工具"""

    name = "shell_execute"
    description = "执行系统命令"

    def __init__(self, allowed_commands: List[str] = None, timeout: int = 30):
        self.allowed_commands = allowed_commands or []
        self.timeout = timeout
        self._history: List[Dict] = []

    def execute(self, command: str = None, **kwargs) -> ToolResult:
        """执行命令"""
        if not command:
            return ToolResult(success=False, error="缺少命令")

        # 安全检查
        if not is_command_safe(command):
            logger.warning(f"危险命令被阻止: {command}")
            return ToolResult(success=False, error="命令包含危险操作，已被阻止")

        # 白名单检查
        if self.allowed_commands:
            allowed = any(cmd in command for cmd in self.allowed_commands)
            if not allowed:
                return ToolResult(success=False, error="命令不在白名单中")

        try:
            logger.info(f"执行命令: {command[:50]}...")

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding="utf-8",
                errors="replace"
            )

            output = {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }

            # 记录历史
            self._history.append(output)

            logger.info(f"命令执行完成: returncode={result.returncode}")

            return ToolResult(
                success=result.returncode == 0,
                data=output
            )
        except subprocess.TimeoutExpired:
            logger.error(f"命令执行超时: {command[:50]}")
            return ToolResult(success=False, error=f"命令执行超时 ({self.timeout}s)")
        except Exception as e:
            logger.error(f"命令执行失败: {e}")
            return ToolResult(success=False, error=str(e))

    def get_history(self) -> List[Dict]:
        """获取命令历史"""
        return self._history[-10:]

    def get_schema(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "要执行的命令"}
                },
                "required": ["command"]
            }
        }
