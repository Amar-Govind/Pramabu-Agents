from __future__ import annotations

from pathlib import Path
from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.models import AgentRole, CampaignPack
from pramabu_agents.poster import render_poster, slugify


class PosterProductionAgent(BaseAgent):
    role = AgentRole.POSTER_PRODUCTION
    name = "Poster Production"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        output_root = Path(context.get("output_dir", "output"))
        poster_dir = output_root / "posters" / pack.week_of
        colors = list(self.brand.get("brand", {}).get("visual", {}).get("primary_colors", []))

        posters = []
        candidates = [
            c
            for c in pack.creatives
            if c.brand_safe and c.format.lower() in {"poster", "carousel"}
        ]

        # Always produce at least one poster sample when ideas include posters
        if not candidates:
            poster_ideas = [c for c in pack.creatives if c.brand_safe][:1]
            candidates = poster_ideas

        for index, creative in enumerate(candidates, start=1):
            filename = f"{index:02d}-{slugify(creative.idea_title)}.png"
            path = poster_dir / filename
            asset = render_poster(
                creative,
                brand_name=self.brand_name,
                website=self.website,
                colors=colors,
                output_path=path,
            )
            posters.append(asset)
            creative.notes = list(creative.notes) + [f"Poster rendered: {asset.path}"]

        pack.posters = posters
        pack.agent_trace.append(
            self.trace(
                "Rendered poster assets",
                {"count": len(posters), "dir": str(poster_dir)},
            )
        )
        return pack
