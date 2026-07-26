from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pramabu_agents.models import AgentMessage, AgentRole, CampaignPack


class BaseAgent(ABC):
    role: AgentRole
    name: str

    def __init__(self, brand: dict[str, Any]):
        self.brand = brand

    @property
    def brand_name(self) -> str:
        return self.brand.get("brand", {}).get("name", "Pramabu")

    def trace(self, content: str, data: dict[str, Any] | None = None) -> AgentMessage:
        return AgentMessage(role=self.role, content=content, data=data or {})

    @abstractmethod
    def run(self, pack: CampaignPack, context: dict[str, Any]) -> CampaignPack:
        raise NotImplementedError
