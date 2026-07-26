from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path
from typing import Any

from pramabu_agents.agents import (
    AnalyticsAgent,
    BrandGuardianAgent,
    BusinessGrowthAgent,
    ContentIdeationAgent,
    CreativeProductionAgent,
    CrisisPRAgent,
    CRMAgent,
    EcommerceAgent,
    InfluencerAgent,
    LocalizationAgent,
    MarketAnalysisAgent,
    MarketplaceAgent,
    PerformanceMarketingAgent,
    PosterProductionAgent,
    QAAgent,
    SocialMediaAgent,
    SupplyChainAgent,
    TrendScoutAgent,
)
from pramabu_agents.config import load_brand, llm_enabled
from pramabu_agents.models import CampaignPack
from pramabu_agents.orchestrator import Orchestrator
from pramabu_agents.report import pack_to_markdown, write_outputs

AGENT_CATALOG = [
    ("trend scout", TrendScoutAgent, "Finds current social/content trends"),
    ("market analysis", MarketAnalysisAgent, "Category and demand insights"),
    ("content ideation", ContentIdeationAgent, "Ideas for posters, reels, shorts"),
    ("creative production", CreativeProductionAgent, "Headlines, scripts, visual briefs"),
    ("brand guardian", BrandGuardianAgent, "Tone and claims compliance"),
    ("poster production", PosterProductionAgent, "Renders poster PNG assets"),
    ("social media", SocialMediaAgent, "Weekly calendar and captions"),
    ("ecommerce", EcommerceAgent, "PDP and site improvement actions"),
    ("e-commerce", EcommerceAgent, "PDP and site improvement actions"),
    ("performance marketing", PerformanceMarketingAgent, "Paid media plan"),
    ("business growth", BusinessGrowthAgent, "Growth opportunities"),
    ("marketplace", MarketplaceAgent, "Amazon/Flipkart listing actions"),
    ("influencer", InfluencerAgent, "Creator seeding and UGC"),
    ("crm", CRMAgent, "Lifecycle and retention actions"),
    ("supply chain", SupplyChainAgent, "Inventory and fulfillment readiness"),
    ("crisis", CrisisPRAgent, "Crisis and PR readiness"),
    ("crisis & pr", CrisisPRAgent, "Crisis and PR readiness"),
    ("localization", LocalizationAgent, "Tamil/English localization plan"),
    ("analytics", AnalyticsAgent, "Measurement plan"),
    ("qa", QAAgent, "Approval gate"),
]


def list_agents() -> list[dict[str, str]]:
    seen: set[str] = set()
    rows = []
    for name, cls, role in AGENT_CATALOG:
        key = cls.__name__
        if key in seen:
            continue
        seen.add(key)
        rows.append({"name": cls(load_brand()).name, "key": name, "role": role})
    rows.insert(0, {"name": "Orchestrator", "key": "weekly", "role": "Full weekly campaign pipeline"})
    return rows


def _match_agent(message: str):
    lowered = message.lower()
    # Prefer longer keys first
    for key, cls, _role in sorted(AGENT_CATALOG, key=lambda row: len(row[0]), reverse=True):
        if key in lowered:
            return key, cls
    return None, None


def _intent(message: str) -> str:
    lowered = message.lower().strip()
    if not lowered:
        return "help"
    if any(token in lowered for token in ("help", "what can you", "how do i")):
        return "help"
    if any(token in lowered for token in ("list agents", "show agents", "which agents")):
        return "list_agents"
    if any(token in lowered for token in ("run all", "weekly", "campaign pack", "full pipeline")):
        return "weekly"
    if "poster" in lowered and "only" not in lowered:
        # "create posters" / "make a poster" → poster-focused mini pipeline
        if any(token in lowered for token in ("create", "make", "generate", "render", "design")):
            return "posters"
    matched, _ = _match_agent(lowered)
    if matched:
        return "single_agent"
    return "weekly"


def _enrich_objective(message: str, attachment_summary: dict[str, Any]) -> str:
    parts = [message.strip() or "Grow D2C sales on parambu.in"]
    if attachment_summary.get("notes"):
        parts.append("Attachments: " + "; ".join(attachment_summary["notes"]))
    if attachment_summary.get("combined_text"):
        excerpt = attachment_summary["combined_text"][:2500]
        parts.append("Reference document excerpts:\n" + excerpt)
    return "\n\n".join(parts)


def _collect_files(session_dir: Path, pack: CampaignPack) -> list[dict[str, str]]:
    files: list[dict[str, str]] = []
    for poster in pack.posters:
        src = Path(poster.path)
        if not src.exists():
            continue
        dest = session_dir / "outputs" / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.resolve() != dest.resolve():
            shutil.copy2(src, dest)
        files.append(
            {
                "name": dest.name,
                "path": str(dest),
                "kind": "poster",
                "url": f"/api/files/{session_dir.name}/outputs/{dest.name}",
            }
        )

    for pattern in (f"campaign_{pack.week_of}.md", f"campaign_{pack.week_of}.json"):
        src = session_dir / pattern
        if src.exists():
            files.append(
                {
                    "name": src.name,
                    "path": str(src),
                    "kind": "report",
                    "url": f"/api/files/{session_dir.name}/{src.name}",
                }
            )
    return files


