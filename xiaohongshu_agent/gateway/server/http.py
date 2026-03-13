"""
HTTP 服务器
参考 ai-agent-gateway/src/server/http.ts
"""
from typing import Dict, Any, Optional, Callable
from flask import Flask, request, jsonify
import uuid

from xiaohongshu_agent.gateway.types import UnifiedMessage
from xiaohongshu_agent.gateway.core import SessionManager, AgentRegistry, ToolGateway


class HttpServer:
    """HTTP 服务器"""

    def __init__(
        self,
        config: Dict,
        session_manager: SessionManager,
        agent_registry: AgentRegistry,
        tool_gateway: ToolGateway,
        logger: Optional[Any] = None
    ):
        self.config = config
        self.session_manager = session_manager
        self.agent_registry = agent_registry
        self.tool_gateway = tool_gateway
        self.logger = logger
        self.app: Optional[Flask] = None

    def create_app(self) -> Flask:
        """创建 Flask 应用"""
        app = Flask(__name__)
        app.config["JSON_AS_ASCII"] = False

        # 健康检查
        @app.route("/health", methods=["GET"])
        def health():
            return jsonify({
                "status": "ok",
                "service": "xiaohongshu-gateway"
            })

        # 发送消息
        @app.route("/api/v1/messages", methods=["POST"])
        async def send_message():
            data = request.json or {}
            user_id = data.get("userId", "anonymous")
            content = data.get("content", "")
            channel = data.get("channel", "http")
            session_id = data.get("sessionId")

            # 创建或获取会话
            if not session_id:
                session = self.session_manager.create(user_id, channel)
                session_id = session.id
            else:
                session = self.session_manager.get(session_id)
                if not session:
                    session = self.session_manager.create(user_id, channel, session_id)

            # 创建消息
            message = UnifiedMessage(
                id=str(uuid.uuid4()),
                userId=user_id,
                channel=channel,
                content=content,
                sessionId=session_id
            )

            # 添加到历史
            self.session_manager.add_message(session_id, "user", content)

            # 处理消息
            response = await self.agent_registry.handle_message(
                message,
                session,
                self.session_manager,
                self.tool_gateway
            )

            # 添加回复到历史
            self.session_manager.add_message(session_id, "assistant", response["content"])

            return jsonify({
                "sessionId": session_id,
                "response": response["content"],
                "metadata": response.get("metadata")
            })

        # 获取会话
        @app.route("/api/v1/sessions", methods=["GET"])
        def get_sessions():
            sessions = []
            for sid, session in self.session_manager.sessions.items():
                sessions.append({
                    "id": sid,
                    "userId": session.userId,
                    "channel": session.channel,
                    "agentId": session.agentId,
                    "createdAt": session.createdAt.isoformat(),
                    "updatedAt": session.updatedAt.isoformat()
                })
            return jsonify({"sessions": sessions})

        # 获取会话历史
        @app.route("/api/v1/sessions/<session_id>/history", methods=["GET"])
        def get_session_history(session_id):
            limit = request.args.get("limit", type=int)
            history = self.session_manager.get_history(session_id, limit)
            return jsonify({"sessionId": session_id, "history": history})

        # 删除会话
        @app.route("/api/v1/sessions/<session_id>", methods=["DELETE"])
        def delete_session(session_id):
            success = self.session_manager.delete(session_id)
            return jsonify({"success": success})

        # 获取 Agent 列表
        @app.route("/api/v1/agents", methods=["GET"])
        def get_agents():
            agents = self.agent_registry.get_all()
            return jsonify({
                "agents": [
                    {
                        "id": a.id,
                        "name": a.name,
                        "description": a.description,
                        "status": a.status.value,
                        "version": a.version,
                        "capabilities": [{"name": c.name, "description": c.description}
                                        for c in a.capabilities]
                    }
                    for a in agents
                ]
            })

        # 获取工具列表
        @app.route("/api/v1/tools", methods=["GET"])
        def get_tools():
            tools = self.tool_gateway.get_tool_list()
            return jsonify({"tools": tools})

        # 获取统计
        @app.route("/api/v1/stats", methods=["GET"])
        def get_stats():
            return jsonify({
                "sessions": self.session_manager.get_stats(),
                "agents": self.agent_registry.get_stats(),
                "tools": self.tool_gateway.get_stats()
            })

        self.app = app
        return app

    def run(self, host: str = "0.0.0.0", port: int = 3000, **kwargs):
        """运行服务器"""
        if not self.app:
            self.create_app()
        self.app.run(host=host, port=port, **kwargs)
