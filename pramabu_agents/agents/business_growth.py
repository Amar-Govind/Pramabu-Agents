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
        site = self.website
        fallback = {
            "opportunities": [
                f"Launch a first-order soap sampler bundle on {site} for new D2C buyers.",
                "Create Oil + Soap and Gardening starter kits to raise average order value.",
                "Partner with 10 micro-creators in Tamil Nadu / Kerala for UGC seeding.",
                "Add WhatsApp reorder + abandoned-cart recovery for WooCommerce shoppers.",
                "Publish Tamil + English captions on top Reels to expand local reach.",
                "Improve SEO landing pages for 'organic soap', 'virgin coconut oil', and 'coco pith'.",
                "Collect review photos from terrace-garden customers for gardening PDP trust.",
            ]
        }
        result = complete_json(
            system="You are a growth strategist for organic D2C FMCG. Return JSON with opportunities (array of strings).",
            user=(
                f"Brand={self.brand_name}. Website={site}. Objective={pack.objective}. "
                f"Insights={pack.insights}. Suggest {n} practical growth opportunities."
            ),
            fallback=fallback,
        )
        pack.growth_opportunities = list(result.get("opportunities", fallback["opportunities"]))[:n]
        pack.agent_trace.append(
            self.trace("Identified growth opportunities", {"count": len(pack.growth_opportunities)})
        )
        return pack