def _pack_reply(pack: CampaignPack, title: str) -> str:
    lines = [
        f"**{title}**",
        "",
        f"- Brand: {pack.brand}",
        f"- Week: {pack.week_of}",
        f"- Objective: {pack.objective}",
        f"- Approved: {'yes' if pack.approved else 'needs review'}",
        f"- Ideas: {len(pack.ideas)} · Creatives: {len(pack.creatives)} · Posters: {len(pack.posters)}",
        "",
    ]
    if pack.ideas:
        lines.append("**Content ideas**")
        for idea in pack.ideas[:5]:
            lines.append(f"- {idea.title} ({idea.format}) — _{idea.hook}_")
        lines.append("")
    if pack.posters:
        lines.append("**Posters ready to download**")
        for poster in pack.posters:
            lines.append(f"- {poster.idea_title}")
        lines.append("")
    if pack.growth_opportunities:
        lines.append("**Growth opportunities**")
        for item in pack.growth_opportunities[:3]:
            lines.append(f"- {item}")
        lines.append("")
    lines.append("Full campaign markdown and files are attached below.")
    return "\n".join(lines)


def run_chat_turn(
    *,
    message: str,
    session_dir: Path,
    attachment_paths: list[Path],
) -> dict[str, Any]:
    from agent_chat.attachments import summarize_attachments

    brand = load_brand()
    attachment_summary = summarize_attachments(attachment_paths)
    intent = _intent(message)
    mode = "LLM" if llm_enabled() else "template"
    objective = _enrich_objective(message, attachment_summary)
    context = {
        "output_dir": str(session_dir),
        "content_pieces": 5,
        "growth_ideas": 4,
        "uploaded_images": attachment_summary["images"],
        "uploaded_documents": [d["name"] for d in attachment_summary["documents"]],
    }

    # Copy reference images into session inputs for traceability
    inputs_dir = session_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)

    if intent == "help":
        return {
            "reply": (
                "**Parambu Agent Chat**\n\n"
                "You can:\n"
                "- Ask for a full weekly campaign (`run weekly campaign`)\n"
                "- Ask a specialist (`run influencer agent`, `crm plan`, `create posters`)\n"
                "- Upload briefs, PDFs, images, or spreadsheets as context\n\n"
                "Generated posters and reports appear as downloadable files in the reply."
            ),
            "files": [],
            "intent": intent,
            "mode": mode,
        }

    if intent == "list_agents":
        rows = list_agents()
        body = ["**Available agents**", ""]
        for row in rows:
            body.append(f"- **{row['name']}** — {row['role']}")
        return {"reply": "\n".join(body), "files": [], "intent": intent, "mode": mode}

    pack: CampaignPack
    title: str

    if intent == "posters":
        pack = CampaignPack(
            brand=brand.get("brand", {}).get("name", "Parambu Organics"),
            week_of=date.today().isoformat(),
            objective=objective,
        )
        pack = TrendScoutAgent(brand).run(pack, context)
        pack = ContentIdeationAgent(brand).run(pack, context)
        pack = CreativeProductionAgent(brand).run(pack, context)
        pack = BrandGuardianAgent(brand).run(pack, context)
        # Force poster formats for generation when user asked for posters
        for creative in pack.creatives:
            if creative.format.lower() not in {"poster", "carousel"}:
                creative.format = "poster"
        pack = PosterProductionAgent(brand).run(pack, context)
        title = "Poster production complete"
    elif intent == "single_agent":
        key, cls = _match_agent(message)
        pack = CampaignPack(
            brand=brand.get("brand", {}).get("name", "Parambu Organics"),
            week_of=date.today().isoformat(),
            objective=objective,
        )
        # Seed upstream context for agents that need ideas/creatives
        if cls in {CreativeProductionAgent, BrandGuardianAgent, PosterProductionAgent, SocialMediaAgent, QAAgent}:
            pack = ContentIdeationAgent(brand).run(pack, context)
            pack = CreativeProductionAgent(brand).run(pack, context)
        if cls is PosterProductionAgent:
            pack = BrandGuardianAgent(brand).run(pack, context)
            for creative in pack.creatives:
                creative.format = "poster"
        agent = cls(brand)
        pack = agent.run(pack, context)
        title = f"{agent.name} finished"
    else:
        pack = Orchestrator(brand).run_weekly_campaign(
            objective=objective,
            week_of=date.today().isoformat(),
            context=context,
        )
        title = "Weekly campaign pack ready"

    write_outputs(pack, session_dir)
    # Also keep a short chat-facing markdown snippet file
    snippet = session_dir / "latest_reply.md"
    reply = _pack_reply(pack, title)
    if attachment_summary["notes"]:
        reply += "\n\n**Using your uploads**\n" + "\n".join(f"- {n}" for n in attachment_summary["notes"])
    snippet.write_text(reply + "\n\n---\n\n" + pack_to_markdown(pack), encoding="utf-8")

    files = _collect_files(session_dir, pack)
    files.append(
        {
            "name": "latest_reply.md",
            "path": str(snippet),
            "kind": "report",
            "url": f"/api/files/{session_dir.name}/latest_reply.md",
        }
    )

    return {
        "reply": reply,
        "files": files,
        "intent": intent,
        "mode": mode,
        "pack": {
            "week_of": pack.week_of,
            "approved": pack.approved,
            "ideas": len(pack.ideas),
            "creatives": len(pack.creatives),
            "posters": len(pack.posters),
        },
    }
