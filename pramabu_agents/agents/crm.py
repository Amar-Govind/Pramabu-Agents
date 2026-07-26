from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.llm import complete_json
from pramabu_agents.models import AgentRole, CampaignPack


class CRMAgent(BaseAgent):
    role = AgentRole.CRM
    name = "CRM"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        n = int(context.get("crm_actions", 5))
        site = self.website
        fallback = {
            "actions": [
                f"Send a welcome series for new {site} buyers: brand story → usage tips → reorder CTA.",
                "Trigger WhatsApp / SMS cart recovery at 1h and 24h for abandoned checkouts.",
                "Segment buyers into Oils / Soap / Gardening and send category tips weekly.",
                "Offer a second-purchase coupon (e.g. WELCOME50) to first-time buyers after delivery.",
                "Ask for photo reviews 7 days post-delivery for soap and coco pith customers.",
                "Win-back email for 60+ day lapsed buyers with a soap sampler bundle.",
                "Add VIP early-access list for festival drops and limited herbal bars.",
            ]
        }
        result = complete_json(
            system=(
                "You are a CRM / retention marketer for organic D2C FMCG. "
                "Return JSON with actions (array of strings)."
            ),
            user=(
                f"Brand={self.brand_name}. Website={site}. Objective={pack.objective}. "
                f"Suggest {n} CRM, lifecycle, and retention actions."
            ),
            fallback=fallback,
        )
        pack.crm_actions = list(result.get("actions", fallback["actions"]))[:n]
        pack.agent_trace.append(
            self.trace("Planned CRM lifecycle actions", {"count": len(pack.crm_actions)})
        )
        return pack
