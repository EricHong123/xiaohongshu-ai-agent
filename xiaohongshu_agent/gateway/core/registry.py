"""
Agent 注册表
参考 ai-agent-gateway/src/core/registry.ts
"""
from typing import Dict, List, Optional, Any

from xiaohongshu_agent.gateway.types import (
    Agent, AgentStatus, AgentHandler, AgentContext,
    UnifiedMessage, Session, RoutingRules, AgentResponse
)
from xiaohongshu_agent.gateway.commands import process_command


class ToolGateway:
    """工具网关占位符"""

    def get_tool_list(self) -> List[Dict]:
        return []

    def call(self, name: str, params: Dict, ctx: Any) -> Any:
        return {"success": False}


class AgentRegistry:
    """Agent 注册表"""

    def __init__(
        self,
        config: Optional[Dict] = None,
        logger: Optional[Any] = None
    ):
        self.config = config or {}
        self.logger = logger
        self.agents: Dict[str, Agent] = {}
        self.round_robin_index: Dict[str, int] = {}

        # 配置项
        self.default_agent = self.config.get("defaultAgent", "assistant")
        self.routing_mode = self.config.get("routingMode", "keyword")

    def register(self, agent: Agent) -> None:
        """注册 Agent"""
        if agent.id in self.agents:
            self._log("warn", "Agent already registered, overwriting", agent_id=agent.id)

        self.agents[agent.id] = agent
        self._log("info", "Agent registered", agent_id=agent.id, name=agent.name)

    def unregister(self, agent_id: str) -> bool:
        """注销 Agent"""
        if agent_id not in self.agents:
            return False

        agent = self.agents.pop(agent_id)
        self._log("info", "Agent unregistered", agent_id=agent_id, name=agent.name)
        return True

    def get(self, agent_id: str) -> Optional[Agent]:
        """获取 Agent"""
        return self.agents.get(agent_id)

    def get_all(self) -> List[Agent]:
        """获取所有 Agent"""
        return list(self.agents.values())

    def get_online(self) -> List[Agent]:
        """获取在线 Agent"""
        return [a for a in self.agents.values() if a.status == AgentStatus.ONLINE]

    def set_status(self, agent_id: str, status: AgentStatus) -> bool:
        """设置 Agent 状态"""
        agent = self.agents.get(agent_id)
        if not agent:
            return False

        agent.status = status
        self._log("info", "Agent status updated", agent_id=agent_id, status=status)
        return True

    def _match_by_rules(self, message: UnifiedMessage, agent: Agent) -> bool:
        """根据规则匹配"""
        rules = agent.routingRules
        if not rules:
            return False

        if rules.keywords:
            content = message.content.lower()
            if not any(kw.lower() in content for kw in rules.keywords):
                return False

        if rules.users:
            if message.userId not in rules.users:
                return False

        if rules.channels:
            if message.channel not in rules.channels:
                return False

        return True

    def route(self, message: UnifiedMessage) -> Optional[Agent]:
        """路由消息到合适的 Agent"""
        online = self.get_online()

        if not online:
            self._log("warn", "No online agents available")
            return None

        if len(online) == 1:
            return online[0]

        if self.routing_mode == "keyword":
            for agent in online:
                if self._match_by_rules(message, agent):
                    return agent
            return self.get(self.default_agent) or online[0]

        elif self.routing_mode == "round_robin":
            channel = message.channel
            index = (self.round_robin_index.get(channel, 0) + 1) % len(online)
            self.round_robin_index[channel] = index
            return online[index]

        # first_available
        return online[0]

    async def handle_message(
        self,
        message: UnifiedMessage,
        session: Session,
        session_manager: Any,
        tool_gateway: Optional[ToolGateway] = None
    ) -> Dict[str, Any]:
        """处理消息"""
        
        # 检查是否是命令
        if message.content.strip().startswith("/"):
            cmd_result = process_command(message.content)
            if cmd_result:
                return {
                    "content": cmd_result.content,
                    "metadata": cmd_result.metadata
                }
        
        agent = self.route(message)

        if not agent:
            return {
                "content": "抱歉，暂无可用的 Agent 处理您的请求。",
                "metadata": {"error": "no_agent_available"}
            }

        # 更新会话关联的 Agent
        session_manager.update(session.id, {"agentId": agent.id})

        self._log("info", "Routing message to agent",
                   session_id=message.sessionId,
                   agent_id=agent.id,
                   agent_name=agent.name)

        if not agent.handler:
            return {
                "content": f"Agent {agent.name} 未配置处理函数",
                "metadata": {"error": "no_handler"}
            }

        try:
            context = AgentContext(
                session=session,
                sessionManager=session_manager,
                toolGateway=tool_gateway or ToolGateway(),
                logger=self.logger
            )

            response = await agent.handler(message, context)
            return {
                "content": response.content,
                "metadata": response.metadata
            }
        except Exception as e:
            self._log("error", "Agent handler error", agent_id=agent.id, error=str(e))
            return {
                "content": "处理您的请求时发生错误，请稍后重试。",
                "metadata": {"error": str(e)}
            }

    def get_stats(self) -> Dict:
        """获取统计"""
        agents = self.get_all()
        return {
            "total": len(agents),
            "online": sum(1 for a in agents if a.status == AgentStatus.ONLINE),
            "busy": sum(1 for a in agents if a.status == AgentStatus.BUSY),
            "offline": sum(1 for a in agents if a.status == AgentStatus.OFFLINE),
            "by_id": {a.id: {"name": a.name, "status": a.status.value if hasattr(a.status, "value") else a.status} for a in agents}
        }

    @staticmethod
    def create_simple_agent(
        agent_id: str,
        name: str,
        description: str,
        handler: AgentHandler
    ) -> Agent:
        """创建简单的 Agent"""
        return Agent(
            id=agent_id,
            name=name,
            description=description,
            version="1.0.0",
            status=AgentStatus.ONLINE,
            capabilities=[],
            handler=handler
        )

    def _log(self, level: str, message: str, **kwargs):
        if self.logger:
            getattr(self.logger, level)(message, **kwargs)
