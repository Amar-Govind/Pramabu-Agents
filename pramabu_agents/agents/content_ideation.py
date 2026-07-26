from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.llm import complete_json
from pramabu_agents.models import AgentRole, CampaignPack, ContentIdea


class ContentIdeationAgent(BaseAgent):
    role = AgentRole.CONTENT_IDEATION
    name = "Content Ideation"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        n = int(context.get("content_pieces", self.brand.get("weekly_defaults", {}).get("content_pieces", 7)))
        products = self.brand.get("products", [])
        hero = products[0]["name"] if products else self.brand_name
        channels = self.brand.get("channels", {}).get("social", ["instagram", "youtube_shorts"])

        seed_ideas = [
            ContentIdea(
                title=f"{hero}: 10-second stain rescue",
                format="reel",
                hook="Wait… this stain came out in one wash?",
                angle="Transformation proof",
                cta="Shop the value pack today",
                platforms=channels[:2],
                trend_tags=["before-after", "transformation"],
                priority=1,
            ),
            ContentIdea(
                title="Family morning routine poster",
                format="poster",
                hook="Fresh start. Real value.",
                angle="Everyday ritual branding",
                cta="Add to cart",
                platforms=["instagram", "facebook"],
                trend_tags=["routine", "family"],
                priority=2,
            ),
            ContentIdea(
                title="Myth vs fact: fragrance vs clean",
                format="carousel",
                hook="Smell ≠ clean. Here's the truth.",
                angle="Education + trust",
                cta="See what actually works",
                platforms=["instagram"],
                trend_tags=["myth-busting"],
                priority=2,
            ),
            ContentIdea(
                title="Quick commerce unboxing ASMR",
                format="short",
                hook="From doorstep to first wash",
                angle="Convenience + sensory",
                cta="Order in minutes",
                platforms=["youtube_shorts", "instagram"],
                trend_tags=["asmr", "unboxing"],
                priority=1,
            ),
            ContentIdea(
                title="Festival home-ready checklist",
                format="poster",
                hook="Guest-ready home in 3 steps",
                angle="Seasonal utility",
                cta="Get festival pack",
                platforms=["instagram", "facebook"],
                trend_tags=["seasonal", "checklist"],
                priority=3,
            ),
            ContentIdea(
                title="Value pack math for families",
                format="reel",
                hook="Same clean. Smarter spend.",
                angle="Price-value storytelling",
                cta="Compare packs",
                platforms=["instagram", "youtube_shorts"],
                trend_tags=["value", "comparison"],
                priority=1,
            ),
            ContentIdea(
                title="Customer tip of the week",
                format="reel",
                hook="A tip our customers swear by",
                angle="UGC-style social proof",
                cta="Try it and tell us",
                platforms=["instagram"],
                trend_tags=["ugc", "tips"],
                priority=3,
            ),
        ]

        fallback = {"ideas": [i.model_dump() for i in seed_ideas[:n]]}
        result = complete_json(
            system=(
                "You create FMCG content ideas. Return JSON: {ideas:[{title,format,hook,angle,cta,platforms,trend_tags,priority}]} "
                "Formats: poster|reel|short|carousel. Priority 1 is highest."
            ),
            user=(
                f"Brand={self.brand_name}. Objective={pack.objective}. "
                f"Trends={pack.trends}. Insights={pack.insights}. Generate {n} ideas."
            ),
            fallback=fallback,
        )

        ideas: list[ContentIdea] = []
        for raw in result.get("ideas", fallback["ideas"])[:n]:
            try:
                ideas.append(ContentIdea.model_validate(raw))
            except Exception:
                continue
        if not ideas:
            ideas = seed_ideas[:n]

        pack.ideas = sorted(ideas, key=lambda x: x.priority)
        pack.agent_trace.append(self.trace("Generated content ideas", {"count": len(pack.ideas)}))
        return pack
