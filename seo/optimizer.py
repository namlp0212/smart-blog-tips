"""SEO optimization utilities."""

import re
from bs4 import BeautifulSoup


def extract_headings(content: str) -> list[str]:
    soup = BeautifulSoup(content, "lxml")
    return [tag.get_text(strip=True) for tag in soup.find_all(["h2", "h3"])]


def count_keyword_density(content: str, keyword: str) -> float:
    text = BeautifulSoup(content, "lxml").get_text()
    words = text.lower().split()
    keyword_words = keyword.lower().split()
    count = sum(
        1 for i in range(len(words) - len(keyword_words) + 1)
        if words[i:i + len(keyword_words)] == keyword_words
    )
    return round((count / len(words)) * 100, 2) if words else 0.0


def check_images_have_alt(content: str) -> bool:
    """Return True if all <img> tags have non-empty alt attributes."""
    soup = BeautifulSoup(content, "lxml")
    imgs = soup.find_all("img")
    if not imgs:
        return True
    return all(img.get("alt", "").strip() for img in imgs)


def count_external_links(content: str) -> int:
    soup = BeautifulSoup(content, "lxml")
    return sum(1 for a in soup.find_all("a", href=True) if a["href"].startswith("http"))


def has_lsi_keywords(content: str, related_keywords: list[str]) -> bool:
    """Check that at least 40% of related keywords appear in the content."""
    if not related_keywords:
        return True
    text = BeautifulSoup(content, "lxml").get_text().lower()
    found = sum(1 for kw in related_keywords if kw.lower() in text)
    return (found / len(related_keywords)) >= 0.4


def estimate_read_time(content: str) -> int:
    text = BeautifulSoup(content, "lxml").get_text()
    return max(1, len(text.split()) // 200)


def _keyword_in_first_para(content: str, keyword: str) -> bool:
    soup = BeautifulSoup(content, "lxml")
    first_p = soup.find("p")
    if not first_p:
        return False
    return keyword in first_p.get_text().lower()


def check_seo_score(post: dict) -> dict:
    """
    Extended SEO checklist. Returns score dict with per-check details.
    post = {title, content, meta_description, keyword, slug, related_keywords?}
    """
    keyword = post.get("keyword", "").lower()
    title = post.get("title", "").lower()
    content = post.get("content", "")
    meta = post.get("meta_description", "").lower()
    slug = post.get("slug", "").lower()
    related = post.get("related_keywords", [])

    soup = BeautifulSoup(content, "lxml")
    text_content = soup.get_text()
    word_count = len(text_content.split())

    checks = {
        # Core keyword placement
        "keyword_in_title": keyword in title,
        "keyword_in_meta": keyword in meta,
        "keyword_in_slug": (
            keyword.replace(" ", "-") in slug
            or keyword.replace(" ", "") in slug.replace("-", "")
        ),
        "keyword_in_first_paragraph": _keyword_in_first_para(content, keyword),

        # Meta tags quality
        "meta_length_ok": 130 <= len(meta) <= 160,
        "title_length_ok": 45 <= len(post.get("title", "")) <= 65,

        # Content structure
        "has_h2": bool(soup.find("h2")),
        "has_h3": bool(soup.find("h3")),
        "has_faq": "faq" in content.lower() or "frequently asked" in content.lower(),
        "has_table_or_list": bool(soup.find(["table", "ul", "ol"])),

        # Images
        "images_have_alt": check_images_have_alt(content),

        # Links
        "has_internal_link": 'href="/' in content,
        "has_external_link": count_external_links(content) >= 2,

        # Keyword density
        "keyword_density_ok": 0.5 <= count_keyword_density(content, keyword) <= 2.0,

        # Length
        "word_count_ok": word_count >= 2000,
        "word_count_great": word_count >= 2500,

        # LSI / related keywords
        "lsi_keywords_present": has_lsi_keywords(content, related),
    }

    passed = sum(checks.values())
    score = round((passed / len(checks)) * 100)

    return {
        "score": score,
        "checks": checks,
        "passed": passed,
        "total": len(checks),
        "word_count": word_count,
        "read_time": estimate_read_time(content),
        "keyword_density": count_keyword_density(content, keyword),
    }


def generate_tags_from_content(keyword: str, content: str, max_tags: int = 5) -> list[str]:
    tags = [keyword]
    soup = BeautifulSoup(content, "lxml")
    headings = [h.get_text(strip=True) for h in soup.find_all(["h2", "h3"])]
    for h in headings[:max_tags]:
        words = h.split()
        if 2 <= len(words) <= 4:
            tags.append(h.lower())
    return list(dict.fromkeys(tags))[:max_tags]


def print_seo_report(seo: dict, console=None):
    """Print a detailed SEO check report to the console."""
    if console is None:
        from rich.console import Console
        console = Console()

    from rich.table import Table
    table = Table(title="SEO Check Report", show_header=True, header_style="bold cyan")
    table.add_column("Check", style="dim")
    table.add_column("Result", justify="center")

    icons = {True: "[green]✓[/green]", False: "[red]✗[/red]"}
    for check, passed in seo["checks"].items():
        label = check.replace("_", " ").title()
        table.add_row(label, icons[passed])

    console.print(table)
    console.print(
        f"[bold]Score:[/bold] {seo['score']}/100  |  "
        f"[bold]Words:[/bold] {seo['word_count']}  |  "
        f"[bold]Read time:[/bold] {seo['read_time']} min  |  "
        f"[bold]Density:[/bold] {seo['keyword_density']}%"
    )
