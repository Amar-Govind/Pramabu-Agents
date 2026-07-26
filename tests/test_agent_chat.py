from pathlib import Path

from agent_chat.attachments import extract_text, summarize_attachments
from agent_chat.service import list_agents, run_chat_turn


def test_list_agents_includes_orchestrator_and_poster():
    agents = list_agents()
    names = {a["name"] for a in agents}
    assert "Orchestrator" in names
    assert "Poster Production" in names
    assert "Content Ideation" in names


def test_chat_turn_creates_downloadable_outputs(tmp_path):
    brief = tmp_path / "brief.txt"
    brief.write_text("Focus on Neem Soap and Virgin Coconut Oil for Instagram posters.", encoding="utf-8")

    session_dir = tmp_path / "session"
    result = run_chat_turn(
        message="create posters for neem soap",
        session_dir=session_dir,
        attachment_paths=[brief],
    )

    assert result["agent"] == "Poster Production"
    assert "Neem" in result["reply"] or "neem" in result["reply"].lower()
    assert result["files"]
    assert any(f["name"].endswith(".png") for f in result["files"])
    assert any(f["name"].endswith(".md") for f in result["files"])
    for item in result["files"]:
        assert Path(item["path"]).exists()


def test_chat_replies_differ_by_request(tmp_path):
    rose = run_chat_turn(
        message="create posters for rose soap",
        session_dir=tmp_path / "rose",
        attachment_paths=[],
    )
    crm = run_chat_turn(
        message="run crm agent for repeat purchase",
        session_dir=tmp_path / "crm",
        attachment_paths=[],
    )

    assert rose["agent"] == "Poster Production"
    assert crm["agent"] == "CRM"
    assert rose["reply"] != crm["reply"]
    assert "CRM" in crm["reply"] or "crm" in crm["reply"].lower() or "Welcome" in crm["reply"] or "reorder" in crm["reply"].lower()
    assert "Rose" in rose["reply"] or "rose" in rose["reply"].lower()


def test_extract_text_from_txt(tmp_path):
    path = tmp_path / "notes.md"
    path.write_text("# Hello\nWorld", encoding="utf-8")
    summary = summarize_attachments([path])
    assert "notes.md" in summary["combined_text"]
    assert "Hello" in extract_text(path)
