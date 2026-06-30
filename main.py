"""
CLI entry point for the SEO AI Blog pipeline.

Usage:
  python main.py run                          # Run pipeline with keywords.csv
  python main.py run --limit 5               # Process max 5 keywords
  python main.py run --dry-run               # Generate content only, no publish
  python main.py run --keywords "keyword"    # Process a single keyword
  python main.py suggest "weight loss"       # Suggest questions for a niche
  python main.py cluster                     # Show topic cluster status
  python main.py cluster --next              # Show recommended next keywords
  python main.py cluster --add "pillar" "kw1" "kw2"  # Add a new cluster
  python main.py check-wp                    # Test WordPress connection
  python main.py stats                       # Show published post stats
"""

import argparse
import sys
from rich.console import Console
from rich.table import Table

console = Console()


def cmd_run(args):
    from pipeline.runner import run_pipeline
    keywords = [args.keywords] if args.keywords else None
    run_pipeline(keywords=keywords, limit=args.limit, dry_run=args.dry_run, auto_push=not args.no_push)


def cmd_suggest(args):
    from keyword_research.fetcher import suggest_questions
    from keyword_research.filter import deduplicate
    questions = suggest_questions(args.niche)
    questions = deduplicate(questions)
    console.print(f"\n[bold green]{len(questions)} suggested questions for '{args.niche}':[/bold green]")
    for i, q in enumerate(questions, 1):
        console.print(f"  {i:2}. {q}")
    console.print(f"\n[dim]Tip: Add your favorites to data/keywords.csv and run: python main.py run[/dim]")


def cmd_check_wp(args):
    from publisher.wordpress import test_connection
    ok = test_connection()
    sys.exit(0 if ok else 1)


def cmd_cluster(args):
    from keyword_research.cluster import (
        print_cluster_status, add_cluster, get_pending_cluster_keywords
    )
    import json, os
    from config.settings import DATA_DIR

    if args.add:
        pillar = args.add[0]
        pages = args.add[1:]
        if not pages:
            console.print("[red]Usage: --add <pillar> <cluster1> <cluster2> ...[/red]")
            return
        add_cluster(pillar, pages)
        return

    published_file = os.path.join(DATA_DIR, "published.json")
    published_keywords: set[str] = set()
    if os.path.exists(published_file):
        with open(published_file) as f:
            records = json.load(f)
        published_keywords = {r["keyword"].lower() for r in records}

    if args.next:
        pending = get_pending_cluster_keywords(published_keywords)
        limit = args.limit or 10
        table = Table(
            title="Recommended Next Keywords (Cluster Priority)",
            show_header=True, header_style="bold cyan"
        )
        table.add_column("#", justify="right", style="dim")
        table.add_column("Type", width=8)
        table.add_column("Keyword")
        table.add_column("Pillar")
        for i, p in enumerate(pending[:limit], 1):
            type_label = "[bold yellow]PILLAR[/bold yellow]" if p["type"] == "pillar" else "cluster"
            table.add_row(str(i), type_label, p["keyword"], p["pillar"])
        console.print(table)
    else:
        print_cluster_status(published_keywords)


def cmd_stats(args):
    import json, os
    from config.settings import DATA_DIR
    path = os.path.join(DATA_DIR, "published.json")
    if not os.path.exists(path):
        console.print("[yellow]No published posts yet.[/yellow]")
        return
    with open(path) as f:
        records = json.load(f)
    table = Table(title=f"Published Posts ({len(records)} total)", show_header=True, header_style="bold cyan")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Keyword")
    table.add_column("SEO", justify="right")
    table.add_column("Words", justify="right")
    table.add_column("Status")
    table.add_column("Published At")
    for i, r in enumerate(records, 1):
        table.add_row(
            str(i), r["keyword"], str(r.get("seo_score", "-")),
            str(r.get("word_count", "-")), r.get("status", "-"),
            r.get("published_at", "-")[:10],
        )
    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="SEO AI Blog — Auto-generate and publish SEO blog posts")
    subparsers = parser.add_subparsers(dest="command")

    # run
    run_parser = subparsers.add_parser("run", help="Run the blog generation pipeline")
    run_parser.add_argument("--keywords", type=str, help="Single keyword to process")
    run_parser.add_argument("--limit", type=int, default=3, help="Max posts to generate per run")
    run_parser.add_argument("--dry-run", action="store_true", help="Generate content without publishing")
    run_parser.add_argument("--no-push", action="store_true", help="Skip auto git push to GitHub")

    # suggest
    suggest_parser = subparsers.add_parser("suggest", help="Suggest questions for a niche keyword")
    suggest_parser.add_argument("niche", type=str, help="Niche keyword (e.g. 'weight loss')")

    # cluster
    cluster_parser = subparsers.add_parser("cluster", help="Manage topic clusters")
    cluster_parser.add_argument("--next", action="store_true", help="Show next recommended keywords")
    cluster_parser.add_argument("--add", nargs="+", metavar="KW", help="Add cluster: <pillar> <kw1> <kw2> ...")
    cluster_parser.add_argument("--limit", type=int, default=10, help="Max items to show with --next")

    # check-wp
    subparsers.add_parser("check-wp", help="Test WordPress connection")

    # stats
    subparsers.add_parser("stats", help="Show published post statistics")

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args)
    elif args.command == "suggest":
        cmd_suggest(args)
    elif args.command == "cluster":
        cmd_cluster(args)
    elif args.command == "check-wp":
        cmd_check_wp(args)
    elif args.command == "stats":
        cmd_stats(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
