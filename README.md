# Pramabu Agents

Multi-agent system for FMCG brand operations: content, social, e-commerce, marketing, and growth.

## Start here (immediate)

We are shipping **Phase 1 MVP now** — a runnable weekly pipeline that coordinates specialist agents and outputs a campaign pack you can review today.

| Phase | Focus | Status |
|---|---|---|
| **0 – Today** | Run pipeline in template mode, customize `brand/brand_bible.yaml` | Ready |
| **1 – This sprint** | LLM mode + human review loop for weekly content/ads/site actions | In progress |
| **2 – Next** | Social drafts, ads APIs, marketplace listings, approval workflow | Planned |
| **3 – Scale** | CRM, influencer, supply chain, crisis/PR, closed-loop learning | Planned |

### Why this starting point

Building every agent at once stalls delivery. The fastest path to value:

1. **Orchestrator + weekly campaign pack** (ideas → creatives → social → ads → site → growth)
2. **Brand bible** as shared truth for all agents
3. **Template mode** so the system works immediately without API keys
4. **Optional LLM mode** when `OPENAI_API_KEY` is set

## MVP agents included

1. Orchestrator  
2. Trend Scout  
3. Market Analysis  
4. Content Ideation  
5. Creative Production  
6. Brand Guardian  
7. Social Media Manager  
8. E-commerce Website  
9. Performance Marketing  
10. Business Growth  
11. Analytics & BI  
12. QA (approval gate)

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# See roadmap
python -m pramabu_agents plan

# List agents
python -m pramabu_agents agents

# Run this week's campaign pack (no API key needed)
python -m pramabu_agents weekly --print
```

Outputs land in `output/`:

- `campaign_YYYY-MM-DD.json`
- `campaign_YYYY-MM-DD.md`

### Optional LLM mode

```bash
cp .env.example .env
# set OPENAI_API_KEY=...
python -m pramabu_agents weekly --objective "Grow D2C repeat purchase"
```

## Customize your brand

Edit `brand/brand_bible.yaml`:

- Brand voice / forbidden claims
- Real SKUs and benefits
- Channels and weekly defaults
- Goals and KPIs

## Weekly pipeline

```text
Goal
  → Trend Scout
  → Market Analysis
  → Content Ideation
  → Creative Production
  → Brand Guardian
  → Social Media
  → E-commerce
  → Performance Marketing
  → Business Growth
  → Analytics
  → QA / Approval
```

## Project layout

```text
brand/brand_bible.yaml          # Brand source of truth
pramabu_agents/
  agents/                       # Specialist agents
  orchestrator.py               # Pipeline runner
  cli.py                        # CLI entrypoint
  models.py                     # Shared schemas
  report.py                     # Markdown/JSON export
tests/                          # Pipeline tests
```

## Tests

```bash
pytest -q
```

## Next build priorities

1. Connect Instagram/Facebook draft publishing (manual approve first)
2. Hook Meta/Google ads campaign draft creation
3. Website agent → GitHub issues / Shopify task export
4. Simple approval UI or Slack “Approve / Reject”
5. Add marketplace + influencer agents once weekly loop is stable
