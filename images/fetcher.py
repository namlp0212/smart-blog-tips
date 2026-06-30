"""Fetch relevant images from Pexels or Unsplash APIs."""

import requests
import os
from rich.console import Console
from config.settings import PEXELS_API_KEY, UNSPLASH_ACCESS_KEY

console = Console()


def fetch_from_pexels(keyword: str, count: int = 3) -> list[dict]:
    """Fetch images from Pexels API."""
    if not PEXELS_API_KEY:
        return []
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": keyword, "per_page": count, "orientation": "landscape"}
    try:
        resp = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            photos = resp.json().get("photos", [])
            return [
                {
                    "url": p["src"]["large"],
                    "alt": p.get("alt", keyword),
                    "photographer": p.get("photographer", ""),
                    "source": "pexels",
                }
                for p in photos
            ]
    except Exception as e:
        console.print(f"[yellow]Pexels error: {e}[/yellow]")
    return []


def fetch_from_unsplash(keyword: str, count: int = 3) -> list[dict]:
    """Fetch images from Unsplash API."""
    if not UNSPLASH_ACCESS_KEY:
        return []
    params = {"query": keyword, "per_page": count, "orientation": "landscape", "client_id": UNSPLASH_ACCESS_KEY}
    try:
        resp = requests.get("https://api.unsplash.com/search/photos", params=params, timeout=10)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            return [
                {
                    "url": r["urls"]["regular"],
                    "alt": r.get("alt_description", keyword) or keyword,
                    "photographer": r["user"]["name"],
                    "source": "unsplash",
                }
                for r in results
            ]
    except Exception as e:
        console.print(f"[yellow]Unsplash error: {e}[/yellow]")
    return []


def get_featured_image(keyword: str) -> dict | None:
    """Get one featured image — try Pexels first, fallback to Unsplash."""
    images = fetch_from_pexels(keyword, count=1)
    if not images:
        images = fetch_from_unsplash(keyword, count=1)
    if images:
        console.print(f"[green]Image found:[/green] {images[0]['source']} — {images[0]['url'][:60]}...")
        return images[0]
    console.print("[yellow]No image found, post will have no featured image[/yellow]")
    return None


def download_image(url: str, dest_path: str) -> bool:
    """Download image to local path."""
    try:
        resp = requests.get(url, timeout=15, stream=True)
        if resp.status_code == 200:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except Exception as e:
        console.print(f"[red]Download error: {e}[/red]")
    return False
