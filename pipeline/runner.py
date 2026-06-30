"""
Main pipeline runner.

Flow:
  keyword → generate content → fetch image → SEO check → publish → save record

Publisher mode:
  - "local"  (default): save HTML files to output/
  - "wordpress": publish via WordPress REST API
"""

import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table

from config.settings import DATA_DIR, LOGS_DIR, POSTS_PER_RUN, WP_URL, SITE_URL
from content.generator import generate_blog_post
from content.formatter import clean_html, inject_faq_schema, inject_internal_links
from images.fetcher import get_featured_image, download_image
from seo.optimizer import check_seo_score, generate_tags_from_content

console = Console()

PUBLISHED_FILE = os.path.join(DATA_DIR, "published.json")
KEYWORDS_FILE = os.path.join(DATA_DIR, "keywords.csv")


def load_published() -> list[dict]:
    if os.path.exists(PUBLISHED_FILE):
        with open(PUBLISHED_FILE) as f:
            return json.load(f)
    return []


def save_published(records: list[dict]):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PUBLISHED_FILE, "w") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def load_pending_keywords() -> list[str]:
    """Load keywords not yet published from keywords.csv."""
    if not os.path.exists(KEYWORDS_FILE):
        console.print(f"[red]keywords.csv not found at {KEYWORDS_FILE}[/red]")
        return []

    import pandas as pd
    df = pd.read_csv(KEYWORDS_FILE)
    published = load_published()
    done_keywords = {r["keyword"] for r in published}

    col = "keyword" if "keyword" in df.columns else df.columns[0]
    pending = [row[col] for _, row in df.iterrows() if row[col] not in done_keywords]
    return pending


def _detect_publisher_mode() -> str:
    """Auto-detect publisher: use wordpress if WP_URL is configured, else local."""
    if WP_URL and WP_URL != "https://yourblog.com":
        return "wordpress"
    return "local"


def run_pipeline(
    keywords: list[str] | None = None,
    limit: int = POSTS_PER_RUN,
    dry_run: bool = False,
    publisher: str = "auto",
    auto_push: bool = True,
):
    """
    Run the full pipeline for a list of keywords.
    publisher: "auto" | "local" | "wordpress"
    """
    console.rule("[bold blue]SEO AI Blog Pipeline[/bold blue]")

    mode = _detect_publisher_mode() if publisher == "auto" else publisher
    console.print(f"[bold]Publisher mode:[/bold] [cyan]{mode}[/cyan]")

    if mode == "wordpress" and not dry_run:
        from publisher.wordpress import test_connection
        if not test_connection():
            console.print("[red]Aborting: WordPress connection failed.[/red]")
            return

    if keywords is None:
        keywords = load_pending_keywords()

    # Reorder keywords by topic cluster priority if no explicit list was given
    if keywords:
        published = load_published()
        published_set = {r["keyword"].lower() for r in published}
        keywords = _prioritize_by_cluster(keywords, published_set)

    if not keywords:
        console.print("[yellow]No pending keywords found.[/yellow]")
        return

    keywords = keywords[:limit]
    console.print(f"[bold]Processing {len(keywords)} keyword(s)[/bold]\n")

    published = load_published()
    results = []

    for i, keyword in enumerate(keywords[:limit], 1):
        console.rule(f"[{i}/{len(keywords)}] {keyword}")
        try:
            result = _process_keyword(keyword, published, dry_run, mode)
            if result:
                published.append(result)
                results.append(result)
                save_published(published)
                if mode == "local" and not dry_run:
                    from publisher.local import save_index
                    save_index(published)
        except Exception as e:
            console.print(f"[red]Error processing '{keyword}': {e}[/red]")
            _log_error(keyword, str(e))
        # Delay giữa các bài để tránh Groq rate limit
        if i < len(keywords) and not dry_run:
            import time
            console.print("[dim]Chờ 15s...[/dim]")
            time.sleep(15)

    _print_summary(results)

    if results and not dry_run and mode == "local":
        # Regenerate SEO files
        from publisher.seo_files import generate_sitemap, generate_robots
        generate_sitemap(published, SITE_URL)
        generate_robots(SITE_URL)
        console.print(f"[green]sitemap.xml + robots.txt updated[/green]")

        # Auto-push to GitHub
        if auto_push:
            from publisher.github_push import push_output, has_remote
            if has_remote():
                push_output(post_titles=[r["title"] for r in results])
            else:
                console.print("[yellow]GitHub remote not set — skipping push.[/yellow]")
                console.print("[dim]Run: git remote add origin https://github.com/USER/REPO.git[/dim]")


