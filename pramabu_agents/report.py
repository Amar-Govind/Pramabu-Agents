from __future__ import annotations

import json
from pathlib import Path

from pramabu_agents.models import CampaignPack


def pack_to_markdown(pack: CampaignPack) -> str:
    lines = [
        f"# {pack.brand} Weekly Campaign Pack",
        "",
        f"**Week of:** {pack.week_of}  ",
        f"**Objective:** {pack.objective}  ",
        f"**Approved:** {'yes' if pack.approved else 'no (needs review)'}  ",
        "",
        "## Market Insights",
    ]
    lines.extend(f"- {item}" for item in pack.insights or ["_None_"])

    lines.extend(["", "## Trends"])
    lines.extend(f"- {item}" for item in pack.trends or ["_None_"])

    lines.extend(["", "## Content Ideas"])
    for idea in pack.ideas:
        lines.append(
            f"- **{idea.title}** ({idea.format}, P{idea.priority}) — hook: _{idea.hook}_ → CTA: {idea.cta}"
        )

    lines.extend(["", "## Creative Briefs"])
    for creative in pack.creatives:
        lines.extend(
            [
                f"### {creative.idea_title}",
                f"- Format: {creative.format}",
                f"- Headline: {creative.headline}",
                f"- Body: {creative.body}",
                f"- Visual: {creative.visual_direction}",
                f"- Brand safe: {creative.brand_safe}",
            ]
        )
        if creative.script_beats:
            lines.append("- Script beats:")
            lines.extend(f"  - {beat}" for beat in creative.script_beats)
        if creative.hashtags:
            lines.append("- Hashtags: " + " ".join(creative.hashtags))
        if creative.notes:
            lines.append("- Notes: " + "; ".join(creative.notes))
        lines.append("")

    lines.extend(["", "## Poster Assets"])
    if pack.posters:
        for poster in pack.posters:
            lines.append(
                f"- **{poster.idea_title}** — `{poster.path}` ({poster.width}x{poster.height})"
            )
    else:
        lines.append("- _None_")

    lines.extend(["", "## Social Calendar"])
    for post in pack.social_calendar:
        lines.append(
            f"- **{post.day}** | {post.platform} | {post.format} @ {post.best_time_local} — {post.creative_ref}"
        )

    lines.extend(["", "## E-commerce Actions"])
    lines.extend(f"- {item}" for item in pack.ecommerce_actions or ["_None_"])

    lines.extend(["", "## Ad Plan"])
    lines.extend(f"- {item}" for item in pack.ad_plan or ["_None_"])

    lines.extend(["", "## Growth Opportunities"])
    lines.extend(f"- {item}" for item in pack.growth_opportunities or ["_None_"])

    lines.extend(["", "## Marketplace Actions"])
    lines.extend(f"- {item}" for item in pack.marketplace_actions or ["_None_"])

    lines.extend(["", "## Influencer / UGC Plan"])
    lines.extend(f"- {item}" for item in pack.influencer_plan or ["_None_"])

    lines.extend(["", "## CRM Actions"])
    lines.extend(f"- {item}" for item in pack.crm_actions or ["_None_"])

    lines.extend(["", "## Supply Chain"])
    lines.extend(f"- {item}" for item in pack.supply_chain_actions or ["_None_"])

    lines.extend(["", "## Crisis & PR"])
    lines.extend(f"- {item}" for item in pack.crisis_pr_plan or ["_None_"])

    lines.extend(["", "## Localization"])
    lines.extend(f"- {item}" for item in pack.localization_plan or ["_None_"])

    lines.extend(["", "## Analytics Plan"])
    lines.extend(f"- {item}" for item in pack.analytics_plan or ["_None_"])

    lines.extend(["", "## QA Flags"])
    if pack.qa_flags:
        lines.extend(f"- {item}" for item in pack.qa_flags)
    else:
        lines.append("- None")

    lines.extend(["", "## Agent Trace"])
    for msg in pack.agent_trace:
        lines.append(f"- `{msg.role.value}`: {msg.content}")

    lines.append("")
    return "\n".join(lines)


def write_outputs(pack: CampaignPack, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"campaign_{pack.week_of}.json"
    md_path = output_dir / f"campaign_{pack.week_of}.md"
    posters_dir = output_dir / "posters" / pack.week_of

    json_path.write_text(pack.model_dump_json(indent=2), encoding="utf-8")
    md_path.write_text(pack_to_markdown(pack), encoding="utf-8")
    result = {"json": json_path, "markdown": md_path}
    if pack.posters or posters_dir.exists():
        result["posters"] = posters_dir
    return result


def load_pack(path: Path) -> CampaignPack:
    data = json.loads(path.read_text(encoding="utf-8"))
    return CampaignPack.model_validate(data)
