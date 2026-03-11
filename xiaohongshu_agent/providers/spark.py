"""
讯飞星火 (Spark) 提供商
"""
import os
import requests
import base64
import hashlib
import time
from typing import List, Dict, Any

from xiaohongshu_agent.providers.base import BaseProvider


class SparkProvider(BaseProvider):
    """讯飞星火 LLM 提供商"""

    def __init__(self, api_key: str = "", base_url: str = "", model: str = "spark-4.0"):
        super().__init__(api_key, base_url, model)
        self.api_key = api_key or os.getenv("SPARK_API_KEY", "")
        self.app_id = os.getenv("SPARK_APP_ID", "")
        self.model = model or os.getenv("SPARK_MODEL", "spark-4.0")

        # 模型与domain对应
        self.model_domain = {
            "spark-4.0": "generalv4.0",
            "spark-3.5": "generalv3.5",
            "spark-3.0": "generalv3.0",
            "spark-v3.5": "generalv3.5",
        }

    def _get_auth_url(self) -> str:
        """生成鉴权URL"""
        host = "spark-api.xf-yun.com"
        path = "/v3.5/chat"

        # 生成鉴权参数
        now = time.gmtime(time.time())
        date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", now)

        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"

        # 使用API Secret进行HMAC-SHA256签名
        import hmac
        import base64

        api_secret = os.getenv("SPARK_API_SECRET", "")
        signature_sha = hmac.new(
            api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode('utf-8')

        authorization_origin = (
            f'api_key="{self.api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature_sha_base64}"'
        )
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

        return f"wss://{host}{path}?authorization={authorization}&date={date}&host={host}"

    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """发送聊天请求 (需要WebSocket)"""
        try:
            import websocket

            domain = self.model_domain.get(self.model, "generalv3.5")

            # 构建请求
            request_data = {
                "header": {
                    "app_id": self.app_id
                },
                "parameter": {
                    "chat": {
                        "domain": domain,
                        "temperature": 0.5,
                        "max_tokens": 2048
                    }
                },
                "payload": {
                    "message": {
                        "text": messages
                    }
                }
            }

            # 这里简化处理,实际需要WebSocket
            # 建议使用官方SDK: pip install spark_api
            return "讯飞星火需要使用WebSocket连接,请使用官方SDK"

        except Exception as e:
            return f"讯飞星火 调用失败: {e}"

    def get_name(self) -> str:
        return "讯飞星火"
