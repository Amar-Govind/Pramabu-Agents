from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.llm import complete_json
from pramabu_agents.models import AgentRole, CampaignPack


class SupplyChainAgent(BaseAgent):
    role = AgentRole.SUPPLY_CHAIN
    name = "Supply Chain"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        n = int(context.get("supply_actions", 5))
        products = [p.get("name") for p in self.brand.get("products", [])[:6]]
        fallback = {
            "actions": [
                "Confirm cold-process soap curing buffer covers next 4 weeks of D2C + marketplace demand.",
                f"Prioritize replenishment for top movers: {', '.join(products[:3]) or 'hero SKUs'}.",
                "Flag low stock SKUs on WooCommerce before ad spend increases.",
                "Align gardening coco pith / chips bagging with monsoon demand spike.",
                "Verify packaging QC for rose-gold brand mark consistency on new batches.",
                "Prepare festival safety stock for Virgin Coconut Oil and Neem Soap.",
                "Track supplier lead times for neem, coconut oil, and cocopeat inputs weekly.",
            ]
        }
        result = complete_json(
            system=(
                "You are a supply-chain planner for a handcrafted organic FMCG brand. "
                "Return JSON with actions (array of strings)."
            ),
            user=(
                f"Brand={self.brand_name}. Objective={pack.objective}. Products={products}. "
                f"Suggest {n} inventory, QC, and fulfillment actions for this week."
            ),
            fallback=fallback,
        )
        pack.supply_chain_actions = list(result.get("actions", fallback["actions"]))[:n]
        pack.agent_trace.append(
            self.trace("Planned supply-chain actions", {"count": len(pack.supply_chain_actions)})
        )
        return pack
