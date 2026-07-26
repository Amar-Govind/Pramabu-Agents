from pathlib import Path

from agent_chat.attachments import extract_text, summarize_attachments
from agent_chat.knowledge import retrieve_knowledge
from agent_chat.service import list_agents, run_chat_turn


def test_list_agents_includes_assistant_and_poster():
    agents = list_agents()
    names = {a["name"] for a in agents}
    assert "Parambu Assistant" in names
    assert "Poster Production" in names
    assert "Content Ideation" in names


def test_knowledge_retrieval_finds_product():
    chunks = retrieve_knowledge("Tell me about Rose Soap benefits")
    blob = " ".join(c["text"] for c in chunks).lower()
    assert "rose" in blob


def test_chat_answers_from_knowledge_without_tool(tmp_path):
    result = run_chat_turn(
        message="What’s special about Rose Soap?",
        session_dir=tmp_path / "ask",
        attachment_paths=[],
    )
    assert result["agent"] == "Parambu Assistant"
    assert result["intent"] == "chat"
    assert "Rose" in result["reply"] or "rose" in result["reply"].lower()
    assert result["files"] == []


def test_chat_turn_creates_downloadable_outputs(tmp_path):
    brief = tmp_path / "brief.txt"
    brief.write_text("Focus on Neem Soap Instagram posters.", encoding="utf-8")

    session_dir = tmp_path / "session"
    result = run_chat_turn(
        message="create posters for neem soap",
        session_dir=session_dir,
        attachment_paths=[brief],
    )

    assert result["agent"] == "Poster Production"
    assert "Neem" in result["reply"] or "neem" in result["reply"].lower() or "poster" in result["reply"].lower()
    assert result["files"]
    assert any(f["name"].endswith(".png") for f in result["files"])
    for item in result["files"]:
        assert Path(item["path"]).exists()


def test_chat_keeps_history(tmp_path):
    session = tmp_path / "hist"
    first = run_chat_turn(
        message="What’s special about Rose Soap?",
        session_dir=session,
        attachment_paths=[],
    )
    second = run_chat_turn(
        message="What price is it?",
        session_dir=session,
        attachment_paths=[],
    )
    assert first["reply"]
    assert second["reply"]
    assert (session / "history.json").exists()


def test_extract_text_from_txt(tmp_path):
    path = tmp_path / "notes.md"
    path.write_text("# Hello\nWorld", encoding="utf-8")
    summary = summarize_attachments([path])
    assert "notes.md" in summary["combined_text"]
    assert "Hello" in extract_text(path)
