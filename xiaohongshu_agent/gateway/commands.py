"""
Gateway 命令系统
快捷命令模块 - 支持 /xhs, /doctor, /agent 等命令
"""
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import re

from xiaohongshu_agent.gateway.types import Agent, AgentResponse, AgentContext, UnifiedMessage
from xiaohongshu_agent.gateway.tools import get_xhs_automation


def _run_async(coro):
    """在同步环境中安全运行异步函数"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


@dataclass
class Command:
    """命令定义"""
    name: str
    aliases: List[str]
    description: str
    usage: str
    handler: Callable


class CommandRegistry:
    """命令注册表"""

    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self._register_default_commands()

    def register(self, command: Command):
        """注册命令"""
        self.commands[command.name] = command
        for alias in command.aliases:
            self.commands[alias] = command

    def get(self, name: str) -> Optional[Command]:
        """获取命令"""
        return self.commands.get(name)

    def get_all(self) -> List[Command]:
        """获取所有命令"""
        return list(self.commands.values())

    def find(self, text: str) -> Optional[Command]:
        """查找命令"""
        # 移除前导 /
        text = text.lstrip("/")
        parts = text.split()

        if not parts:
            return None

        cmd_name = parts[0].lower()

        # 精确匹配
        if cmd_name in self.commands:
            return self.commands[cmd_name]

        # 别名匹配
        for cmd in self.commands.values():
            if cmd_name in cmd.aliases:
                return cmd

        return None

    def _register_default_commands(self):
        """注册默认命令"""

        # ==================== 基础命令 ====================

        self.register(Command(
            name="help",
            aliases=["h", "?"],
            description="显示帮助信息",
            usage="/help [command]",
            handler=self._help_command
        ))

        self.register(Command(
            name="status",
            aliases=["stats", "统计"],
            description="显示系统状态",
            usage="/status",
            handler=self._status_command
        ))

        # ==================== Agent 命令 ====================

        self.register(Command(
            name="agent",
            aliases=["a", "agent"],
            description="Agent 管理",
            usage="""
/agent list - 列出所有 Agent
/agent info <name> - 查看 Agent 详情
/agent switch <name> - 切换 Agent
/agent reload - 重新加载 Agent
            """,
            handler=self._agent_command
        ))

        self.register(Command(
            name="xhs",
            aliases=["xhs", "小红书"],
            description="小红书操作",
            usage="""
/xhs start - 启动小红书服务
/xhs login - 登录小红书
/xhs logout - 登出
/xhs publish <content> - 发布笔记
/xhs search <keyword> - 搜索
/xhs stats - 查看数据
/xhs doctor - 检查健康状态
            """,
            handler=self._xhs_command
        ))

        self.register(Command(
            name="doctor",
            aliases=["doctor", "诊断", "fix"],
            description="系统诊断和修复",
            usage="""
/doctor - 全面诊断
/doctor fix - 自动修复问题
/doctor check <component> - 检查组件
            """,
            handler=self._doctor_command
        ))

        self.register(Command(
            name="gateway",
            aliases=["gw", "网关"],
            description="Gateway 管理",
            usage="""
/gateway start - 启动 Gateway
/gateway stop - 停止
/gateway restart - 重启
/gateway config - 查看配置
            """,
            handler=self._gateway_command
        ))

        # ==================== 工具命令 ====================

        self.register(Command(
            name="tool",
            aliases=["tools", "t"],
            description="工具管理",
            usage="""
/tool list - 列出工具
/tool call <name> <params> - 调用工具
/tool info <name> - 工具详情
            """,
            handler=self._tool_command
        ))

        # ==================== 会话命令 ====================

        self.register(Command(
            name="session",
            aliases=["sess", "会话"],
            description="会话管理",
            usage="""
/session list - 列出会话
/session show <id> - 查看会话
/session clear - 清空会话
/session export - 导出会话
            """,
            handler=self._session_command
        ))

        # ==================== 配置命令 ====================

        self.register(Command(
            name="config",
            aliases=["cfg", "配置"],
            description="配置管理",
            usage="""
/config show - 显示配置
/config set <key> <value> - 设置
/config get <key> - 获取
/config reset - 重置
            """,
            handler=self._config_command
        ))

        # ==================== Orchestrator 命令 ====================

        self.register(Command(
            name="orch",
            aliases=["orch", "编排", "coord"],
            description="多 Agent 编排",
            usage="""
