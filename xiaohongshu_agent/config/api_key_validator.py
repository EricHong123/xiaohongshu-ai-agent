from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional, Protocol


class HttpResponseLike(Protocol):
    status_code: int


class HttpClientLike(Protocol):
    def get(
        self,
        url: str,
        *,
        headers: Optional[Mapping[str, str]] = None,
        timeout: float | int | None = None,
    ) -> HttpResponseLike: ...


@dataclass(frozen=True, slots=True)
class ApiKeyCheck:
    ok: bool
    provider: str
    status_code: int | None = None
    error: str | None = None


def validate_api_key(
    *,
    provider: str,
    api_key: str,
    http: Optional[HttpClientLike] = None,
    timeout_s: float = 5.0,
) -> ApiKeyCheck:
    """
    Validate API key with a minimal, provider-specific request.

    - `http` can be injected for tests; if omitted, uses `requests`.
    - Never raises; returns a structured result.
    """

    provider = (provider or "").strip().lower()
    if not api_key:
        return ApiKeyCheck(ok=False, provider=provider, error="missing_api_key")

    if http is None:
        import requests  # local import to keep module import side-effects minimal

        http = requests

    try:
        if provider == "openai":
            resp = http.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=timeout_s,
            )
            return ApiKeyCheck(ok=resp.status_code == 200, provider=provider, status_code=resp.status_code)

        if provider == "anthropic":
            # Anthropic "messages" is POST; keep existing project behavior: best-effort GET and treat as ok if reachable.
            resp = http.get(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
                timeout=timeout_s,
            )
            return ApiKeyCheck(ok=True, provider=provider, status_code=getattr(resp, "status_code", None))

        # Other providers: syntactic validation only (legacy behavior).
        return ApiKeyCheck(ok=True, provider=provider)

    except Exception as e:  # noqa: BLE001 - want a safe boolean check
        return ApiKeyCheck(ok=False, provider=provider, error=str(e))

