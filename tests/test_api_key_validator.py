from dataclasses import dataclass

from xiaohongshu_agent.config.api_key_validator import validate_api_key


@dataclass
class _Resp:
    status_code: int


class _Http:
    def __init__(self, status_code: int):
        self.status_code = status_code
        self.calls = []

    def get(self, url: str, *, headers=None, timeout=None):
        self.calls.append((url, dict(headers or {}), timeout))
        return _Resp(self.status_code)


def test_validate_openai_success():
    http = _Http(status_code=200)
    r = validate_api_key(provider="openai", api_key="k", http=http)
    assert r.ok is True
    assert http.calls[0][0].endswith("/v1/models")


def test_validate_openai_fail():
    http = _Http(status_code=401)
    r = validate_api_key(provider="openai", api_key="k", http=http)
    assert r.ok is False


def test_validate_anthropic_always_ok_when_reachable():
    http = _Http(status_code=400)
    r = validate_api_key(provider="anthropic", api_key="k", http=http)
    assert r.ok is True
    assert "anthropic-version" in http.calls[0][1]


def test_validate_missing_key():
    r = validate_api_key(provider="openai", api_key="")
    assert r.ok is False

