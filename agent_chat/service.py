from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path
from typing import Any

from agent_chat.focus import extract_focus
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
    for key, cls, _role in sorted(AGENT_CATALOG, key=lambda row: len(row[0]), reverse=True):
        if key in lowered:
            return key, cls
    # Also match display names like "Content Ideation"
    for _key, cls, _role in AGENT_CATALOG:
        agent_name = cls(load_brand()).name.lower()
        if agent_name in lowered:
            return agent_name, cls
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
    if "poster" in lowered:
        if any(token in lowered for token in ("create", "make", "generate", "render", "design", "poster production")):
            return "posters"
    matched, _ = _match_agent(lowered)
    if matched:
        return "single_agent"
    return "weekly"


def _enrich_objective(message: str, attachment_summary: dict[str, Any], focus: dict[str, Any]) -> str:
    parts = [message.strip() or "Grow D2C sales on parambu.in"]
    if focus.get("product_names"):
        parts.append("Focus products: " + ", ".join(focus["product_names"]))
    if focus.get("categories"):
        parts.append("Focus categories: " + ", ".join(focus["categories"]))
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


def _section(title: str, items: list[str], limit: int = 6) -> list[str]:
    if not items:
        return []
    lines = [f"**{title}**"]
    lines.extend(f"- {item}" for item in items[:limit])
    lines.append("")
    return lines


