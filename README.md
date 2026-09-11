# Parambu Agents

Multi-agent system for **Parambu Organics** ([parambu.in](https://parambu.in)): content, social, e-commerce, marketing, and growth.

## Start here (immediate)

We are shipping **Phase 1 MVP now** — a runnable weekly pipeline that coordinates specialist agents and outputs a campaign pack you can review today.

| Phase | Focus | Status |
|---|---|---|
| **0 – Today** | Run pipeline against Parambu Organics brand bible + [parambu.in](https://parambu.in) | Ready |
| **1 – Agents** | Full specialist agent suite in weekly campaign pack | Ready |
| **1b – Storefront** | Custom Next.js site in `/storefront` with gold branding, gallery, recommendations, cart, coupons, reviews | Ready |
| **1c – Agent Chat** | Web chat console to talk to agents, upload files, download outputs | Ready |
| **2 – Next** | Razorpay checkout, social drafts, ads APIs, approval workflow, live connectors | Planned |
| **3 – Scale** | Closed-loop learning from analytics winners | Planned |

### Why this starting point

Building every agent at once stalls delivery. The fastest path to value:

1. **Orchestrator + weekly campaign pack** (ideas → creatives → social → ads → site → growth)
2. **Brand bible** as shared truth for all agents
3. **Template mode** so the system works immediately without API keys
4. **Optional LLM mode** when `OPENAI_API_KEY` is set

## Agents included (full suite)

1. Orchestrator  
2. Trend Scout  
3. Market Analysis  
4. Content Ideation  
5. Creative Production  
6. Brand Guardian  
7. Poster Production (renders PNG posters)  
8. Social Media Manager  
9. E-commerce Website  
10. Performance Marketing  
11. Business Growth  
12. Marketplace  
13. Influencer  
14. CRM  
15. Supply Chain  
16. Crisis & PR  
17. Localization  
18. Analytics & BI  
19. QA (approval gate)

## Quick start — agents

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

## Quick start — agent chat console

```bash
pip install -r requirements.txt
python -m agent_chat.app
```

Open http://localhost:8000

Chat like an LLM assistant grounded in your knowledge base:

- Uses `brand/brand_bible.yaml`, product catalog, and uploaded files as context
- Answers product/voice/campaign questions in natural conversation
- When you ask to generate work (`create posters…`, `run weekly campaign…`), specialist agents run as tools
- Download posters/reports from chips under the reply

For live LLM replies (recommended):

```bash
cp .env.example .env
# set OPENAI_API_KEY=...
python -m agent_chat.app
```

## Quick start — custom storefront

```bash
cd storefront
npm install
npm run dev
```

Open http://localhost:3000. Includes home, shop, category pages, product pages, cart, coupons, and reviews. Live checkout remains on https://parambu.in until Razorpay is added.

Outputs land in `output/`:

- `campaign_YYYY-MM-DD.json`
- `campaign_YYYY-MM-DD.md`
- `posters/YYYY-MM-DD/*.png` (generated poster creatives)

### Optional LLM mode

```bash
cp .env.example .env
# set OPENAI_API_KEY=...
python -m pramabu_agents weekly --objective "Grow D2C repeat purchase"
```

## Brand source of truth

Configured for **Parambu Organics** at **https://parambu.in** (WooCommerce).

Categories: Oils · Soap · Gardening

Edit `brand/brand_bible.yaml` to refine:

- Brand voice / forbidden claims
- SKUs, PDP URLs, and benefits
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
  → Poster Production
  → Social Media
  → E-commerce
  → Performance Marketing
  → Business Growth
  → Marketplace
  → Influencer
  → CRM
  → Supply Chain
  → Crisis & PR
  → Localization
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
  poster.py                     # Poster PNG renderer
agent_chat/                     # Web chat console (FastAPI + UI)
storefront/                     # Next.js D2C storefront MVP
tests/                          # Pipeline + chat tests
```

## Tests

```bash
pytest -q
```

## Next build priorities

1. Connect Instagram/Facebook draft publishing (manual approve first)
2. Hook Meta/Google ads campaign draft creation
3. Website agent → WooCommerce / GitHub task export
4. Simple approval UI or Slack “Approve / Reject”
5. Live marketplace + CRM connectors for drafted actions
6. Razorpay native checkout on the storefront
