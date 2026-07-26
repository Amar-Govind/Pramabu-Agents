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
        soap = next((p["name"] for p in products if p.get("category") == "Soap"), "Neem Soap")
        garden = next(
            (p["name"] for p in products if p.get("category") == "Gardening"), "Coco Pith (Low EC)"
        )
        channels = self.brand.get("channels", {}).get("social", ["instagram", "youtube_shorts"])
        site = self.website

        seed_ideas = [
            ContentIdea(
                title=f"{hero}: morning self-care ritual",
                format="reel",
                hook="One cold-pressed habit for everyday glow",
                angle="Oil as daily nourishment",
                cta=f"Shop now at {site}",
                platforms=channels[:2],
                trend_tags=["routine", "self-care"],
                priority=1,
            ),
            ContentIdea(
                title=f"{soap}: handcrafted clean poster",
                format="poster",
                hook="Pure heritage care for your skin",
                angle="Handcrafted organic soap story",
                cta="Shop soap essentials",
                platforms=["instagram", "facebook"],
                trend_tags=["heritage", "organic"],
                priority=1,
            ),
            ContentIdea(
                title="Soap finder: which bar for your skin?",
                format="carousel",
                hook="Neem, Rose, Charcoal, Vetpalai — pick yours",
                angle="Education + product discovery",
                cta=f"Explore soaps on {site}",
                platforms=["instagram"],
                trend_tags=["guide", "carousel"],
                priority=2,
            ),
            ContentIdea(
                title=f"{garden}: terrace garden transformation",
                format="short",
                hook="Same pot. Healthier roots.",
                angle="Gardening proof / moisture retention",
                cta="Shop gardening essentials",
                platforms=["youtube_shorts", "instagram"],
                trend_tags=["before-after", "gardening"],
                priority=1,
            ),
            ContentIdea(
                title="What's inside organic vs regular soap",
                format="reel",
                hook="Read the bar before you buy the bar",
                angle="Myth-busting / trust",
                cta="Choose pure & natural",
                platforms=["instagram", "youtube_shorts"],
                trend_tags=["myth-busting", "trust"],
                priority=2,
            ),
            ContentIdea(
                title="Family wellness shelf essentials",
                format="poster",
                hook="Oil + soap + garden — one natural home",
                angle="Cross-category bundle storytelling",
                cta="Build your Parambu shelf",
                platforms=["instagram", "facebook"],
                trend_tags=["bundle", "home"],
                priority=3,
            ),
            ContentIdea(
                title="Customer story: chemical-free switch",
                format="reel",
                hook="Why families are switching to Parambu",
                angle="UGC-style social proof",
                cta="Join the pure & natural routine",
                platforms=["instagram"],
                trend_tags=["ugc", "testimonial"],
                priority=3,
            ),
        ]

        fallback = {"ideas": [i.model_dump() for i in seed_ideas[:n]]}
        result = complete_json(
            system=(
                "You create FMCG/organic brand content ideas for Parambu Organics. "
                "Return JSON: {ideas:[{title,format,hook,angle,cta,platforms,trend_tags,priority}]} "
                "Formats: poster|reel|short|carousel. Priority 1 is highest. "
                f"Website CTA should prefer {site}."
            ),
            user=(
                f"Brand={self.brand_name}. Website={site}. Objective={pack.objective}. "
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
