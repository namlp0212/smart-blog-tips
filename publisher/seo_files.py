"""Generate sitemap.xml and robots.txt for SEO."""

import os
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def generate_sitemap(published: list[dict], site_url: str):
    """Generate sitemap.xml from published posts list."""
    site_url = site_url.rstrip("/")
    urls = [f"""  <url>
    <loc>{site_url}/{p['slug']}.html</loc>
    <lastmod>{p.get('published_at', datetime.utcnow().isoformat())[:10]}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>""" for p in published]

    # Add homepage
    index_url = f"""  <url>
    <loc>{site_url}/index.html</loc>
    <lastmod>{datetime.utcnow().isoformat()[:10]}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>"""

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{index_url}
{chr(10).join(urls)}
</urlset>"""

    path = os.path.join(OUTPUT_DIR, "sitemap.xml")
    with open(path, "w") as f:
        f.write(xml)
    return path


def generate_robots(site_url: str):
    """Generate robots.txt."""
    site_url = site_url.rstrip("/")
    content = f"""User-agent: *
Allow: /

Sitemap: {site_url}/sitemap.xml
"""
    path = os.path.join(OUTPUT_DIR, "robots.txt")
    with open(path, "w") as f:
        f.write(content)
    return path
