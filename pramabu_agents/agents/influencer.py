from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.llm import complete_json
from pramabu_agents.models import AgentRole, CampaignPack


class InfluencerAgent(BaseAgent):
    role = AgentRole.INFLUENCER
    name = "Influencer"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        n = int(context.get("influencer_actions", 5))
        fallback = {
            "plan": [
                "Brief 8 micro-creators (5k–50k) in Tamil Nadu / Kerala for soap first-use UGC.",
                "Seed Virgin Coconut Oil morning ritual Reels with 3 haircare creators.",
                "Partner with terrace-garden creators for coco pith before/after series.",
                "Offer product-only gifting for nano creators; paid boost only for top performers.",
                "Require brand-safe claims checklist in every creator brief (no medical claims).",
                "Repurpose best UGC into Meta ads and PDP review gallery on parambu.in.",
                "Track creator codes for 14-day attributed sales and content save rate.",
            ]
        }
        result = complete_json(
            system=(
                "You are an influencer / UGC strategist for an organic Indian D2C brand. "
                "Return JSON with plan (array of strings)."
            ),
            user=(
                f"Brand={self.brand_name}. Objective={pack.objective}. Trends={pack.trends[:5]}. "
                f"Suggest {n} influencer seeding and UGC actions for this week."
            ),
            fallback=fallback,
        )
        pack.influencer_plan = list(result.get("plan", fallback["plan"]))[:n]
        pack.agent_trace.append(
            self.trace("Built influencer / UGC plan", {"count": len(pack.influencer_plan)})
        )
        return pack
