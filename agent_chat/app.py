from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from agent_chat.attachments import safe_filename
from agent_chat.service import list_agents, run_chat_turn

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
CHAT_OUTPUT_ROOT = Path("output/chat")
CHAT_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Parambu Agent Chat", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "service": "parambu-agent-chat"}


@app.get("/api/agents")
def agents() -> dict:
    return {"agents": list_agents()}


@app.post("/api/chat")
async def chat(
    message: str = Form(""),
    session_id: str = Form(""),
    files: list[UploadFile] | None = File(default=None),
) -> dict:
    sid = session_id.strip() or uuid.uuid4().hex
    session_dir = CHAT_OUTPUT_ROOT / sid
    uploads_dir = session_dir / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    saved: list[Path] = []
    for upload in files or []:
        if not upload.filename:
            continue
        dest = uploads_dir / safe_filename(upload.filename)
        # Avoid overwrite collisions
        if dest.exists():
            dest = uploads_dir / f"{uuid.uuid4().hex[:8]}_{safe_filename(upload.filename)}"
        content = await upload.read()
        dest.write_bytes(content)
        saved.append(dest)

    try:
        result = run_chat_turn(
            message=message,
            session_dir=session_dir,
            attachment_paths=saved,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "session_id": sid,
        "agent": result.get("agent", "Orchestrator"),
        "reply": result["reply"],
        "files": result["files"],
        "intent": result.get("intent"),
        "mode": result.get("mode"),
        "focus": result.get("focus"),
        "pack": result.get("pack"),
        "uploads": [path.name for path in saved],
    }


@app.get("/api/files/{session_id}/{file_path:path}")
def download_file(session_id: str, file_path: str) -> FileResponse:
    # Prevent path traversal
    if ".." in session_id or ".." in file_path:
        raise HTTPException(status_code=400, detail="Invalid path")
    target = (CHAT_OUTPUT_ROOT / session_id / file_path).resolve()
    root = CHAT_OUTPUT_ROOT.resolve()
    if not str(target).startswith(str(root)) or not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(target, filename=target.name)


def main() -> None:
    import uvicorn

    uvicorn.run("agent_chat.app:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
