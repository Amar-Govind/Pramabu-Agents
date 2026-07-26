from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.models import AgentRole, CampaignPack


class EcommerceAgent(BaseAgent):
    role = AgentRole.ECOMMERCE
    name = "E-commerce Website"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        products = self.brand.get("products", [])
        actions = [
            "Audit PDP hero image contrast and first 80 characters of title for mobile.",
            "Add trust strip: delivery promise, secure payment, easy returns.",
            "Create homepage banner aligned to this week's lead creative.",
            "Ensure WhatsApp/support CTA is visible above the fold on mobile.",
        ]
        for product in products:
            name = product.get("name", "SKU")
            actions.append(
                f"Refresh {name} bullets to mirror campaign benefits: "
                + ", ".join(product.get("benefits", [])[:3])
            )
            channels = product.get("channels", [])
            if "amazon" in channels or "blinkit" in channels:
                actions.append(f"Sync marketplace listing keywords for {name} with campaign hooks.")

        if any(i.format == "poster" for i in pack.ideas):
            actions.append("Export poster creative variants for website promo strip and PDP gallery.")

        pack.ecommerce_actions = actions
        pack.agent_trace.append(self.trace("Planned e-commerce improvements", {"actions": len(actions)}))
        return pack