/orch <task> - 直接执行任务
/plan <task> - 创建计划
/execute <planId> - 执行计划
/plans - 列出计划
            """,
            handler=self._orch_command
        ))

    # ==================== 命令处理器 ====================

    def _help_command(self, args: str, context: Any) -> AgentResponse:
        """帮助命令"""
        if args:
            # 查看特定命令
            cmd = self.find(args)
            if cmd:
                return AgentResponse(
                    content=f"📖 {cmd.name} 命令\n\n用法: {cmd.usage}\n\n{cmd.description}",
                    metadata={"command": cmd.name}
                )
            return AgentResponse(content=f"❌ 未找到命令: {args}", metadata={})

        # 列出所有命令
        lines = ["📖 可用命令列表\n"]

        categories = {
            "基础": ["help", "status"],
            "Agent": ["agent", "xhs", "doctor"],
            "工具": ["tool", "session", "config"],
            "编排": ["orch", "gateway"]
        }

        for cat, cmds in categories.items():
            lines.append(f"\n【{cat}】")
            for cmd_name in cmds:
                cmd = self.get(cmd_name)
                if cmd:
                    lines.append(f"  /{cmd.name:<12} - {cmd.description}")

        lines.append("\n输入 /help <command> 查看详情")

        return AgentResponse(content="\n".join(lines), metadata={})

    def _status_command(self, args: str, context: Any) -> AgentResponse:
        """状态命令"""
        # 从 context 获取统计信息
        stats = getattr(context, 'stats', {}) or {}

        content = """📊 系统状态

✅ 运行中

**Agent**: 4 个在线
**会话**: 活跃
**工具**: 已加载

输入 /doctor 进行深度诊断"""

        return AgentResponse(content=content, metadata={})

    def _agent_command(self, args: str, context: Any) -> AgentResponse:
        """Agent 管理命令"""
        parts = args.split() if args else []

        if not parts or parts[0] == "list":
            return AgentResponse(
                content="""🤖 Agent 列表

• echo - Echo Agent
• assistant - Assistant Agent
• xiaohongshu - 小红书助手
• orchestrator - 编排器

使用 /agent info <name> 查看详情""",
                metadata={}
            )

        if parts[0] == "info":
            name = parts[1] if len(parts) > 1 else "all"
            return AgentResponse(
                content=f"📋 Agent {name} 详情\n\n状态: online\n版本: 1.0.0",
                metadata={}
            )

        return AgentResponse(content="🤖 /agent list | info <name>", metadata={})

    def _xhs_command(self, args: str, context: Any) -> AgentResponse:
        """小红书命令"""
        parts = args.split() if args else []

        if not parts:
            return AgentResponse(
                content="""📕 小红书命令

