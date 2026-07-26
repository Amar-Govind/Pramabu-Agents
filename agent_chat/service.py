from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path
from typing import Any

from agent_chat.assistant_local import local_chat_reply
from agent_chat.focus import extract_focus
from agent_chat.history import as_llm_messages, load_history, save_history
from agent_chat.knowledge import (
    attachment_chunks,
    dump_brand_snapshot,
    format_knowledge_block,
    retrieve_knowledge,
)
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
from pramabu_agents.llm import complete_chat
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
    rows.insert(
        0,
        {
            "name": "Parambu Assistant",
            "key": "assistant",
            "role": "Conversational assistant with brand knowledge + agent tools",
        },
    )
    return rows


def _match_agent(message: str):
    lowered = message.lower()
    for key, cls, _role in sorted(AGENT_CATALOG, key=lambda row: len(row[0]), reverse=True):
        if key in lowered:
            return key, cls
    for _key, cls, _role in AGENT_CATALOG:
        agent_name = cls(load_brand()).name.lower()
        if agent_name in lowered:
            return agent_name, cls
    return None, None


def _wants_tool(message: str) -> str | None:
    """Return tool intent when user asks to generate/run something actionable."""
    lowered = message.lower().strip()
    action_verbs = ("create", "make", "generate", "render", "design", "run", "build", "draft", "produce")
    has_action = any(v in lowered for v in action_verbs)

    if any(t in lowered for t in ("run all", "weekly campaign", "campaign pack", "full pipeline")):
        return "weekly"
    if "poster" in lowered and (has_action or "please" in lowered or lowered.endswith("poster") or "poster for" in lowered):
        return "posters"
    matched, _ = _match_agent(lowered)
    if matched and has_action:
        return "single_agent"
    # Explicit "use the crm agent" style
    if matched and any(t in lowered for t in ("use", "ask", "with", "via", "using")):
        return "single_agent"
    return None


def _collect_files(session_dir: Path, pack: CampaignPack | None) -> list[dict[str, str]]:
    files: list[dict[str, str]] = []
    if not pack:
        return files
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


def _run_tool(
    *,
    tool: str,
    message: str,
    brand: dict[str, Any],
    context: dict[str, Any],
    session_dir: Path,
) -> tuple[str, CampaignPack, str]:
    objective = message.strip()
    if tool == "posters":
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
        write_outputs(pack, session_dir)
        facts = [
            f"Generated {len(pack.posters)} poster file(s).",
            *[f"- {p.idea_title}: {p.headline}" for p in pack.posters[:6]],
        ]
        return agent_name, pack, "\n".join(facts)

    if tool == "single_agent":
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
        write_outputs(pack, session_dir)
        # Collect the most relevant list field
        payload = {
            "CRM": pack.crm_actions,
            "Influencer": pack.influencer_plan,
            "Marketplace": pack.marketplace_actions,
            "Supply Chain": pack.supply_chain_actions,
            "Crisis & PR": pack.crisis_pr_plan,
            "Localization": pack.localization_plan,
            "Business Growth": pack.growth_opportunities,
            "Performance Marketing": pack.ad_plan,
            "E-commerce Website": pack.ecommerce_actions,
            "Analytics & BI": pack.analytics_plan,
            "Trend Scout": pack.trends,
            "Market Analysis": pack.insights,
            "Content Ideation": [f"{i.title} ({i.format}) — {i.hook}" for i in pack.ideas],
            "Creative Production": [f"{c.idea_title}: {c.headline}" for c in pack.creatives],
            "Social Media Manager": [
                f"{p.day} | {p.platform} | {p.format} — {p.creative_ref}" for p in pack.social_calendar
            ],
            "Brand Guardian": pack.qa_flags or ["No brand flags."],
            "QA": pack.qa_flags or ["No blockers."],
            "Poster Production": [f"{p.idea_title}: {p.headline}" for p in pack.posters],
        }.get(agent.name, [])
        facts = [f"{agent.name} completed."] + [f"- {item}" for item in payload[:8]]
        return agent.name, pack, "\n".join(facts)

    # weekly
    pack = Orchestrator(brand).run_weekly_campaign(
        objective=objective,
        week_of=date.today().isoformat(),
        context=context,
    )
    write_outputs(pack, session_dir)
    facts = [
        f"Weekly campaign ready for {pack.week_of}.",
        f"Ideas: {len(pack.ideas)}, creatives: {len(pack.creatives)}, posters: {len(pack.posters)}.",
        *[f"- {i.title} ({i.format}) — {i.hook}" for i in pack.ideas[:5]],
    ]
    return "Orchestrator", pack, "\n".join(facts)


