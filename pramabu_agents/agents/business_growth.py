from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.llm import complete_json
from pramabu_agents.models import AgentRole, CampaignPack


class BusinessGrowthAgent(BaseAgent):
    role = AgentRole.BUSINESS_GROWTH
    name = "Business Growth"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        n = int(context.get("growth_ideas", self.brand.get("weekly_defaults", {}).get("growth_ideas", 5)))
        fallback = {
            "opportunities": [
                "Launch a 2-SKU starter bundle for first-time D2C buyers.",
                "Add subscription/refill option with 5-8% loyalty incentive.",
                "Partner with 10 micro-creators in Tier-1/2 cities for UGC seeding.",
                "Create Blinkit/Zepto-specific creatives optimized for thumbnail readability.",
                "Run a win-back WhatsApp flow for customers inactive 45+ days.",
                "Test regional language captions (Hindi + one state language) on top posts.",
                "Introduce limited festive packaging sleeve without changing core SKU.",
            ]
        }
        result = complete_json(
            system="You are a growth strategist for FMCG. Return JSON with opportunities (array of strings).",
            user=(
                f"Brand={self.brand_name}. Objective={pack.objective}. "
                f"Insights={pack.insights}. Suggest {n} practical growth opportunities."
            ),
            fallback=fallback,
        )
        pack.growth_opportunities = list(result.get("opportunities", fallback["opportunities"]))[:n]
        pack.agent_trace.append(
            self.trace("Identified growth opportunities", {"count": len(pack.growth_opportunities)})
        )
        return pack
