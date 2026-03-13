"""
Combined HTTP + WebSocket Server
整合 HTTP 和 WebSocket 服务
"""
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
import uuid
import threading

from xiaohongshu_agent.gateway.types import UnifiedMessage
from xiaohongshu_agent.gateway.core import SessionManager, AgentRegistry, ToolGateway


class CombinedServer:
    """整合的 HTTP + WebSocket 服务器"""

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
        self.socketio: Optional[SocketIO] = None

    def create_app(self) -> Flask:
        """创建 Flask 应用（包含 HTTP 和 WebSocket）"""
        app = Flask(__name__)
        app.config["JSON_AS_ASCII"] = False
        self.socketio = SocketIO(app, cors_allowed_origions="*", async_mode="threading")

        # ==================== HTTP 端点 ====================

        # 健康检查
        @app.route("/health", methods=["GET"])
        def health():
            return jsonify({
                "status": "ok",
                "service": "xiaohongshu-gateway",
                "ws_enabled": self.socketio is not None
            })

        # 发送消息 (HTTP)
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

        # 获取会话列表
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
            limit = request.args.get("limit", 50, type=int)
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
                        "status": a.status.value if hasattr(a.status, 'value') else str(a.status),
                        "version": a.version,
                        "capabilities": [
                            {"name": c.name, "description": c.description}
                            for c in (a.capabilities or [])
                        ]
                    }
                    for a in agents
                ]
            })

        # 注册 Agent
        @app.route("/api/v1/agents", methods=["POST"])
        def register_agent():
            data = request.json or {}
            # 简化处理，实际应该传入完整的 Agent 对象
            return jsonify({"success": True, "message": "Agent 注册接口"})

        # 获取工具列表
        @app.route("/api/v1/tools", methods=["GET"])
        def get_tools():
            tools = self.tool_gateway.get_tool_list()
            return jsonify({"tools": tools})

        # 调用工具
        @app.route("/api/v1/tools/<tool_name>", methods=["POST"])
        async def call_tool(tool_name):
            params = request.json or {}
            result = await self.tool_gateway.call(tool_name, params, {})
            return jsonify(result)

        # 获取统计
        @app.route("/api/v1/stats", methods=["GET"])
        def get_stats():
            return jsonify({
                "sessions": self.session_manager.get_stats(),
                "agents": self.agent_registry.get_stats(),
                "tools": self.tool_gateway.get_stats()
            })

        # ==================== WebSocket 端点 ====================

        @self.socketio.on("connect")
        def handle_connect(auth=None):
            session_id = str(uuid.uuid4())
            self.socketio.emit("connected", {"session_id": session_id})
            self._log("info", "WS client connected")

        @self.socketio.on("disconnect")
        def handle_disconnect():
            self._log("info", "WS client disconnected")

        @self.socketio.on("message")
        async def handle_message(data):
            user_id = data.get("userId", "anonymous")
            content = data.get("content", "")
            session_id = data.get("sessionId")

            # 创建或获取会话
            if not session_id:
                session = self.session_manager.create(user_id, "websocket")
                session_id = session.id
            else:
                session = self.session_manager.get(session_id)
                if not session:
                    session = self.session_manager.create(user_id, "websocket", session_id)

            message = UnifiedMessage(
                id=str(uuid.uuid4()),
                userId=user_id,
                channel="websocket",
                content=content,
                sessionId=session_id
            )

            self.session_manager.add_message(session_id, "user", content)
            self.socketio.emit("message_sent", {"id": message.id, "sessionId": session_id})

            try:
                response = await self.agent_registry.handle_message(
                    message, session, self.session_manager, self.tool_gateway
                )
                self.session_manager.add_message(session_id, "assistant", response["content"])
                self.socketio.emit("response", {
                    "sessionId": session_id,
                    "content": response["content"],
                    "metadata": response.get("metadata")
                })
            except Exception as e:
                self.socketio.emit("error", {"message": str(e)})

        @self.socketio.on("history")
        def handle_history(data):
            session_id = data.get("sessionId")
            limit = data.get("limit", 50)
            if session_id:
                history = self.session_manager.get_history(session_id, limit)
                self.socketio.emit("history", {"sessionId": session_id, "history": history})

        @self.socketio.on("ping")
        def handle_ping():
            self.socketio.emit("pong", {"timestamp": str(uuid.uuid4())})

        self.app = app
        return app

    def run(self, http_port: int = 3000, ws_port: int = 3001):
        """运行服务器"""
        if not self.app:
            self.create_app()

        print(f"🚀 Gateway 服务启动")
        print(f"   HTTP:  http://localhost:{http_port}")
        print(f"   WebSocket: ws://localhost:{ws_port}")

        # 使用 SocketIO 运行（同时支持 HTTP 和 WebSocket）
        self.socketio.run(self.app, host="0.0.0.0", port=ws_port, debug=False, allow_unsafe_werkzeug=True)

    def run_separate(self, http_port: int = 3000, ws_port: int = 3001):
        """分离运行 HTTP 和 WebSocket"""
        if not self.app:
            self.create_app()

        # 可以在不同端口运行
        print(f"🚀 Gateway 服务启动")
        print(f"   HTTP:  http://localhost:{http_port}")
        print(f"   WebSocket: ws://localhost:{ws_port}")

        self.socketio.run(self.app, host="0.0.0.0", port=ws_port, debug=False, allow_unsafe_werkzeug=True)

    def _log(self, level: str, message: str, **kwargs):
        if self.logger:
            getattr(self.logger, level)(message, **kwargs)
