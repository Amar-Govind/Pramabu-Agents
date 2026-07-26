from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.llm import complete_json
from pramabu_agents.models import AgentRole, CampaignPack


class MarketplaceAgent(BaseAgent):
    role = AgentRole.MARKETPLACE
    name = "Marketplace"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        n = int(context.get("marketplace_actions", 5))
        products = self.brand.get("products", [])
        hero = [p.get("name") for p in products[:4] if p.get("name")]
        fallback = {
            "actions": [
                f"Refresh Amazon/Flipkart titles for {', '.join(hero[:2]) or 'hero SKUs'} with benefit-first keywords.",
                "Align marketplace images with D2C PDP photography (rose-gold accent, natural texture).",
                "Add A+ content / brand story modules highlighting handcrafted organic process.",
                "Sync pricing and stock status daily between WooCommerce and marketplace listings.",
                "Seed early reviews on marketplace listings for Virgin Coconut Oil and Neem Soap.",
                "Create festival bundles exclusive to Amazon for Discovery + D2C retargeting.",
                "Monitor competitor organic soap listings weekly for pricing/claim gaps.",
            ]
        }
        result = complete_json(
            system=(
                "You are a marketplace listing strategist for organic FMCG in India. "
                "Return JSON with actions (array of strings)."
            ),
            user=(
                f"Brand={self.brand_name}. Website={self.website}. Objective={pack.objective}. "
                f"Products={hero}. Suggest {n} marketplace listing / Amazon-Flipkart actions."
            ),
            fallback=fallback,
        )
        pack.marketplace_actions = list(result.get("actions", fallback["actions"]))[:n]
        pack.agent_trace.append(
            self.trace("Planned marketplace actions", {"count": len(pack.marketplace_actions)})
        )
        return pack
