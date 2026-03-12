from xiaohongshu_agent.apps.xhs.services.prompts import (
    build_chat_system_prompt,
    build_generate_content_prompt,
)


def test_build_chat_system_prompt_includes_context():
    p = build_chat_system_prompt("CTX")
    assert "专业" in p
    assert "CTX" in p


def test_build_generate_content_prompt_contains_json_shape():
    p = build_generate_content_prompt("- a")
    assert "JSON格式" in p
    assert '"title"' in p
    assert '"content"' in p
    assert '"tags"' in p

