from __future__ import annotations

import re
from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.models import AgentRole, CampaignPack


class BrandGuardianAgent(BaseAgent):
    role = AgentRole.BRAND_GUARDIAN
    name = "Brand Guardian"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        forbidden = [
            c.lower()
            for c in self.brand.get("brand", {}).get("compliance", {}).get("forbidden_claims", [])
        ]
        flags: list[str] = []

        texts: list[str] = []
        for idea in pack.ideas:
            texts.extend([idea.title, idea.hook, idea.cta, idea.angle])
        for creative in pack.creatives:
            texts.extend([creative.headline, creative.body, " ".join(creative.script_beats)])
            for claim in forbidden:
                blob = f"{creative.headline} {creative.body}".lower()
                if claim and claim in blob:
                    creative.brand_safe = False
                    creative.notes.append(f"Contains forbidden claim language: '{claim}'")
                    flags.append(f"Creative '{creative.idea_title}' may violate claim policy: {claim}")

        for text in texts:
            lower = text.lower()
            for claim in forbidden:
                if claim and claim in lower and f"forbidden:{claim}:{text}" not in flags:
                    flags.append(f"Potential forbidden claim '{claim}' in: {text}")

            # Soft checks for overclaim patterns
            if re.search(r"\b(guaranteed|miracle|instant cure)\b", lower):
                flags.append(f"Overclaim risk in: {text}")

        pack.qa_flags.extend(flags)
        pack.agent_trace.append(
            self.trace(
                "Reviewed brand voice and claims",
                {"flags": len(flags), "creatives_checked": len(pack.creatives)},
            )
        )
        return pack
