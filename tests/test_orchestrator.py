from pathlib import Path

from pramabu_agents.agents.brand_guardian import BrandGuardianAgent
from pramabu_agents.agents.qa import QAAgent
from pramabu_agents.config import load_brand
from pramabu_agents.orchestrator import Orchestrator
from pramabu_agents.report import pack_to_markdown, write_outputs


def test_weekly_pipeline_produces_approved_pack(tmp_path):
    brand = load_brand()
    pack = Orchestrator(brand).run_weekly_campaign(
        objective="Grow D2C repeat purchase",
        week_of="2026-07-26",
        context={
            "content_pieces": 5,
            "growth_ideas": 4,
            "weekly_ad_budget_inr": 10000,
            "output_dir": str(tmp_path),
        },
    )

    assert pack.brand == "Parambu Organics"
    assert any("parambu.in" in action for action in pack.ecommerce_actions)
    assert pack.week_of == "2026-07-26"
    assert len(pack.trends) >= 3
    assert len(pack.insights) >= 3
    assert len(pack.ideas) == 5
    assert len(pack.creatives) >= 3
    assert len(pack.social_calendar) >= 3
    assert pack.ecommerce_actions
    assert pack.ad_plan
    assert len(pack.growth_opportunities) == 4
    assert pack.marketplace_actions
    assert pack.influencer_plan
    assert pack.crm_actions
    assert pack.supply_chain_actions
    assert pack.crisis_pr_plan
    assert pack.localization_plan
    assert pack.analytics_plan
    assert pack.posters
    assert all(Path(p.path).exists() for p in pack.posters)
    assert pack.approved is True
    assert any(m.role.value == "orchestrator" for m in pack.agent_trace)

    agent_names = [a.name for a in Orchestrator(brand).pipeline]
    for required in (
        "Poster Production",
        "Marketplace",
        "Influencer",
        "CRM",
        "Supply Chain",
        "Crisis & PR",
        "Localization",
    ):
        assert required in agent_names

    paths = write_outputs(pack, tmp_path)
    assert paths["json"].exists()
    assert paths["markdown"].exists()
    md = pack_to_markdown(pack)
    assert "Weekly Campaign Pack" in md
    assert "Content Ideas" in md
    assert "Poster Assets" in md
    assert "Marketplace Actions" in md
    assert "Influencer / UGC Plan" in md
    assert "CRM Actions" in md


def test_brand_guardian_flags_forbidden_claims():
    brand = load_brand()
    orch = Orchestrator(brand)
    pack = orch.run_weekly_campaign(week_of="2026-07-26", context={"content_pieces": 3})
    pack.creatives[0].headline = "Clinically proven miracle clean"
    pack.creatives[0].body = "This cures all stains and is 100% natural guaranteed"
    pack.qa_flags = []

    brand_guardian = next(a for a in orch.pipeline if isinstance(a, BrandGuardianAgent))
    qa = next(a for a in orch.pipeline if isinstance(a, QAAgent))
    pack = brand_guardian.run(pack, {})
    pack = qa.run(pack, {})

    assert pack.qa_flags
    assert pack.approved is False
