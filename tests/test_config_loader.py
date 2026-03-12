from xiaohongshu_agent.config.loader import PROVIDERS_INFO, load_config


def test_providers_env_keys_are_not_secrets():
    # env_key 应该是环境变量名，而不是某个真实 key
    for provider, info in PROVIDERS_INFO.items():
        env_key = info.get("env_key", "")
        assert isinstance(env_key, str)
        assert env_key.endswith("_API_KEY")
        assert "sk-" not in env_key.lower()
        assert "." not in env_key  # 避免把 token/密钥写进源码


def test_load_config_reads_env_defaults(monkeypatch, tmp_path):
    # Isolate from user's real ~/.xiaohongshu_agent/config.json
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("XIAOHONGSHU_MCP_URL", "http://example.com/mcp")

    cfg = load_config()
    assert cfg.get("llm_provider") == "openai"
    assert cfg.get("mcp_url") == "http://example.com/mcp"


def test_get_api_key_prefers_env(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("LLM_PROVIDER", "minimax")
    monkeypatch.setenv("MINIMAX_API_KEY", "dummy-key")
    cfg = load_config()
    assert cfg.get_api_key() == "dummy-key"

