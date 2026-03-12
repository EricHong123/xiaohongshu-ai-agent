from __future__ import annotations

from dataclasses import dataclass

from xiaohongshu_agent.apps.xhs.usecases.chat import chat


@dataclass
class _FakeProvider:
    def chat(self, messages):
        # Return deterministic output for test
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        return "OK"


@dataclass
class _FakeMemory:
    _history: list
    written: list

    def get_history(self, limit: int = 50):
        return self._history[-limit:]

    def add_message(self, role: str, content: str):
        self.written.append((role, content))


class _FakeAgent:
    def __init__(self):
        self.provider = _FakeProvider()
        self.memory = _FakeMemory(_history=[{"role": "user", "content": "hi"}], written=[])
        self.knowledge = [{"content": "AI Agent 自动化", "category": "AI"}]


def test_chat_writes_memory():
    agent = _FakeAgent()
    out = chat(agent, "hello")
    assert out == "OK"
    assert agent.memory.written[0][0] == "user"
    assert agent.memory.written[1][0] == "assistant"

