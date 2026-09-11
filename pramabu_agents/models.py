from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    BRAND_GUARDIAN = "brand_guardian"
    TREND_SCOUT = "trend_scout"
    MARKET_ANALYSIS = "market_analysis"
    CONTENT_IDEATION = "content_ideation"
    CREATIVE_PRODUCTION = "creative_production"
    POSTER_PRODUCTION = "poster_production"
    SOCIAL_MEDIA = "social_media"
    ECOMMERCE = "ecommerce"
    PERFORMANCE_MARKETING = "performance_marketing"
    BUSINESS_GROWTH = "business_growth"
    MARKETPLACE = "marketplace"
    INFLUENCER = "influencer"
    CRM = "crm"
    SUPPLY_CHAIN = "supply_chain"
    CRISIS_PR = "crisis_pr"
    LOCALIZATION = "localization"
    ANALYTICS = "analytics"
    QA = "qa"


class AgentMessage(BaseModel):
    role: AgentRole
    content: str
    data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContentIdea(BaseModel):
    title: str
    format: str  # poster | reel | short | carousel
    hook: str
    angle: str
    cta: str
    platforms: list[str]
    trend_tags: list[str] = Field(default_factory=list)
    priority: int = 3


class CreativeBrief(BaseModel):
    idea_title: str
    format: str
    headline: str
    body: str
    visual_direction: str
    script_beats: list[str] = Field(default_factory=list)
    hashtags: list[str] = Field(default_factory=list)
    brand_safe: bool = True
    notes: list[str] = Field(default_factory=list)


class SocialPostPlan(BaseModel):
    platform: str
    day: str
    format: str
    caption: str
    creative_ref: str
    best_time_local: str


class PosterAsset(BaseModel):
    idea_title: str
    headline: str
    path: str
    width: int = 1080
    height: int = 1350
    format: str = "poster"


class CampaignPack(BaseModel):
    brand: str
    week_of: str
    objective: str
    insights: list[str] = Field(default_factory=list)
    trends: list[str] = Field(default_factory=list)
    ideas: list[ContentIdea] = Field(default_factory=list)
    creatives: list[CreativeBrief] = Field(default_factory=list)
    posters: list[PosterAsset] = Field(default_factory=list)
    social_calendar: list[SocialPostPlan] = Field(default_factory=list)
    ecommerce_actions: list[str] = Field(default_factory=list)
    ad_plan: list[str] = Field(default_factory=list)
    growth_opportunities: list[str] = Field(default_factory=list)
    marketplace_actions: list[str] = Field(default_factory=list)
    influencer_plan: list[str] = Field(default_factory=list)
    crm_actions: list[str] = Field(default_factory=list)
    supply_chain_actions: list[str] = Field(default_factory=list)
    crisis_pr_plan: list[str] = Field(default_factory=list)
    localization_plan: list[str] = Field(default_factory=list)
    analytics_plan: list[str] = Field(default_factory=list)
    qa_flags: list[str] = Field(default_factory=list)
    approved: bool = False
    agent_trace: list[AgentMessage] = Field(default_factory=list)
