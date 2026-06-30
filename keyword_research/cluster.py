"""
Topic cluster strategy for keyword grouping.

A topic cluster consists of:
- 1 Pillar page  : broad, high-volume keyword (e.g. "affiliate marketing")
- N Cluster pages: specific, long-tail keywords supporting the pillar

Benefits:
- Internal links from cluster → pillar boost pillar authority
- Google sees the site as topically authoritative
- Long-tail pages can rank faster (lower competition)
"""

from __future__ import annotations
import os
import json
from typing import TypedDict
from rich.console import Console
from rich.table import Table

console = Console()

CLUSTERS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "clusters.json"
)

# --- Default topic cluster definitions ---
# Each entry: pillar keyword → list of supporting cluster keywords
# These should match or be subsets of data/keywords.csv
DEFAULT_CLUSTERS: dict[str, list[str]] = {
    "affiliate marketing": [
        "what is affiliate marketing and how does it work",
        "how to start affiliate marketing with no money",
        "can you actually make money from affiliate marketing",
        "can i do affiliate marketing without a website",
        "which affiliate program pays the most",
        "can i do affiliate marketing without showing my face",
        "best affiliate programs for beginners",
    ],
    "make money blogging": [
        "how to make money blogging for beginners",
        "how to make money blogging in 2026",
        "how to start a blog and make money",
        "how to make money with google adsense",
        "how to make passive income online for beginners",
    ],
    "seo for beginners": [
        "best free keyword research tools",
        "how to get free traffic from google",
        "how to write SEO blog posts fast",
        "how to rank on google first page",
        "how to build backlinks for free",
    ],
    "content marketing": [
        "best tools for content marketing",
        "chatgpt prompts for blog writing",
    ],
}


class Cluster(TypedDict):
    pillar: str
    cluster_pages: list[str]
    published_pillar: bool
    published_cluster: list[str]


def load_clusters() -> dict[str, Cluster]:
    """Load cluster state from disk, merging with DEFAULT_CLUSTERS."""
    saved: dict[str, Cluster] = {}
    if os.path.exists(CLUSTERS_FILE):
        with open(CLUSTERS_FILE) as f:
            saved = json.load(f)

    # Merge defaults — add new clusters, don't overwrite existing state
    for pillar, cluster_pages in DEFAULT_CLUSTERS.items():
        if pillar not in saved:
            saved[pillar] = {
                "pillar": pillar,
                "cluster_pages": cluster_pages,
                "published_pillar": False,
                "published_cluster": [],
            }
        else:
            # Add new cluster pages that weren't there before
            existing = set(saved[pillar]["cluster_pages"])
            for kw in cluster_pages:
                if kw not in existing:
                    saved[pillar]["cluster_pages"].append(kw)

    return saved


def save_clusters(clusters: dict[str, Cluster]):
    os.makedirs(os.path.dirname(CLUSTERS_FILE), exist_ok=True)
    with open(CLUSTERS_FILE, "w") as f:
        json.dump(clusters, f, indent=2, ensure_ascii=False)


def get_cluster_for_keyword(keyword: str) -> tuple[str | None, list[str]]:
    """
    Given a keyword, find which cluster it belongs to.
    Returns (pillar_keyword, sibling_cluster_pages) for internal linking context.
    """
    clusters = load_clusters()
    kw_lower = keyword.lower().strip()
    for pillar, data in clusters.items():
        if kw_lower == pillar or kw_lower in [c.lower() for c in data["cluster_pages"]]:
            siblings = [c for c in data["cluster_pages"] if c.lower() != kw_lower]
            return pillar, siblings
    return None, []


