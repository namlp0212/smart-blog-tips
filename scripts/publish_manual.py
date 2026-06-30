"""
Publish a hand-written blog post through the full SEO pipeline.

Use this when you want to provide the article HTML yourself (e.g. authored by
Claude) instead of generating it via Groq/Anthropic. Runs the same formatting,
SEO check, image fetch, save, sitemap and git-push steps as the normal pipeline.

Usage:
  python scripts/publish_manual.py <slug> "Title" "keyword" "meta description"
        [--content-file data/manual/<slug>.html] [--no-push] [--dry-run]

If --content-file is omitted, it defaults to data/manual/<slug>.html
"""

import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from content.formatter import clean_html, inject_faq_schema
from seo.optimizer import check_seo_score, print_seo_report
from images.fetcher import get_featured_image
from publisher.local import save_post, save_index
from config.settings import DATA_DIR, SITE_URL

console = Console()
PUBLISHED_FILE = os.path.join(DATA_DIR, "published.json")


def load_published() -> list[dict]:
    if os.path.exists(PUBLISHED_FILE):
        with open(PUBLISHED_FILE) as f:
            return json.load(f)
    return []


def save_published(records: list[dict]):
    with open(PUBLISHED_FILE, "w") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("title")
    ap.add_argument("keyword")
    ap.add_argument("meta")
    ap.add_argument("--content-file")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    content_file = args.content_file or os.path.join(DATA_DIR, "manual", f"{args.slug}.html")
    if not os.path.exists(content_file):
        console.print(f"[red]Content file not found: {content_file}[/red]")
        sys.exit(1)

    with open(content_file, encoding="utf-8") as f:
        raw = f.read()

    # 1. Clean + 2. FAQ schema (internal links are already hand-written in the file)
    content = clean_html(raw)
    content = inject_faq_schema(content, args.keyword)

    post_data = {
        "keyword": args.keyword,
        "title": args.title,
        "slug": args.slug,
        "content": content,
        "meta_description": args.meta,
        "word_count": len(content.split()),
    }

    # 3. SEO check
    seo = check_seo_score(post_data)
    print_seo_report(seo, console)

    # 4. Featured image (embed at top)
    image_info = get_featured_image(args.keyword)
    if image_info:
        img_tag = (
            f'<img src="{image_info["url"]}" '
            f'alt="{image_info.get("alt") or args.keyword}" '
            f'style="width:100%;border-radius:8px;margin-bottom:1.5rem;" />\n'
        )
        post_data["content"] = img_tag + post_data["content"]

    if args.dry_run:
        console.print(f"[yellow][DRY RUN][/yellow] Would publish: {args.title} (SEO {seo['score']}/100)")
        return

    # 5. Save post
    record = save_post(post_data, seo_score=seo["score"])

    # 6. Update published.json (replace existing record for this keyword)
    published = load_published()
    published = [r for r in published if r["keyword"].lower() != args.keyword.lower()]
    published.append(record)
    save_published(published)
    save_index(published)

    # 7. Regenerate SEO files
    from publisher.seo_files import generate_sitemap, generate_robots
    generate_sitemap(published, SITE_URL)
    generate_robots(SITE_URL)
    console.print("[green]sitemap.xml + robots.txt updated[/green]")

    # 8. Git push
    if not args.no_push:
        from publisher.github_push import push_output, has_remote
        if has_remote():
            push_output(post_titles=[args.title])
        else:
            console.print("[yellow]No git remote — skipping push.[/yellow]")


if __name__ == "__main__":
    main()
