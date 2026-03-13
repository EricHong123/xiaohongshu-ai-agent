"""
WebSocket 服务器
参考 ai-agent-gateway/src/server/websocket.ts
"""
from typing import Dict, Any, Optional, Callable
import json
import uuid
from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room

from xiaohongshu_agent.gateway.types import UnifiedMessage
from xiaohongshu_agent.gateway.core import SessionManager, AgentRegistry, ToolGateway


class WebSocketServer:
    """WebSocket 服务器"""

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
        self.socketio: Optional[SocketIO] = None
        self.active_connections: Dict[str, Dict] = {}

    def create_app(self) -> SocketIO:
        """创建 Flask-SocketIO 应用"""
        app = Flask(__name__)
        app.config["JSON_AS_ASCII"] = False

        socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

        # 连接事件
        @socketio.on("connect")
        def handle_connect(auth=None):
            session_id = str(uuid.uuid4())
            self.active_connections[session_id] = {
                "session_id": session_id,
                "connected": True
            }
            emit("connected", {"session_id": session_id})
            self._log("info", "Client connected", session_id=session_id)

        # 断开连接
        @socketio.on("disconnect")
        def handle_disconnect():
            # 找到并移除连接
            for sid, conn in list(self.active_connections.items()):
                emit("disconnected", {"session_id": sid}, to=sid)
                del self.active_connections[sid]
            self._log("info", "Client disconnected")

        # 加入会话房间
        @socketio.on("join")
        def handle_join(data):
            session_id = data.get("session_id")
            if session_id:
                join_room(session_id)
                emit("joined", {"session_id": session_id})

        # 离开会话房间
        @socketio.on("leave")
        def handle_leave(data):
            session_id = data.get("session_id")
            if session_id:
                leave_room(session_id)
                emit("left", {"session_id": session_id})

        # 发送消息
        @socketio.on("message")
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

            # 创建消息
            message = UnifiedMessage(
                id=str(uuid.uuid4()),
                userId=user_id,
                channel="websocket",
                content=content,
                sessionId=session_id
            )

            # 添加到历史
            self.session_manager.add_message(session_id, "user", content)

            # 发送确认
            emit("message_sent", {"id": message.id, "sessionId": session_id})

            # 处理消息
            try:
                response = await self.agent_registry.handle_message(
                    message,
                    session,
                    self.session_manager,
                    self.tool_gateway
                )

                # 添加回复到历史
                self.session_manager.add_message(session_id, "assistant", response["content"])

                # 发送回复
                emit("response", {
                    "sessionId": session_id,
                    "content": response["content"],
                    "metadata": response.get("metadata")
                })

            except Exception as e:
                self._log("error", "Message handling failed", error=str(e))
                emit("error", {"message": str(e)})

        # 获取会话历史
        @socketio.on("history")
        def handle_history(data):
            session_id = data.get("sessionId")
            limit = data.get("limit", 50)

            if session_id:
                history = self.session_manager.get_history(session_id, limit)
                emit("history", {"sessionId": session_id, "history": history})

        # 心跳
        @socketio.on("ping")
        def handle_ping():
            emit("pong", {"timestamp": str(uuid.uuid4())})

        self.socketio = socketio
        return socketio

    def emit(self, event: str, data: Dict, room: str = None):
        """发送消息到客户端"""
        if self.socketio:
            if room:
                self.socketio.emit(event, data, room=room)
            else:
                self.socketio.emit(event, data)

    def run(self, host: str = "0.0.0.0", port: int = 3001, **kwargs):
        """运行服务器"""
        if not self.socketio:
            self.create_app()
        self.socketio.run(self.socketio.app, host=host, port=port, **kwargs)

    def _log(self, level: str, message: str, **kwargs):
        if self.logger:
            getattr(self.logger, level)(message, **kwargs)
