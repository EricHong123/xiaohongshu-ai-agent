#!/usr/bin/env python3
"""
LLM 适配器 - 支持多种大模型提供商
"""
import json
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from config import LLMConfig, get_llm_config


# ============== 基类 ==============
class LLMAdapter(ABC):
    """LLM 适配器基类"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        pass

    @abstractmethod
    def chat_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict]) -> str:
        """带工具调用"""
        pass

    def format_messages(self, system: str, user: str) -> List[Dict[str, str]]:
        """格式化消息"""
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]


# ============== OpenAI 适配器 ==============
class OpenAIAdapter(LLMAdapter):
    """OpenAI 适配器"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=config.api_key)
        except ImportError:
            print("⚠️ 未安装 openai 库，使用 HTTP 请求")

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        if self.client:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            )
            return response.choices[0].message.content
        else:
            # HTTP 请求
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.config.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            }
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            return resp.json()["choices"][0]["message"]["content"]

    def chat_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict]) -> str:
        if not self.client:
            return self.chat(messages)

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            tools=tools,
            temperature=self.config.temperature,
        )

        if response.choices[0].message.tool_calls:
            return response.choices[0].message.tool_calls[0]
        return response.choices[0].message.content


# ============== Anthropic 适配器 ==============
class AnthropicAdapter(LLMAdapter):
    """Anthropic (Claude) 适配器"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=config.api_key)
        except ImportError:
            print("⚠️ 未安装 anthropic 库")

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        if not self.client:
            return "Anthropic 库未安装"

        # 转换消息格式
        system = messages[0]["content"] if messages[0]["role"] == "system" else ""
        user_msgs = [m for m in messages if m["role"] != "system"]

        response = self.client.messages.create(
            model=self.config.model,
            system=system,
            messages=user_msgs,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
        )
        return response.content[0].text

    def chat_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict]) -> str:
        return self.chat(messages)


# ============== 智谱 GLM 适配器 ==============
class ZhipuAdapter(LLMAdapter):
    """智谱 GLM 适配器"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://open.bigmodel.cn/api/paas/v4"

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }

        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )

        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        return f"Error: {resp.text}"

    def chat_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict]) -> str:
        return self.chat(messages)


# ============== Minimax 适配器 ==============
class MinimaxAdapter(LLMAdapter):
    """Minimax 适配器"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.minimax.chat/v1"

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        # Minimax 需要特殊格式
        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }

        resp = requests.post(
            f"{self.base_url}/text/chatcompletion_v2",
            headers=headers,
            json=data
        )

        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        return f"Error: {resp.text}"

    def chat_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict]) -> str:
        return self.chat(messages)


# ============== Kimi 适配器 ==============
class KimiAdapter(LLMAdapter):
    """Kimi (月之暗面) 适配器"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.moonshot.cn/v1"

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }

        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )

        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        return f"Error: {resp.text}"

    def chat_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict]) -> str:
        return self.chat(messages)


# ============== Gemini 适配器 ==============
class GeminiAdapter(LLMAdapter):
    """Google Gemini 适配器"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        import google.generativeai as genai

        genai.configure(api_key=self.config.api_key)

        model = genai.GenerativeModel(self.config.model)

        # 转换消息格式
        system = ""
        chat_msgs = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                chat_msgs.append(msg)

        if system:
            model = genai.GenerativeModel(
                self.config.model,
                system_instruction=system
            )

        response = model.generate_content(
            chat_msgs[-1]["content"] if chat_msgs else "",
            generation_config={
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_output_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            }
        )
        return response.text

    def chat_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict]) -> str:
        return self.chat(messages)


# ============== 工厂函数 ==============
def create_llm_adapter(config: LLMConfig = None) -> LLMAdapter:
    """创建 LLM 适配器"""
    config = config or get_llm_config()

    adapters = {
        "openai": OpenAIAdapter,
        "anthropic": AnthropicAdapter,
        "zhipu": ZhipuAdapter,
        "minimax": MinimaxAdapter,
        "kimi": KimiAdapter,
        "gemini": GeminiAdapter,
    }

    adapter_class = adapters.get(config.provider, OpenAIAdapter)
    return adapter_class(config)


# ============== 测试 ==============
if __name__ == "__main__":
    # 测试各适配器
    print("🧪 测试 LLM 适配器")
    print("=" * 50)

    # 测试 OpenAI
    print("\n[1] OpenAI 测试")
    try:
        adapter = create_llm_adapter(LLMConfig(provider="openai", api_key="test"))
        print(f"   适配器: {type(adapter).__name__}")
    except Exception as e:
        print(f"   错误: {e}")

    # 测试智谱
    print("\n[2] 智谱 GLM 测试")
    try:
        adapter = create_llm_adapter(LLMConfig(provider="zhipu", api_key="test"))
        print(f"   适配器: {type(adapter).__name__}")
    except Exception as e:
        print(f"   错误: {e}")

    # 测试 Kimi
    print("\n[3] Kimi 测试")
    try:
        adapter = create_llm_adapter(LLMConfig(provider="kimi", api_key="test"))
        print(f"   适配器: {type(adapter).__name__}")
    except Exception as e:
        print(f"   错误: {e}")

    # 测试 Gemini
    print("\n[4] Gemini 测试")
    try:
        adapter = create_llm_adapter(LLMConfig(provider="gemini", api_key="test"))
        print(f"   适配器: {type(adapter).__name__}")
    except Exception as e:
        print(f"   错误: {e}")

    print("\n✅ LLM 适配器创建完成")
