from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.models import AgentRole, CampaignPack


class QAAgent(BaseAgent):
    role = AgentRole.QA
    name = "QA"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        flags = list(pack.qa_flags)

        if not pack.ideas:
            flags.append("No content ideas generated.")
        if not pack.creatives:
            flags.append("No creatives produced.")
        if not pack.social_calendar:
            flags.append("Social calendar is empty.")
        if len(pack.creatives) < min(3, len(pack.ideas)):
            flags.append("Fewer creatives than expected for the idea set.")

        unsafe = [c.idea_title for c in pack.creatives if not c.brand_safe]
        if unsafe:
            flags.append(f"Brand-unsafe creatives blocked from auto-approval: {', '.join(unsafe)}")

        # Deduplicate while preserving order
        seen: set[str] = set()
        deduped: list[str] = []
        for flag in flags:
            if flag not in seen:
                seen.add(flag)
                deduped.append(flag)
        pack.qa_flags = deduped

        # Auto-approve only when no hard blockers
        hard_blockers = [f for f in deduped if "forbidden" in f.lower() or "brand-unsafe" in f.lower() or "blocked" in f.lower()]
        pack.approved = len(hard_blockers) == 0 and bool(pack.creatives) and bool(pack.social_calendar)

        pack.agent_trace.append(
            self.trace(
                "Completed QA gate",
                {"approved": pack.approved, "flags": len(pack.qa_flags)},
            )
        )
        return pack