def get_pending_cluster_keywords(published_keywords: set[str]) -> list[dict]:
    """
    Return cluster keywords in recommended publish order:
    1. Cluster pages first (they're easier to rank — lower competition)
    2. Pillar pages after enough cluster pages are published

    Returns list of {keyword, type: "cluster"|"pillar", pillar, priority}
    """
    clusters = load_clusters()
    result = []

    for pillar, data in clusters.items():
        cluster_pages = data["cluster_pages"]
        published_cluster = [c for c in cluster_pages if c in published_keywords]
        coverage = len(published_cluster) / len(cluster_pages) if cluster_pages else 0

        # Recommend cluster pages first
        for kw in cluster_pages:
            if kw not in published_keywords:
                result.append({
                    "keyword": kw,
                    "type": "cluster",
                    "pillar": pillar,
                    "priority": 1,
                })

        # Recommend pillar only after >= 50% of cluster pages are published
        if pillar not in published_keywords and coverage >= 0.5:
            result.append({
                "keyword": pillar,
                "type": "pillar",
                "pillar": pillar,
                "priority": 2,
            })

    # Sort: cluster pages before pillars, then by pillar name for grouping
    result.sort(key=lambda x: (x["priority"], x["pillar"]))
    return result


def mark_published(keyword: str):
    """Update cluster state when a keyword is published."""
    clusters = load_clusters()
    kw_lower = keyword.lower().strip()
    for pillar, data in clusters.items():
        if kw_lower == pillar:
            data["published_pillar"] = True
        elif kw_lower in [c.lower() for c in data["cluster_pages"]]:
            if keyword not in data["published_cluster"]:
                data["published_cluster"].append(keyword)
    save_clusters(clusters)


def print_cluster_status(published_keywords: set[str] | None = None):
    """Print a visual overview of all topic clusters and their publish status."""
    clusters = load_clusters()

    if published_keywords is None:
        # Try to load from published.json
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        published_file = os.path.join(data_dir, "published.json")
        if os.path.exists(published_file):
            import json as _json
            with open(published_file) as f:
                records = _json.load(f)
            published_keywords = {r["keyword"].lower() for r in records}
        else:
            published_keywords = set()

    for pillar, data in clusters.items():
        cluster_pages = data["cluster_pages"]
        done = [c for c in cluster_pages if c.lower() in published_keywords]
        coverage = len(done) / len(cluster_pages) if cluster_pages else 0
        pillar_done = pillar.lower() in published_keywords

        table = Table(
            title=f"[bold]Cluster: {pillar.title()}[/bold]  [{len(done)}/{len(cluster_pages)} cluster pages · pillar {'✓' if pillar_done else '✗'}]",
            show_header=True, header_style="bold magenta"
        )
        table.add_column("Type", width=8)
        table.add_column("Keyword")
        table.add_column("Status", justify="center", width=10)

        pillar_status = "[green]Published[/green]" if pillar_done else f"[yellow]{'Ready' if coverage >= 0.5 else 'Waiting'}[/yellow]"
        table.add_row("PILLAR", pillar, pillar_status)

        for kw in cluster_pages:
            status = "[green]✓[/green]" if kw.lower() in published_keywords else "[dim]pending[/dim]"
            table.add_row("cluster", kw, status)

        console.print(table)
        console.print(f"  Coverage: [cyan]{coverage:.0%}[/cyan]\n")


def add_cluster(pillar: str, cluster_pages: list[str]):
    """Add a new topic cluster (or extend existing)."""
    clusters = load_clusters()
    if pillar in clusters:
        existing = set(clusters[pillar]["cluster_pages"])
        for kw in cluster_pages:
            if kw not in existing:
                clusters[pillar]["cluster_pages"].append(kw)
        console.print(f"[green]Updated cluster:[/green] '{pillar}' — now {len(clusters[pillar]['cluster_pages'])} pages")
    else:
        clusters[pillar] = {
            "pillar": pillar,
            "cluster_pages": cluster_pages,
            "published_pillar": False,
            "published_cluster": [],
        }
        console.print(f"[green]New cluster created:[/green] '{pillar}' with {len(cluster_pages)} cluster pages")
    save_clusters(clusters)
