"""Publish posts to WordPress via REST API."""

import requests
import base64
import os
from rich.console import Console
from config.settings import WP_URL, WP_USERNAME, WP_APP_PASSWORD, DEFAULT_CATEGORY_ID, DEFAULT_STATUS

console = Console()


def _get_auth_header() -> dict:
    credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode("utf-8")
    return {"Authorization": f"Basic {token}"}


def test_connection() -> bool:
    """Verify WordPress credentials are working."""
    try:
        resp = requests.get(
            f"{WP_URL}/wp-json/wp/v2/users/me",
            headers=_get_auth_header(),
            timeout=10,
        )
        if resp.status_code == 200:
            user = resp.json()
            console.print(f"[green]WordPress connected as:[/green] {user.get('name')}")
            return True
        console.print(f"[red]WordPress auth failed: {resp.status_code}[/red]")
        return False
    except Exception as e:
        console.print(f"[red]WordPress connection error: {e}[/red]")
        return False


def upload_image(image_path: str, alt_text: str = "") -> int | None:
    """Upload an image file to WordPress media library. Returns media ID."""
    if not os.path.exists(image_path):
        return None
    filename = os.path.basename(image_path)
    ext = filename.rsplit(".", 1)[-1].lower()
    mime_types = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
    mime = mime_types.get(ext, "image/jpeg")

    headers = {**_get_auth_header(), "Content-Disposition": f'attachment; filename="{filename}"', "Content-Type": mime}
    try:
        with open(image_path, "rb") as f:
            resp = requests.post(f"{WP_URL}/wp-json/wp/v2/media", headers=headers, data=f, timeout=30)
        if resp.status_code == 201:
            media = resp.json()
            media_id = media["id"]
            # Set alt text
            if alt_text:
                requests.post(
                    f"{WP_URL}/wp-json/wp/v2/media/{media_id}",
                    headers={**_get_auth_header(), "Content-Type": "application/json"},
                    json={"alt_text": alt_text},
                    timeout=10,
                )
            console.print(f"[green]Image uploaded:[/green] media ID {media_id}")
            return media_id
    except Exception as e:
        console.print(f"[red]Image upload error: {e}[/red]")
    return None


def create_post(
    title: str,
    content: str,
    slug: str,
    meta_description: str = "",
    featured_media_id: int | None = None,
    category_ids: list[int] | None = None,
    tags: list[str] | None = None,
    status: str = DEFAULT_STATUS,
) -> dict | None:
    """Create a new WordPress post. Returns post data including URL."""
    headers = {**_get_auth_header(), "Content-Type": "application/json"}
    payload = {
        "title": title,
        "content": content,
        "slug": slug,
        "status": status,
        "categories": category_ids or [DEFAULT_CATEGORY_ID],
        "meta": {"_yoast_wpseo_metadesc": meta_description} if meta_description else {},
    }
    if featured_media_id:
        payload["featured_media"] = featured_media_id
    if tags:
        tag_ids = _get_or_create_tags(tags)
        payload["tags"] = tag_ids

    try:
        resp = requests.post(f"{WP_URL}/wp-json/wp/v2/posts", headers=headers, json=payload, timeout=30)
        if resp.status_code == 201:
            post = resp.json()
            console.print(f"[green]Post created:[/green] {post.get('link')}")
            return {"id": post["id"], "url": post.get("link", ""), "status": post["status"]}
        console.print(f"[red]Post creation failed: {resp.status_code} — {resp.text[:200]}[/red]")
    except Exception as e:
        console.print(f"[red]Publish error: {e}[/red]")
    return None


def _get_or_create_tags(tag_names: list[str]) -> list[int]:
    """Get existing tag IDs or create new ones."""
    tag_ids = []
    headers = {**_get_auth_header(), "Content-Type": "application/json"}
    for name in tag_names:
        try:
            # Search for existing tag
            resp = requests.get(f"{WP_URL}/wp-json/wp/v2/tags", params={"search": name}, headers=_get_auth_header(), timeout=10)
            if resp.status_code == 200 and resp.json():
                tag_ids.append(resp.json()[0]["id"])
            else:
                # Create new tag
                resp = requests.post(f"{WP_URL}/wp-json/wp/v2/tags", headers=headers, json={"name": name}, timeout=10)
                if resp.status_code == 201:
                    tag_ids.append(resp.json()["id"])
        except Exception:
            pass
    return tag_ids