def _system_prompt(knowledge: str) -> str:
    return f"""You are Parambu Assistant — a helpful, conversational AI for Parambu Organics.
You chat like a thoughtful teammate in a chat window (similar to ChatGPT/Cursor): clear, natural, concise, and useful.

Always ground answers in the knowledge base and any uploaded documents below.
Never invent medical cures or forbidden claims (no "clinically proven", "cures", "treats disease", etc.).
Brand voice: warm, heritage-rooted, trustworthy, practical.

If tool results are provided, explain them in natural language and mention that downloadable files are attached in the chat.
If the user is just asking a question, answer directly — do not dump a campaign pack unless they asked to generate one.

KNOWLEDGE BASE:
{knowledge}

BRAND SNAPSHOT:
{dump_brand_snapshot()[:6000]}
"""


def run_chat_turn(
    *,
    message: str,
    session_dir: Path,
    attachment_paths: list[Path],
) -> dict[str, Any]:
    from agent_chat.attachments import summarize_attachments

    brand = load_brand()
    history = load_history(session_dir)
    attachment_summary = summarize_attachments(attachment_paths)
    focus = extract_focus(message, brand)
    tool = _wants_tool(message)

    extra = attachment_chunks(attachment_summary)
    chunks = retrieve_knowledge(message, extra_chunks=extra, brand=brand, limit=8)
    knowledge = format_knowledge_block(chunks)

    context = {
        "output_dir": str(session_dir),
        "content_pieces": 5,
        "growth_ideas": 4,
        "uploaded_images": attachment_summary["images"],
        "uploaded_documents": [d["name"] for d in attachment_summary["documents"]],
        "focus": focus,
        "user_message": message,
    }

    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "inputs").mkdir(parents=True, exist_ok=True)

    pack: CampaignPack | None = None
    agent_name = "Parambu Assistant"
    tool_facts = None
    intent = "chat"

    if tool:
        intent = tool
        agent_name, pack, tool_facts = _run_tool(
            tool=tool,
            message=message,
            brand=brand,
            context=context,
            session_dir=session_dir,
        )

    user_content = message
    if attachment_summary.get("notes"):
        user_content += "\n\n[Uploads]\n" + "\n".join(f"- {n}" for n in attachment_summary["notes"])
    if tool_facts:
        user_content += (
            "\n\n[Internal tool results — rewrite these as a natural chat reply for the user]\n"
            + tool_facts
        )

    llm_messages = as_llm_messages(history) + [{"role": "user", "content": user_content}]
    fallback = local_chat_reply(
        message=message,
        history=history,
        knowledge=knowledge,
        tool_facts=tool_facts,
        agent_name=agent_name,
    )
    reply, llm_meta = complete_chat(
        system=_system_prompt(knowledge),
        messages=llm_messages,
        fallback=fallback,
        temperature=0.55,
    )
    mode = "LLM" if llm_meta.get("ok") else "knowledge"

    # Persist conversation
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply, "agent": agent_name})
    save_history(session_dir, history)

    files = _collect_files(session_dir, pack)
    if pack:
        snippet = session_dir / "latest_reply.md"
        snippet.write_text(reply + "\n\n---\n\n" + pack_to_markdown(pack), encoding="utf-8")
        files.append(
            {
                "name": "latest_reply.md",
                "path": str(snippet),
                "kind": "report",
                "url": f"/api/files/{session_dir.name}/latest_reply.md",
            }
        )

    return {
        "agent": agent_name if tool else "Parambu Assistant",
        "reply": reply,
        "files": files,
        "intent": intent,
        "mode": mode,
        "llm": llm_meta,
        "focus": {
            "products": focus.get("product_names", []),
            "categories": focus.get("categories", []),
            "formats": focus.get("formats", []),
        },
        "pack": None
        if not pack
        else {
            "week_of": pack.week_of,
            "approved": pack.approved,
            "ideas": len(pack.ideas),
            "creatives": len(pack.creatives),
            "posters": len(pack.posters),
        },
    }