def _prioritize_by_cluster(keywords: list[str], published_set: set[str]) -> list[str]:
    """Reorder keywords so cluster pages come before their pillar pages."""
    from keyword_research.cluster import get_pending_cluster_keywords
    pending = get_pending_cluster_keywords(published_set)
    cluster_order = [p["keyword"] for p in pending]

    # Keywords in cluster order first, then anything else (outside clusters)
    ordered = [kw for kw in cluster_order if kw in keywords]
    rest = [kw for kw in keywords if kw not in ordered]
    return ordered + rest


def _process_keyword(keyword: str, published: list[dict], dry_run: bool, mode: str) -> dict | None:
    # Fetch cluster context for better internal linking and prompt enrichment
    from keyword_research.cluster import get_cluster_for_keyword, mark_published
    pillar, siblings = get_cluster_for_keyword(keyword)
    cluster_context = f"This is part of the '{pillar}' topic cluster" if pillar else None

    # 1. Generate content
    post_data = generate_blog_post(keyword, cluster_context=cluster_context)
    content = clean_html(post_data["content"])

    # 2. Inject FAQ schema
    content = inject_faq_schema(content, keyword)

    # 3. Inject internal links
    content = inject_internal_links(content, published)

    # 4. SEO check (include related_keywords for LSI check)
    post_data["content"] = content
    seo = check_seo_score(post_data)
    from seo.optimizer import print_seo_report
    print_seo_report(seo, console)
    console.print(f"[cyan]SEO score:[/cyan] {seo['score']}/100 ({seo['passed']}/{seo['total']} checks passed)")

    # 5. Fetch featured image (only for WordPress mode — local embeds via URL)
    featured_media_id = None
    image_info = get_featured_image(keyword)

    if dry_run:
        console.print(f"[yellow][DRY RUN] Would publish:[/yellow] {post_data['title']}")
        console.print(f"  Slug: {post_data['slug']} | Words: {post_data['word_count']} | SEO: {seo['score']}/100")
        return {
            "keyword": keyword,
            "title": post_data["title"],
            "slug": post_data["slug"],
            "url": "(dry-run)",
            "word_count": post_data["word_count"],
            "seo_score": seo["score"],
            "published_at": datetime.utcnow().isoformat(),
            "status": "dry-run",
        }

    # 6. Publish
    if mode == "local":
        # Embed image as <img> tag at top of content if available
        if image_info:
            img_tag = f'<img src="{image_info["url"]}" alt="{image_info.get("alt", keyword)}" style="width:100%;border-radius:8px;margin-bottom:1.5rem;" />\n'
            post_data["content"] = img_tag + post_data["content"]

        from publisher.local import save_post
        return save_post(post_data, seo_score=seo["score"])

    elif mode == "wordpress":
        if image_info:
            tmp_path = f"/tmp/seo_blog_{keyword[:20].replace(' ', '_')}.jpg"
            if download_image(image_info["url"], tmp_path):
                from publisher.wordpress import upload_image
                featured_media_id = upload_image(tmp_path, alt_text=image_info.get("alt", keyword))

        tags = generate_tags_from_content(keyword, content)
        from publisher.wordpress import create_post
        wp_result = create_post(
            title=post_data["title"],
            content=content,
            slug=post_data["slug"],
            meta_description=post_data["meta_description"],
            featured_media_id=featured_media_id,
            tags=tags,
        )
        if not wp_result:
            console.print(f"[red]Failed to publish: {keyword}[/red]")
            return None
        return {
            "keyword": keyword,
            "title": post_data["title"],
            "slug": post_data["slug"],
            "url": wp_result["url"],
            "word_count": post_data["word_count"],
            "seo_score": seo["score"],
            "published_at": datetime.utcnow().isoformat(),
            "status": wp_result["status"],
        }


def _log_error(keyword: str, error: str):
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(os.path.join(LOGS_DIR, "errors.log"), "a") as f:
        f.write(f"[{datetime.utcnow().isoformat()}] {keyword}: {error}\n")


def _print_summary(results: list[dict]):
    if not results:
        return
    console.rule("[bold green]Summary[/bold green]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Keyword", style="cyan")
    table.add_column("Title")
    table.add_column("Words", justify="right")
    table.add_column("SEO", justify="right")
    table.add_column("Output")
    for r in results:
        table.add_row(
            r["keyword"], r["title"][:45], str(r["word_count"]),
            str(r["seo_score"]) + "/100", r.get("url", "-")
        )
    console.print(table)
