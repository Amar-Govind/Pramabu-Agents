from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.llm import complete_json
from pramabu_agents.models import AgentRole, CampaignPack, CreativeBrief


class CreativeProductionAgent(BaseAgent):
    role = AgentRole.CREATIVE_PRODUCTION
    name = "Creative Production"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        visual = self.brand.get("brand", {}).get("visual", {})
        style = visual.get("style", "clean product-first photography")
        colors = ", ".join(visual.get("primary_colors", []))

        creatives: list[CreativeBrief] = []
        for idea in pack.ideas[:6]:
            fallback = {
                "headline": idea.hook,
                "body": f"{idea.angle}. Built for everyday homes with {self.brand_name}.",
                "visual_direction": f"{style}. Colors: {colors}. Product hero center frame.",
                "script_beats": [
                    "0-2s: bold hook on screen",
                    "2-6s: product in real use",
                    "6-10s: benefit proof",
                    "10-12s: CTA + brand lockup",
                ]
                if idea.format in {"reel", "short"}
                else [],
                "hashtags": [f"#{self.brand_name}", "#EverydayFresh", "#HomeCare"],
            }
            result = complete_json(
                system=(
                    "You are a creative director for FMCG. Return JSON with headline, body, "
                    "visual_direction, script_beats (array), hashtags (array)."
                ),
                user=f"Turn this idea into a production brief: {idea.model_dump()}",
                fallback=fallback,
            )
            creatives.append(
                CreativeBrief(
                    idea_title=idea.title,
                    format=idea.format,
                    headline=result.get("headline", fallback["headline"]),
                    body=result.get("body", fallback["body"]),
                    visual_direction=result.get("visual_direction", fallback["visual_direction"]),
                    script_beats=list(result.get("script_beats", fallback["script_beats"])),
                    hashtags=list(result.get("hashtags", fallback["hashtags"])),
                )
            )

        pack.creatives = creatives
        pack.agent_trace.append(self.trace("Produced creative briefs", {"count": len(creatives)}))
        return pack
