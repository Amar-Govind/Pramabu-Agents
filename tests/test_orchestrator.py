from pramabu_agents.config import load_brand
from pramabu_agents.orchestrator import Orchestrator
from pramabu_agents.report import pack_to_markdown, write_outputs


def test_weekly_pipeline_produces_approved_pack(tmp_path):
    brand = load_brand()
    pack = Orchestrator(brand).run_weekly_campaign(
        objective="Grow D2C repeat purchase",
        week_of="2026-07-26",
        context={"content_pieces": 5, "growth_ideas": 4, "weekly_ad_budget_inr": 10000},
    )

    assert pack.brand == "Pramabu"
    assert pack.week_of == "2026-07-26"
    assert len(pack.trends) >= 3
    assert len(pack.insights) >= 3
    assert len(pack.ideas) == 5
    assert len(pack.creatives) >= 3
    assert len(pack.social_calendar) >= 3
    assert pack.ecommerce_actions
    assert pack.ad_plan
    assert len(pack.growth_opportunities) == 4
    assert pack.analytics_plan
    assert pack.approved is True
    assert any(m.role.value == "orchestrator" for m in pack.agent_trace)

    paths = write_outputs(pack, tmp_path)
    assert paths["json"].exists()
    assert paths["markdown"].exists()
    md = pack_to_markdown(pack)
    assert "Weekly Campaign Pack" in md
    assert "Content Ideas" in md


def test_brand_guardian_flags_forbidden_claims():
    brand = load_brand()
    # Inject a forbidden claim into generated creative via a tiny custom run path
    orch = Orchestrator(brand)
    pack = orch.run_weekly_campaign(week_of="2026-07-26", context={"content_pieces": 3})
    pack.creatives[0].headline = "Clinically proven miracle clean"
    pack.creatives[0].body = "This cures all stains and is 100% natural guaranteed"
    pack.qa_flags = []
    pack = orch.pipeline[4].run(pack, {})  # BrandGuardian
    pack = orch.pipeline[-1].run(pack, {})  # QA

    assert pack.qa_flags
    assert pack.approved is False
