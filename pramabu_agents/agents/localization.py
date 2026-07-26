from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.llm import complete_json
from pramabu_agents.models import AgentRole, CampaignPack


class LocalizationAgent(BaseAgent):
    role = AgentRole.LOCALIZATION
    name = "Localization"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        n = int(context.get("localization_actions", 5))
        fallback = {
            "plan": [
                "Produce Tamil + English captions for top 3 Reels this week.",
                "Localize PDP bullets for Virgin Coconut Oil and Neem Soap into simple Tamil.",
                "Use South India festival / seasonal cues (without overclaiming) in posters.",
                "Keep CTAs bilingual on WhatsApp templates: Shop Now / இப்போதே வாங்குங்கள்.",
                "Prefer heritage ingredient names customers recognize: vetpalai, nalangu maavu, neem.",
                "Avoid forced slang; keep warm, trustworthy bilingual tone matching brand voice.",
                "Test Tamil-first creatives on Instagram for Coimbatore / Madurai / Chennai audiences.",
            ]
        }
        result = complete_json(
            system=(
                "You are a localization specialist for a Tamil Nadu rooted organic brand. "
                "Return JSON with plan (array of strings) for bilingual Tamil/English content."
            ),
            user=(
                f"Brand={self.brand_name}. Voice={self.brand.get('brand', {}).get('voice', {})}. "
                f"Objective={pack.objective}. Ideas={[i.title for i in pack.ideas[:4]]}. "
                f"Suggest {n} localization actions."
            ),
            fallback=fallback,
        )
        pack.localization_plan = list(result.get("plan", fallback["plan"]))[:n]
        pack.agent_trace.append(
            self.trace("Planned localization actions", {"count": len(pack.localization_plan)})
        )
        return pack
