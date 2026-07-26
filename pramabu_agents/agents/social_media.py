from __future__ import annotations

from typing import Any

from pramabu_agents.agents.base import BaseAgent
from pramabu_agents.models import AgentRole, CampaignPack, SocialPostPlan

DAY_PLAN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
BEST_TIMES = {
    "instagram": "19:30",
    "facebook": "13:00",
    "youtube_shorts": "18:00",
}


class SocialMediaAgent(BaseAgent):
    role = AgentRole.SOCIAL_MEDIA
    name = "Social Media Manager"

    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        calendar: list[SocialPostPlan] = []
        for idx, creative in enumerate(pack.creatives[:7]):
            platform = (
                pack.ideas[idx].platforms[0]
                if idx < len(pack.ideas) and pack.ideas[idx].platforms
                else "instagram"
            )
            hashtags = " ".join(f"#{h.lstrip('#')}" for h in creative.hashtags[:5])
            caption = f"{creative.headline}\n\n{creative.body}\n\n{hashtags}".strip()
            calendar.append(
                SocialPostPlan(
                    platform=platform,
                    day=DAY_PLAN[idx % 7],
                    format=creative.format,
                    caption=caption,
                    creative_ref=creative.idea_title,
                    best_time_local=BEST_TIMES.get(platform, "19:00"),
                )
            )

        pack.social_calendar = calendar
        pack.agent_trace.append(self.trace("Built weekly social calendar", {"posts": len(calendar)}))
        return pack
