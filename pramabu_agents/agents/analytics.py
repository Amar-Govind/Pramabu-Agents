from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.models import AgentRole, CampaignPack


class AnalyticsAgent(BaseAgent):
    role = AgentRole.ANALYTICS
    name = "Analytics & BI"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        kpis = self.brand.get("goals", {}).get("kpis", ["ROAS", "engagement_rate", "conversion_rate"])
        plan = [
            "Publish a Friday scorecard covering content, ads, and store conversion.",
            f"Primary KPIs this week: {', '.join(kpis)}.",
            "Tag each post/creative with a unique content_id for attribution.",
            "Compare organic vs paid CTR for the same creative concept.",
            "Flag any SKU with PDP bounce rate > 60% for creative/copy rewrite.",
            "Feed winning hooks back into next week's ideation brief.",
        ]
        pack.analytics_plan = plan
        pack.agent_trace.append(self.trace("Defined measurement plan", {"kpis": kpis}))
        return pack
