from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.llm import complete_json
from pramabu_agents.models import AgentRole, CampaignPack, ContentIdea


class ContentIdeationAgent(BaseAgent):
    role = AgentRole.CONTENT_IDEATION
    name = "Content Ideation"

    def _pick_products(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        products = list(self.brand.get("products", []))
        focus = context.get("focus") or {}
        focused = list(focus.get("products") or [])
        if focused:
            # Keep focused products first, then fill with others
            focused_names = {p.get("name") for p in focused}
            rest = [p for p in products if p.get("name") not in focused_names]
            return focused + rest
        return products

    def _seed_ideas(
        self,
        *,
        products: list[dict[str, Any]],
        channels: list[str],
        site: str,
        focus: dict[str, Any],
        n: int,
    ) -> list[ContentIdea]:
        preferred_formats = focus.get("formats") or []
        names = [p.get("name") for p in products if p.get("name")]
        primary = names[0] if names else self.brand_name
        secondary = names[1] if len(names) > 1 else primary
        tertiary = names[2] if len(names) > 2 else secondary

        def fmt(default: str) -> str:
            return preferred_formats[0] if preferred_formats else default

        ideas = [
            ContentIdea(
                title=f"{primary}: hero spotlight",
                format=fmt("poster"),
                hook=f"Meet {primary} — pure heritage care",
                angle=f"Product-first story for {primary}",
                cta=f"Shop {primary} at {site}",
                platforms=channels[:2] or ["instagram"],
                trend_tags=["hero", "product"],
                priority=1,
            ),
            ContentIdea(
                title=f"{primary}: everyday ritual reel",
                format=fmt("reel"),
                hook=f"One simple ritual with {primary}",
                angle="Daily use moment + benefit",
                cta="Shop the ritual",
                platforms=["instagram", "youtube_shorts"],
                trend_tags=["ritual", "self-care"],
                priority=1,
            ),
            ContentIdea(
                title=f"{secondary}: why customers switch",
                format=fmt("carousel"),
                hook=f"Why families choose {secondary}",
                angle="Trust + ingredient honesty",
                cta=f"Explore on {site}",
                platforms=["instagram"],
                trend_tags=["trust", "ugc"],
                priority=2,
            ),
            ContentIdea(
                title=f"{tertiary}: before & after proof",
                format=fmt("short"),
                hook=f"See the {tertiary} difference",
                angle="Proof-led short form",
                cta="Try it this week",
                platforms=["youtube_shorts", "instagram"],
                trend_tags=["before-after", "proof"],
                priority=2,
            ),
            ContentIdea(
                title=f"Bundle: {primary} + {secondary}",
                format=fmt("poster"),
                hook="Build your Parambu shelf",
                angle="Cross-sell / AOV bundle",
                cta="Shop the duo",
                platforms=["instagram", "facebook"],
                trend_tags=["bundle", "offer"],
                priority=3,
            ),
            ContentIdea(
                title=f"{primary}: myth vs truth",
                format=fmt("reel"),
                hook="Organic claims, explained simply",
                angle="Education without medical claims",
                cta="Choose pure & natural",
                platforms=["instagram"],
                trend_tags=["education", "myth-busting"],
                priority=3,
            ),
            ContentIdea(
                title=f"{secondary}: festival / seasonal care",
                format=fmt("poster"),
                hook="Seasonal glow, heritage roots",
                angle="Timely seasonal creative",
                cta=f"Shop now at {site}",
                platforms=["instagram", "facebook"],
                trend_tags=["seasonal", "festival"],
                priority=3,
            ),
        ]

        # If user asked only for posters, bias formats
        if preferred_formats == ["poster"]:
            for idea in ideas:
                idea.format = "poster"
        return ideas[:n]

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        n = int(context.get("content_pieces", self.brand.get("weekly_defaults", {}).get("content_pieces", 7)))
        focus = context.get("focus") or {}
        products = self._pick_products(context)
        channels = self.brand.get("channels", {}).get("social", ["instagram", "youtube_shorts"])
        site = self.website

        seed_ideas = self._seed_ideas(
            products=products,
            channels=channels,
            site=site,
            focus=focus,
            n=n,
        )
        focus_names = ", ".join(focus.get("product_names") or [p.get("name", "") for p in products[:3]])

        fallback = {"ideas": [i.model_dump() for i in seed_ideas]}
        result = complete_json(
            system=(
                "You create FMCG/organic brand content ideas for Parambu Organics. "
                "Return JSON: {ideas:[{title,format,hook,angle,cta,platforms,trend_tags,priority}]} "
                "Formats: poster|reel|short|carousel. Priority 1 is highest. "
                f"Website CTA should prefer {site}. Focus products must lead the ideas."
            ),
            user=(
                f"Brand={self.brand_name}. Website={site}. Objective={pack.objective}. "
                f"Focus products={focus_names}. Focus formats={focus.get('formats')}. "
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
            ideas = seed_ideas

        pack.ideas = sorted(ideas, key=lambda x: x.priority)
        pack.agent_trace.append(
            self.trace(
                "Generated content ideas",
                {"count": len(pack.ideas), "focus": focus.get("product_names", [])},
            )
        )
        return pack
