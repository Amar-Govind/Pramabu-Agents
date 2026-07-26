from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.llm import complete_json
from pramabu_agents.models import AgentRole, CampaignPack


class MarketAnalysisAgent(BaseAgent):
    role = AgentRole.MARKET_ANALYSIS
    name = "Market Analysis"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        products = self.brand.get("products", [])
        product_names = ", ".join(p.get("name", "") for p in products) or "core SKUs"
        site = self.website
        fallback = {
            "insights": [
                f"{self.brand_name} can own 'pure heritage care' across soap, oil, and gardening.",
                f"D2C site {site} should lead with category clarity: Oils, Soap, Gardening.",
                "Short-form video of real product use (lather, oil ritual, plant growth) beats generic lifestyle posts.",
                "Bundles (soap sampler + VCO, or gardening starter pack) can lift average order value.",
                "Tamil Nadu / South India heritage ingredients (neem, vetpalai, nalangu maavu) are a differentiation moat.",
                f"Focus messaging on practical benefits for {product_names}.",
            ]
        }
        result = complete_json(
            system="You are an FMCG market analyst for organic D2C brands. Return JSON with insights (array of strings).",
            user=(
                f"Brand={self.brand_name}. Website={site}. Products={product_names}. "
                f"Objective={pack.objective}. Provide actionable market insights for this week."
            ),
            fallback=fallback,
        )
        pack.insights = list(result.get("insights", fallback["insights"]))[:7]
        pack.agent_trace.append(self.trace("Completed market analysis", {"insights": len(pack.insights)}))
        return pack
