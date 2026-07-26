from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.llm import complete_json
from pramabu_agents.models import AgentRole, CampaignPack


class CrisisPRAgent(BaseAgent):
    role = AgentRole.CRISIS_PR
    name = "Crisis & PR"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        n = int(context.get("crisis_actions", 4))
        forbidden = self.brand.get("compliance", {}).get("forbidden_claims", [])
        fallback = {
            "plan": [
                "Maintain a brand-safe response kit for quality, delivery delay, and claim complaints.",
                "Never use medical/cure language in replies; escalate product safety issues to founders.",
                "Monitor comments on paid + organic posts daily for misinformation about 'organic' claims.",
                "Prepare a transparent FAQ on ingredients, shelf life, and handcrafted process.",
                "If a batch issue arises: pause ads for that SKU, notify buyers, offer replacement.",
                "Keep PR talking points ready: heritage care, honest labeling, South Indian botanicals.",
            ]
        }
        result = complete_json(
            system=(
                "You are a crisis / PR steward for an organic personal-care brand. "
                "Return JSON with plan (array of strings). Avoid medical claims."
            ),
            user=(
                f"Brand={self.brand_name}. Forbidden claims={forbidden}. Objective={pack.objective}. "
                f"Suggest {n} crisis-readiness and PR actions for this week."
            ),
            fallback=fallback,
        )
        pack.crisis_pr_plan = list(result.get("plan", fallback["plan"]))[:n]
        pack.agent_trace.append(
            self.trace("Prepared crisis / PR plan", {"count": len(pack.crisis_pr_plan)})
        )
        return pack
