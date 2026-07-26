from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pramabu_agents.config import load_brand, load_env, llm_enabled
from pramabu_agents.orchestrator import Orchestrator
from pramabu_agents.report import pack_to_markdown, write_outputs

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pramabu",
        description="Pramabu FMCG multi-agent system",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    weekly = sub.add_parser("weekly", help="Run the weekly campaign pipeline")
    weekly.add_argument("--objective", default=None, help="Campaign objective override")
    weekly.add_argument("--week-of", default=None, help="ISO date for the week (YYYY-MM-DD)")
    weekly.add_argument("--budget", type=int, default=25000, help="Weekly ad budget INR")
    weekly.add_argument("--content-pieces", type=int, default=None, help="Number of content ideas")
    weekly.add_argument(
        "--output-dir",
        default="output",
        help="Directory for JSON/Markdown outputs",
    )
    weekly.add_argument("--print", action="store_true", help="Print markdown report to terminal")

    agents = sub.add_parser("agents", help="List MVP agents and roles")
    agents.add_argument("--verbose", action="store_true")

    plan = sub.add_parser("plan", help="Show the start plan / roadmap")
    _ = plan

    return parser


def cmd_agents(verbose: bool = False) -> None:
    rows = [
        ("Orchestrator", "Routes goals through the weekly pipeline"),
        ("Trend Scout", "Finds current social/content trends"),
        ("Market Analysis", "Category, competitor, demand insights"),
        ("Content Ideation", "Ideas for posters, reels, shorts"),
        ("Creative Production", "Headlines, scripts, visual briefs"),
        ("Brand Guardian", "Tone, claims, compliance checks"),
        ("Social Media Manager", "Weekly calendar + captions"),
        ("E-commerce Website", "PDP/site improvement actions"),
        ("Performance Marketing", "Paid media allocation plan"),
        ("Business Growth", "Options to improve the business"),
        ("Analytics & BI", "Measurement and learning loop"),
        ("QA", "Approval gate before publish"),
    ]
    table = Table(title="Pramabu MVP Agents")
    table.add_column("Agent")
    table.add_column("Role")
    for name, role in rows:
        table.add_row(name, role)
    console.print(table)
    if verbose:
        console.print(
            Panel(
                "Phase 1 ships these 12 roles. Later phases add influencer, CRM, supply chain, "
                "marketplace, crisis/PR, and localization agents.",
                title="Roadmap note",
            )
        )


def cmd_plan() -> None:
    console.print(
        Panel(
            """[bold]Where to start (immediate)[/bold]

Phase 0 — Today
• Run template-mode weekly pipeline (no API key needed)
• Fill brand/brand_bible.yaml with real SKUs and voice
• Review output/ campaign pack with humans

Phase 1 — This sprint
• Add OPENAI_API_KEY for stronger ideation/creatives
• Connect one social channel draft workflow
• Connect website checklist to your store backlog

Phase 2 — Next
• Performance ads API hooks (Meta/Google)
• Marketplace listing agent
• Human approval UI / Slack notifications

Phase 3 — Scale
• CRM, influencer, supply chain, crisis agents
• Closed-loop learning from analytics winners
""",
            title="Start Plan",
            expand=False,
        )
    )


def cmd_weekly(args: argparse.Namespace) -> None:
    load_env()
    brand = load_brand()
    context = {"weekly_ad_budget_inr": args.budget}
    if args.content_pieces is not None:
        context["content_pieces"] = args.content_pieces

    mode = "LLM" if llm_enabled() else "template"
    console.print(f"[cyan]Running weekly pipeline in {mode} mode...[/cyan]")

    orchestrator = Orchestrator(brand)
    pack = orchestrator.run_weekly_campaign(
        objective=args.objective,
        week_of=args.week_of,
        context=context,
    )

    paths = write_outputs(pack, Path(args.output_dir))
    console.print(
        Panel(
            f"Brand: {pack.brand}\n"
            f"Week: {pack.week_of}\n"
            f"Ideas: {len(pack.ideas)} | Creatives: {len(pack.creatives)} | Posts: {len(pack.social_calendar)}\n"
            f"Approved: {pack.approved}\n"
            f"JSON: {paths['json']}\n"
            f"Markdown: {paths['markdown']}",
            title="Campaign Pack Ready",
            style="green" if pack.approved else "yellow",
        )
    )

    if args.print:
        console.print(pack_to_markdown(pack))


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "agents":
        cmd_agents(verbose=args.verbose)
    elif args.command == "plan":
        cmd_plan()
    elif args.command == "weekly":
        cmd_weekly(args)
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
