"""
Generate blog post content.

Provider priority (auto-detected):
  1. Groq API  — if GROQ_API_KEY is set (free tier, fast)
  2. Anthropic  — if ANTHROPIC_API_KEY is set
  3. claude CLI — fallback via subprocess (works when running inside Claude Code session)
"""

import subprocess
import os
import re
from rich.console import Console
from config.settings import MIN_WORD_COUNT
from content.prompts import build_blog_post_prompt, build_meta_description_prompt, build_title_prompt

console = Console()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


def _ask_groq(prompt: str) -> str:
    import requests, time
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 8192,
        "temperature": 0.7,
    }
    for attempt in range(3):
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=60)
        if resp.status_code == 429:
            wait = 30 * (attempt + 1)
            console.print(f"[yellow]Groq rate limit — chờ {wait}s...[/yellow]")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    raise RuntimeError("Groq rate limit sau 3 lần thử")


def _ask_anthropic(prompt: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


def _ask_claude_cli(prompt: str) -> str:
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True, text=True, timeout=300,
        stdin=subprocess.DEVNULL, env=os.environ.copy(),
    )
    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise RuntimeError(f"claude CLI: {err[:200]}")
    return result.stdout.strip()


def _ask(prompt: str) -> str:
    """Auto-select provider and call AI."""
    if GROQ_API_KEY:
        console.print("[dim]provider: groq[/dim]")
        return _ask_groq(prompt)
    if ANTHROPIC_API_KEY:
        console.print("[dim]provider: anthropic sdk[/dim]")
        return _ask_anthropic(prompt)
    console.print("[dim]provider: claude cli[/dim]")
    return _ask_claude_cli(prompt)


def generate_blog_post(
    keyword: str,
    related_keywords: list[str] = None,
    cluster_context: str = None,
) -> dict:
    console.print(f"[cyan]Generating content for:[/cyan] {keyword}")
    if cluster_context:
        console.print(f"[dim]Cluster context: {cluster_context}[/dim]")

    # Auto-fetch related keywords from Google autocomplete if not provided
    if not related_keywords:
        try:
            from keyword_research.fetcher import get_google_autocomplete
            suggestions = get_google_autocomplete(keyword)
            related_keywords = suggestions[:8] if suggestions else None
        except Exception:
            pass

    title = _generate_title(keyword)
    console.print(f"[green]Title:[/green] {title}")

    content_html = _ask(build_blog_post_prompt(keyword, related_keywords, cluster_context))
    content_html = content_html.strip()
    word_count = len(content_html.split())
    console.print(f"[green]Content generated:[/green] ~{word_count} words")

    if word_count < MIN_WORD_COUNT:
        console.print(f"[yellow]Content short ({word_count} words), regenerating with expanded prompt...[/yellow]")
        content_html = _ask(build_blog_post_prompt(keyword, related_keywords, cluster_context)).strip()
        word_count = len(content_html.split())

    meta_desc = _ask(build_meta_description_prompt(keyword, content_html)).strip()

    return {
        "keyword": keyword,
        "title": title,
        "slug": _keyword_to_slug(keyword),
        "content": content_html,
        "meta_description": meta_desc,
        "word_count": word_count,
        "related_keywords": related_keywords or [],
        "cluster_context": cluster_context,
    }


def _generate_title(keyword: str) -> str:
    output = _ask(build_title_prompt(keyword))
    lines = [l.strip() for l in output.splitlines() if l.strip()]
    title = lines[0].lstrip("1234567890.). ").strip() if lines else keyword
    return title


def _keyword_to_slug(keyword: str) -> str:
    slug = keyword.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug.strip("-")
