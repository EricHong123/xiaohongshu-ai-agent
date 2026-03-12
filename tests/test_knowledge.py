from xiaohongshu_agent.apps.xhs.services.knowledge import load_knowledge, retrieve_knowledge


def test_load_knowledge_non_empty():
    knowledge = load_knowledge()
    assert isinstance(knowledge, list)
    assert len(knowledge) > 0


def test_retrieve_knowledge_matches_keyword():
    knowledge = [
        {"content": "AI Agent 可以自动化", "category": "AI"},
        {"content": "无关内容", "category": "其他"},
    ]
    ctx = retrieve_knowledge(knowledge, "Agent")
    assert "自动化" in ctx