def _pack_reply(pack: CampaignPack, *, agent_name: str, intent: str, focus: dict[str, Any]) -> str:
    lines = [
        f"### {agent_name}",
        "",
        f"**Request:** {focus.get('raw') or pack.objective.splitlines()[0]}",
    ]
    if focus.get("product_names"):
        lines.append("**Focus:** " + ", ".join(focus["product_names"]))
    lines.extend(
        [
            f"**Week:** {pack.week_of}",
            f"**Approved:** {'yes' if pack.approved else 'needs review'}",
            "",
        ]
    )

    # Intent / agent-specific body so replies don't look identical
    if intent == "posters" or agent_name == "Poster Production":
        lines.extend(_section("Poster concepts", [f"{p.idea_title} — {p.headline}" for p in pack.posters], 8))
        if not pack.posters:
            lines.extend(_section("Creative headlines", [f"{c.idea_title}: {c.headline}" for c in pack.creatives], 5))
    elif agent_name == "CRM":
        lines.extend(_section("CRM actions", pack.crm_actions))
    elif agent_name == "Influencer":
        lines.extend(_section("Influencer / UGC plan", pack.influencer_plan))
    elif agent_name == "Marketplace":
        lines.extend(_section("Marketplace actions", pack.marketplace_actions))
    elif agent_name == "Supply Chain":
        lines.extend(_section("Supply chain actions", pack.supply_chain_actions))
    elif agent_name == "Crisis & PR":
        lines.extend(_section("Crisis & PR plan", pack.crisis_pr_plan))
    elif agent_name == "Localization":
        lines.extend(_section("Localization plan", pack.localization_plan))
    elif agent_name == "Business Growth":
        lines.extend(_section("Growth opportunities", pack.growth_opportunities))
    elif agent_name == "Performance Marketing":
        lines.extend(_section("Ad plan", pack.ad_plan))
    elif agent_name == "E-commerce Website":
        lines.extend(_section("E-commerce actions", pack.ecommerce_actions))
    elif agent_name == "Social Media Manager":
        lines.extend(
            _section(
                "Social calendar",
                [
                    f"{p.day} | {p.platform} | {p.format} — {p.creative_ref}"
                    for p in pack.social_calendar
                ],
                8,
            )
        )
    elif agent_name == "Analytics & BI":
        lines.extend(_section("Analytics plan", pack.analytics_plan))
    elif agent_name == "Trend Scout":
        lines.extend(_section("Trends", pack.trends))
    elif agent_name == "Market Analysis":
        lines.extend(_section("Insights", pack.insights))
    elif agent_name == "Content Ideation":
        lines.extend(
            _section(
                "Content ideas",
                [f"{i.title} ({i.format}) — {i.hook}" for i in pack.ideas],
                8,
            )
        )
    elif agent_name == "Creative Production":
        lines.extend(
            _section(
                "Creative briefs",
                [f"{c.idea_title}: {c.headline}" for c in pack.creatives],
                8,
            )
        )
    elif agent_name == "Brand Guardian":
        lines.extend(_section("QA / brand flags", pack.qa_flags or ["No brand flags. Creatives look safe."], 8))
    elif agent_name == "QA":
        lines.extend(_section("QA flags", pack.qa_flags or ["No blockers. Ready for review."], 8))
    else:
        # Orchestrator / weekly: mixed summary tailored by focus
        lines.extend(
            _section(
                "Content ideas",
                [f"{i.title} ({i.format}) — {i.hook}" for i in pack.ideas],
                5,
            )
        )
        lines.extend(
            _section(
                "Creatives",
                [f"{c.idea_title}: {c.headline}" for c in pack.creatives],
                4,
            )
        )
        lines.extend(_section("Growth opportunities", pack.growth_opportunities, 3))
        lines.extend(_section("CRM actions", pack.crm_actions, 3))
        if pack.posters:
            lines.extend(_section("Posters ready", [p.idea_title for p in pack.posters], 6))

    lines.append("Download the files below for full details.")
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
    focus = extract_focus(message, brand)
    intent = _intent(message)
    mode = "LLM" if llm_enabled() else "template"
    objective = _enrich_objective(message, attachment_summary, focus)
    context = {
        "output_dir": str(session_dir),
        "content_pieces": 5,
        "growth_ideas": 4,
        "uploaded_images": attachment_summary["images"],
        "uploaded_documents": [d["name"] for d in attachment_summary["documents"]],
        "focus": focus,
        "user_message": message,
    }

    inputs_dir = session_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)

    if intent == "help":
        return {
            "agent": "Orchestrator",
            "reply": (
                "### Orchestrator\n\n"
                "You can:\n"
                "- Ask for a full weekly campaign (`run weekly campaign`)\n"
                "- Ask a specialist (`run influencer agent`, `crm plan`, `create posters for rose soap`)\n"
                "- Upload briefs, PDFs, images, or spreadsheets as context\n\n"
                "Generated posters and reports appear as downloadable files in the reply."
            ),
            "files": [],
            "intent": intent,
            "mode": mode,
        }

    if intent == "list_agents":
        rows = list_agents()
        body = ["### Orchestrator", "", "**Available agents**", ""]
        for row in rows:
            body.append(f"- **{row['name']}** — {row['role']}")
        return {
            "agent": "Orchestrator",
            "reply": "\n".join(body),
            "files": [],
            "intent": intent,
            "mode": mode,
        }

    pack: CampaignPack
    agent_name: str

    if intent == "posters":
        agent_name = "Poster Production"
        pack = CampaignPack(
            brand=brand.get("brand", {}).get("name", "Parambu Organics"),
            week_of=date.today().isoformat(),
            objective=objective,
        )
        pack = TrendScoutAgent(brand).run(pack, context)
        pack = ContentIdeationAgent(brand).run(pack, context)
        pack = CreativeProductionAgent(brand).run(pack, context)
        pack = BrandGuardianAgent(brand).run(pack, context)
        for creative in pack.creatives:
            creative.format = "poster"
        pack = PosterProductionAgent(brand).run(pack, context)
    elif intent == "single_agent":
        _key, cls = _match_agent(message)
        pack = CampaignPack(
            brand=brand.get("brand", {}).get("name", "Parambu Organics"),
            week_of=date.today().isoformat(),
            objective=objective,
        )
        if cls in {
            CreativeProductionAgent,
            BrandGuardianAgent,
            PosterProductionAgent,
            SocialMediaAgent,
            QAAgent,
        }:
            pack = ContentIdeationAgent(brand).run(pack, context)
            pack = CreativeProductionAgent(brand).run(pack, context)
        if cls is PosterProductionAgent:
            pack = BrandGuardianAgent(brand).run(pack, context)
            for creative in pack.creatives:
                creative.format = "poster"
        if cls in {SocialMediaAgent, PerformanceMarketingAgent, BusinessGrowthAgent, AnalyticsAgent}:
            if not pack.insights:
                pack = MarketAnalysisAgent(brand).run(pack, context)
            if not pack.trends:
                pack = TrendScoutAgent(brand).run(pack, context)
        agent = cls(brand)
        pack = agent.run(pack, context)
        agent_name = agent.name
    else:
        agent_name = "Orchestrator"
        pack = Orchestrator(brand).run_weekly_campaign(
            objective=objective,
            week_of=date.today().isoformat(),
            context=context,
        )

    write_outputs(pack, session_dir)
    reply = _pack_reply(pack, agent_name=agent_name, intent=intent, focus=focus)
    if attachment_summary["notes"]:
        reply += "\n\n**Using your uploads**\n" + "\n".join(f"- {n}" for n in attachment_summary["notes"])

    snippet = session_dir / "latest_reply.md"
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
        "agent": agent_name,
        "reply": reply,
        "files": files,
        "intent": intent,
        "mode": mode,
        "focus": {
            "products": focus.get("product_names", []),
            "categories": focus.get("categories", []),
            "formats": focus.get("formats", []),
        },
        "pack": {
            "week_of": pack.week_of,
            "approved": pack.approved,
            "ideas": len(pack.ideas),
            "creatives": len(pack.creatives),
            "posters": len(pack.posters),
        },
    }
