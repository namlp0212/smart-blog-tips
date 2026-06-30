"""
CLI entry point for the SEO AI Blog pipeline.

Usage:
  python main.py run                        # Run pipeline with keywords.csv
  python main.py run --limit 5              # Process max 5 keywords
  python main.py run --dry-run              # Generate content only, no publish
  python main.py run --keywords "how to lose weight fast"
  python main.py suggest "weight loss"      # Suggest questions for a niche
  python main.py check-wp                   # Test WordPress connection
  python main.py stats                      # Show published post stats
"""

import argparse
import sys
from rich.console import Console
from rich.table import Table

console = Console()


def cmd_run(args):
    from pipeline.runner import run_pipeline
    keywords = [args.keywords] if args.keywords else None
    run_pipeline(keywords=keywords, limit=args.limit, dry_run=args.dry_run)


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

    # suggest
    suggest_parser = subparsers.add_parser("suggest", help="Suggest questions for a niche keyword")
    suggest_parser.add_argument("niche", type=str, help="Niche keyword (e.g. 'weight loss')")

    # check-wp
    subparsers.add_parser("check-wp", help="Test WordPress connection")

    # stats
    subparsers.add_parser("stats", help="Show published post statistics")

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args)
    elif args.command == "suggest":
        cmd_suggest(args)
    elif args.command == "check-wp":
        cmd_check_wp(args)
    elif args.command == "stats":
        cmd_stats(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
