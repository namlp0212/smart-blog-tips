"""SEO optimization utilities."""

import re
from bs4 import BeautifulSoup


def extract_headings(content: str) -> list[str]:
    """Extract all H2/H3 headings from HTML content."""
    soup = BeautifulSoup(content, "lxml")
    return [tag.get_text(strip=True) for tag in soup.find_all(["h2", "h3"])]


def count_keyword_density(content: str, keyword: str) -> float:
    """Return keyword density as a percentage."""
    text = BeautifulSoup(content, "lxml").get_text()
    words = text.lower().split()
    keyword_words = keyword.lower().split()
    count = sum(
        1 for i in range(len(words) - len(keyword_words) + 1)
        if words[i:i + len(keyword_words)] == keyword_words
    )
    return round((count / len(words)) * 100, 2) if words else 0.0


def check_seo_score(post: dict) -> dict:
    """
    Basic SEO checklist. Returns a score dict.
    post = {title, content, meta_description, keyword, slug}
    """
    keyword = post.get("keyword", "").lower()
    title = post.get("title", "").lower()
    content = post.get("content", "")
    meta = post.get("meta_description", "").lower()
    slug = post.get("slug", "").lower()

    checks = {
        "keyword_in_title": keyword in title,
        "keyword_in_meta": keyword in meta,
        "keyword_in_slug": keyword.replace(" ", "-") in slug or keyword.replace(" ", "") in slug.replace("-", ""),
        "meta_length_ok": 120 <= len(meta) <= 160,
        "has_h2": "<h2" in content,
        "has_faq": "faq" in content.lower(),
        "has_internal_link": 'href="/' in content or 'href="http' in content,
        "keyword_density_ok": 0.5 <= count_keyword_density(content, keyword) <= 2.5,
        "word_count_ok": len(content.split()) >= 1000,
    }

    passed = sum(checks.values())
    score = round((passed / len(checks)) * 100)
    return {"score": score, "checks": checks, "passed": passed, "total": len(checks)}


def generate_tags_from_content(keyword: str, content: str, max_tags: int = 5) -> list[str]:
    """Generate simple tag list from keyword and headings."""
    tags = [keyword]
    soup = BeautifulSoup(content, "lxml")
    headings = [h.get_text(strip=True) for h in soup.find_all(["h2", "h3"])]
    # Extract 2-3 word phrases from headings as tags
    for h in headings[:max_tags]:
        words = h.split()
        if 2 <= len(words) <= 4:
            tags.append(h.lower())
    return list(dict.fromkeys(tags))[:max_tags]
