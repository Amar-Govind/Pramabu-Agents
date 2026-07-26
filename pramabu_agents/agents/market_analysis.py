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
        fallback = {
            "insights": [
                f"{self.brand_name} can win on everyday value + freshness vs premium-only competitors.",
                "Quick-commerce discovery is rising; product thumbnails and first 3 words matter.",
                "Short-form video that shows real product use outperforms generic lifestyle posts.",
                "Bundles and refill/value packs improve basket size without heavy discounting.",
                f"Focus messaging on practical benefits for {product_names}.",
            ]
        }
        result = complete_json(
            system="You are an FMCG market analyst. Return JSON with insights (array of strings).",
            user=(
                f"Brand={self.brand_name}. Products={product_names}. "
                f"Objective={pack.objective}. Provide actionable market insights for this week."
            ),
            fallback=fallback,
        )
        pack.insights = list(result.get("insights", fallback["insights"]))[:7]
        pack.agent_trace.append(self.trace("Completed market analysis", {"insights": len(pack.insights)}))
        return pack
