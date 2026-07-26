from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.models import AgentRole, CampaignPack


class EcommerceAgent(BaseAgent):
    role = AgentRole.ECOMMERCE
    name = "E-commerce Website"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        products = self.brand.get("products", [])
        site = self.website
        actions = [
            f"Audit homepage hero on {site} against this week's lead creative and CTA.",
            "Keep Shop by category (Oils / Soap / Gardening) above the fold on mobile.",
            "Add trust strip: organic/handcrafted story, secure payment, easy support.",
            "Ensure WhatsApp/support and Login/Register flows remain friction-light.",
            "Review active discount badges for margin safety while keeping conversion.",
            "Improve product image consistency across soap, oil, and gardening PDPs.",
        ]
        for product in products[:6]:
            name = product.get("name", "SKU")
            url = product.get("url", site)
            benefits = ", ".join(product.get("benefits", [])[:3])
            actions.append(f"Refresh PDP bullets for {name} ({url}): {benefits}.")

        if any(i.format == "poster" for i in pack.ideas):
            actions.append(
                f"Export poster variants for {site} homepage promo strip and PDP gallery."
            )

        actions.append("Sync campaign hooks into WooCommerce short descriptions and meta titles.")
        pack.ecommerce_actions = actions
        pack.agent_trace.append(
            self.trace(
                f"Planned e-commerce improvements for {site}",
                {"actions": len(actions), "website": site},
            )
        )
        return pack
