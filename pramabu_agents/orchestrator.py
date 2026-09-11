from __future__ import annotations

from datetime import date
from typing import Any

from pramabu_agents.agents import (
    AnalyticsAgent,
    BrandGuardianAgent,
    BusinessGrowthAgent,
    ContentIdeationAgent,
    CreativeProductionAgent,
    CrisisPRAgent,
    CRMAgent,
    EcommerceAgent,
    InfluencerAgent,
    LocalizationAgent,
    MarketAnalysisAgent,
    MarketplaceAgent,
    PerformanceMarketingAgent,
    PosterProductionAgent,
    QAAgent,
    SocialMediaAgent,
    SupplyChainAgent,
    TrendScoutAgent,
)
from pramabu_agents.models import AgentMessage, AgentRole, CampaignPack


class Orchestrator:
    """Runs the weekly FMCG campaign pipeline across specialist agents."""

    def __init__(self, brand: dict[str, Any]):
        self.brand = brand
        self.pipeline = [
            TrendScoutAgent(brand),
            MarketAnalysisAgent(brand),
            ContentIdeationAgent(brand),
            CreativeProductionAgent(brand),
            BrandGuardianAgent(brand),
            PosterProductionAgent(brand),
            SocialMediaAgent(brand),
            EcommerceAgent(brand),
            PerformanceMarketingAgent(brand),
            BusinessGrowthAgent(brand),
            MarketplaceAgent(brand),
            InfluencerAgent(brand),
            CRMAgent(brand),
            SupplyChainAgent(brand),
            CrisisPRAgent(brand),
            LocalizationAgent(brand),
            AnalyticsAgent(brand),
            QAAgent(brand),
        ]

    def run_weekly_campaign(
        self,
        objective: str | None = None,
        week_of: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> CampaignPack:
        brand_name = self.brand.get("brand", {}).get("name", "Parambu Organics")
        goals = self.brand.get("goals", {}).get("primary", [])
        pack = CampaignPack(
            brand=brand_name,
            week_of=week_of or date.today().isoformat(),
            objective=objective or (goals[0] if goals else "Grow brand demand and sales"),
            agent_trace=[
                AgentMessage(
                    role=AgentRole.ORCHESTRATOR,
                    content="Starting weekly campaign pipeline",
                    data={"agents": [a.name for a in self.pipeline]},
                )
            ],
        )

        ctx = {
            **self.brand.get("weekly_defaults", {}),
            **(context or {}),
        }

        for agent in self.pipeline:
            pack = agent.run(pack, ctx)
            pack.agent_trace.append(
                AgentMessage(
                    role=AgentRole.ORCHESTRATOR,
                    content=f"Completed step: {agent.name}",
                )
            )

        pack.agent_trace.append(
            AgentMessage(
                role=AgentRole.ORCHESTRATOR,
                content="Pipeline finished",
                data={"approved": pack.approved, "ideas": len(pack.ideas)},
            )
        )
        return pack
