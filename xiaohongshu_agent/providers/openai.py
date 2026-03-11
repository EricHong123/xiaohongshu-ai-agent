"""
OpenAI 提供商
支持 GPT-4.5, o1, o3 等最新模型
"""
import os
from typing import List, Dict, Any, Optional

from xiaohongshu_agent.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    """OpenAI LLM 提供商"""

    # o1/o3 系列需要特殊处理
    REASONING_MODELS = ["o1", "o1-mini", "o1-preview", "o3", "o3-mini"]

    def __init__(self, api_key: str = "", base_url: str = "", model: str = "gpt-4o"):
        super().__init__(api_key, base_url, model)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")

    def chat(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """发送聊天请求"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)

            # o1/o3 系列不支持 system message,需要特殊处理
            if self.model in self.REASONING_MODELS:
                return self._chat_reasoning(client, messages)
            else:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    **kwargs
                )
                return response.choices[0].message.content

        except Exception as e:
            return f"OpenAI 调用失败: {e}"

    def _chat_reasoning(self, client, messages: List[Dict[str, Any]]) -> str:
        """处理 o1/o3 推理模型"""
        # o1/o3 只支持 user 消息,把 system 合并到 user
        filtered_messages = []
        system_content = ""

        for msg in messages:
            if msg.get("role") == "system":
                system_content = msg.get("content", "")
            elif msg.get("role") == "user":
                if system_content:
                    # 合并 system 到 user
                    msg["content"] = f"{system_content}\n\n{msg.get('content', '')}"
                    system_content = ""
                filtered_messages.append(msg)
            else:
                # o1/o3 不支持 assistant 消息历史,只保留 user
                pass

        response = client.chat.completions.create(
            model=self.model,
            messages=filtered_messages,
        )
        return response.choices[0].message.content

    def chat_with_reasoning(
        self,
        messages: List[Dict[str, Any]],
        reasoning_effort: Optional[str] = None
    ) -> str:
        """发送带推理过程的聊天请求 (o1/o3)"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)

            # 构建请求
            kwargs = {
                "model": self.model,
                "messages": messages,
            }

            # 添加 reasoning_effort 参数 (仅 o1-mini 支持)
            if reasoning_effort and "o1-mini" in self.model:
                kwargs["reasoning_effort"] = reasoning_effort

            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content

        except Exception as e:
            return f"OpenAI 调用失败: {e}"

    def get_name(self) -> str:
        return "OpenAI"
