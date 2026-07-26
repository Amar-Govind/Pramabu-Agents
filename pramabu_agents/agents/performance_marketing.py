from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.models import AgentRole, CampaignPack


class PerformanceMarketingAgent(BaseAgent):
    role = AgentRole.PERFORMANCE_MARKETING
    name = "Performance Marketing"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        budget = context.get("weekly_ad_budget_inr", 25000)
        top_ideas = [i.title for i in pack.ideas if i.priority == 1][:3]
        plan = [
            f"Allocate INR {budget:,} across Meta (60%) and Google (40%) this week.",
            "Create 1 prospecting campaign + 1 retargeting campaign on Meta.",
            "Use top 3 creatives as ad variants; kill underperformers after 48h if CTR < benchmark.",
            "Retarget site visitors and video viewers 50%+ with offer-led creative.",
            "Track UTMs: utm_source/platform, utm_campaign=weekly_pack, utm_content=creative_slug.",
        ]
        for title in top_ideas:
            plan.append(f"Prioritize ad spend on creative: {title}")

        pack.ad_plan = plan
        pack.agent_trace.append(self.trace("Drafted performance marketing plan", {"items": len(plan)}))
        return pack
