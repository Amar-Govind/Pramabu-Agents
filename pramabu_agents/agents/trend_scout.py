from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.llm import complete_json
from pramabu_agents.models import AgentRole, CampaignPack


class TrendScoutAgent(BaseAgent):
    role = AgentRole.TREND_SCOUT
    name = "Trend Scout"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        season = context.get("season", "general")
        fallback = {
            "trends": [
                "POV / day-in-the-life product usage",
                "Before-after stain/clean transformations",
                "Value-for-money pack comparisons",
                "Regional festival / monsoon / summer routines",
                "ASMR unboxing and first-use moments",
                "Myth-busting household cleaning tips",
            ]
        }
        result = complete_json(
            system="You are a social trend scout for an Indian FMCG brand. Return JSON with key trends (array of strings).",
            user=f"Brand={self.brand_name}. Season={season}. Find current short-form content trends useful for posters and Reels.",
            fallback=fallback,
        )
        pack.trends = list(result.get("trends", fallback["trends"]))[:8]
        pack.agent_trace.append(self.trace("Scouted current content trends", {"count": len(pack.trends)}))
        return pack