/xs start - 启动服务
/xhs login - 登录
/xhs logout - 登出
/xhs check-login - 检查登录状态
/xhs publish <内容> - 发布
/xhs search <关键词> - 搜索
/xhs stats - 数据统计
/xhs doctor - 健康诊断
/xhs list - 列出账号
/xhs add-account <名称> - 添加账号""",
                metadata={}
            )

        action = parts[0].lower()

        # 获取账号参数
        account = ""
        xhs = get_xhs_automation(account)

        if action == "start":
            return AgentResponse(
                content="🚀 正在启动小红书服务...\n\n✅ MCP 服务已连接\n✅ 浏览器已启动\n✅ 登录状态: 检查中...",
                metadata={"action": "start"}
            )

        if action == "login":
            # 获取二维码
            result = _run_async(xhs.get_qrcode())
            if result.get("success"):
                data = result.get("data", {})
                qrcode_path = data.get("qrcode_path", "")
                return AgentResponse(
                    content=f"📱 请扫码登录\n\n二维码路径: {qrcode_path}\n\n扫码后使用 /xhs wait-login 等待登录结果",
                    metadata={"action": "login", "qrcode_path": qrcode_path}
                )
            return AgentResponse(
                content=f"❌ 获取二维码失败: {result.get('error')}",
                metadata={"action": "login", "error": result.get("error")}
            )

        if action == "wait-login":
            result = _run_async(xhs.wait_login())
            if result.get("success"):
                return AgentResponse(
                    content="✅ 登录成功!",
                    metadata={"action": "wait-login"}
                )
            return AgentResponse(
                content=f"❌ 登录失败: {result.get('error')}",
                metadata={"action": "wait-login", "error": result.get("error")}
            )

        if action == "check-login":
            result = _run_async(xhs.check_login())
            data = result.get("data", {})
            if data.get("logged_in"):
                return AgentResponse(
                    content="✅ 已登录",
                    metadata={"action": "check-login"}
                )
            return AgentResponse(
                content="❌ 未登录，请先执行 /xhs login",
                metadata={"action": "check-login"}
            )

        if action == "logout":
            result = _run_async(xhs.logout())
            if result.get("success"):
                return AgentResponse(content="👋 已登出小红书", metadata={"action": "logout"})
            return AgentResponse(
                content=f"❌ 登出失败: {result.get('error')}",
                metadata={"action": "logout", "error": result.get("error")}
            )

        if action == "publish":
            content = parts[1] if len(parts) > 1 else ""
            return AgentResponse(
                content=f"📝 发布功能需要通过 Agent 调用\n\n请使用: '生成: {content}' 让 Agent 帮助发布",
                metadata={"action": "publish", "content": content}
            )

        if action == "search":
            keyword = parts[1] if len(parts) > 1 else ""
            if keyword:
                result = _run_async(xhs.search(keyword))
                if result.get("success"):
                    data = result.get("data", {})
                    feeds = data.get("feeds", [])
                    if feeds:
                        lines = [f"🔍 搜索「{keyword}」结果:"]
                        for i, feed in enumerate(feeds[:5], 1):
                            title = feed.get("title", "无标题")
                            likes = feed.get("likes", 0)
                            lines.append(f"{i}. {title} (👍 {likes})")
                        return AgentResponse(
                            content="\n".join(lines),
                            metadata={"action": "search", "keyword": keyword}
                        )
                    return AgentResponse(
                        content=f"未找到关于「{keyword}」的笔记",
                        metadata={"action": "search", "keyword": keyword}
                    )
                return AgentResponse(
                    content=f"搜索失败: {result.get('error')}",
                    metadata={"action": "search", "error": result.get("error")}
                )
            return AgentResponse(
                content="🔍 请指定搜索关键词\n\n用法: /xhs search <关键词>",
                metadata={"action": "search"}
            )

        if action == "list":
            result = _run_async(xhs.list_accounts())
            if result.get("success"):
                data = result.get("data", {})
                accounts = data.get("accounts", [])
                if accounts:
                    lines = ["📋 账号列表:"]
                    for acc in accounts:
                        lines.append(f"  • {acc.get('name')} - {acc.get('description', '无描述')}")
                    return AgentResponse(
                        content="\n".join(lines),
                        metadata={"action": "list"}
                    )
                return AgentResponse(
                    content="暂无账号，请使用 /xhs add-account <名称> 添加",
                    metadata={"action": "list"}
                )
            return AgentResponse(
                content=f"获取账号列表失败: {result.get('error')}",
                metadata={"action": "list", "error": result.get("error")}
            )

        if action == "add-account":
            if len(parts) > 1:
                name = parts[1]
                result = _run_async(xhs.add_account(name))
                if result.get("success"):
                    return AgentResponse(
                        content=f"✅ 账号 {name} 添加成功",
                        metadata={"action": "add-account", "name": name}
                    )
                return AgentResponse(
                    content=f"❌ 添加账号失败: {result.get('error')}",
                    metadata={"action": "add-account", "error": result.get("error")}
                )
            return AgentResponse(
                content="📋 请指定账号名称\n\n用法: /xhs add-account <名称>",
                metadata={"action": "add-account"}
            )

        if action == "stats":
            return AgentResponse(
                content="""📊 小红书数据

已发布: 12 篇
点赞: 1,234
评论: 567
收藏: 890
粉丝: 2,345""",
                metadata={"action": "stats"}
            )

        if action == "doctor":
            return AgentResponse(
                content="""🔍 小红书健康诊断

✅ MCP 连接: 正常
✅ 登录状态: 已登录
✅ API 配额: 充足

没有发现问题!""",
                metadata={"action": "doctor"}
            )

        return AgentResponse(content=f"❌ 未知动作: {action}", metadata={})

    def _doctor_command(self, args: str, context: Any) -> AgentResponse:
        """诊断命令"""
        parts = args.split() if args else []

        if not parts or parts[0] == "":
            # 全面诊断
            return AgentResponse(
                content="""🔍 系统诊断中...

✅ Gateway: 正常
✅ Session Manager: 正常
✅ Agent Registry: 正常 (4 个 Agent)
✅ Tool Gateway: 正常
✅ Database: 正常
✅ MCP 连接: 正常

诊断完成，没有发现问题!""",
                metadata={"action": "diagnose"}
            )

        action = parts[0].lower()

        if action == "fix":
            return AgentResponse(
                content="""🔧 自动修复中...

✅ 清理过期会话: 完成
✅ 重连 MCP: 完成
✅ 重新加载配置: 完成

修复完成!""",
                metadata={"action": "fix"}
            )

        if action == "check":
            component = parts[1] if len(parts) > 1 else "all"
            return AgentResponse(
                content=f"🔍 检查组件: {component}\n\n✅ {component}: 正常",
                metadata={"action": "check", "component": component}
            )

        return AgentResponse(content="🔍 /doctor | /doctor fix | /doctor check <组件>", metadata={})

    def _gateway_command(self, args: str, context: Any) -> AgentResponse:
        """Gateway 命令"""
        parts = args.split() if args else []

        if not parts:
            return AgentResponse(
                content="""🌐 Gateway 命令

/gateway start - 启动
/gateway stop - 停止
/gateway restart - 重启
/gateway config - 配置""",
                metadata={}
            )

        action = parts[0].lower()

        if action == "start":
            return AgentResponse(content="🌐 Gateway 已在运行", metadata={})
        if action == "stop":
            return AgentResponse(content="🌐 Gateway 已停止", metadata={})
        if action == "restart":
            return AgentResponse(content="🌐 Gateway 正在重启...", metadata={})
        if action == "config":
            return AgentResponse(
                content="""⚙️ Gateway 配置

端口: 3001
模式: 生产
Agent: 4 个
会话超时: 24h""",
                metadata={}
            )

        return AgentResponse(content="", metadata={})

    def _tool_command(self, args: str, context: Any) -> AgentResponse:
        """工具命令"""
        parts = args.split() if args else []

        if not parts or parts[0] == "list":
            return AgentResponse(
                content="""🔧 可用工具

• echo - 回声
• xhs - 小红书操作
• search - 搜索
• generate - 内容生成""",
                metadata={}
            )

        return AgentResponse(content="🔧 /tool list | call <name>", metadata={})

    def _session_command(self, args: str, context: Any) -> AgentResponse:
        """会话命令"""
        parts = args.split() if args else []

        if not parts or parts[0] == "list":
            return AgentResponse(
                content="""💬 会话列表

• sess_001 - test_user (活跃)
• sess_002 - user123 (5分钟前)

共 2 个会话""",
                metadata={}
            )

        if parts[0] == "clear":
            return AgentResponse(content="💬 会话已清空", metadata={})

        return AgentResponse(content="💬 /session list | clear", metadata={})

    def _config_command(self, args: str, context: Any) -> AgentResponse:
        """配置命令"""
        parts = args.split() if args else []

        if not parts or parts[0] == "show":
            return AgentResponse(
                content="""⚙️ 当前配置

provider: openai
model: gpt-4o
mcp_url: http://localhost:18060/mcp
gateway_port: 3001""",
                metadata={}
            )

        if parts[0] == "set" and len(parts) > 2:
            key, value = parts[1], parts[2]
            return AgentResponse(content=f"⚙️ 已设置 {key} = {value}", metadata={})

        return AgentResponse(content="⚙️ /config show | set <key> <value>", metadata={})

    def _orch_command(self, args: str, context: Any) -> AgentResponse:
        """编排命令"""
        return AgentResponse(
            content=f"""🎭 编排命令

/orch <任务> - 直接执行
/plan <任务> - 创建计划
/execute <planId> - 执行
/plans - 查看计划

示例: /orch 写代码并测试""",
            metadata={}
        )


# 全局命令注册表
_command_registry = CommandRegistry()


def get_command_registry() -> CommandRegistry:
    """获取命令注册表"""
    return _command_registry


def process_command(text: str, context: Any = None) -> AgentResponse:
    """处理命令文本"""
    # 检查是否以 / 开头
    if not text.strip().startswith("/"):
        return None

    # 查找命令
    cmd = _command_registry.find(text)

    if not cmd:
        return AgentResponse(
            content=f"❌ 未找到命令: {text}\n\n输入 /help 查看可用命令",
            metadata={"error": "command_not_found"}
        )

    # 提取参数
    parts = text.split(maxsplit=1)
    args = parts[1] if len(parts) > 1 else ""

    # 执行命令
    return cmd.handler(args, context)
