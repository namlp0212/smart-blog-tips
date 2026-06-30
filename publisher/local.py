"""
Local file publisher — saves posts as standalone HTML files in output/.
No WordPress needed. Files can be opened in browser or deployed to any hosting.
"""

import os
import json
from datetime import datetime
from rich.console import Console

console = Console()
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{meta_description}" />
  <meta name="keywords" content="{keyword}" />
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 18px; line-height: 1.7; color: #222;
      max-width: 780px; margin: 0 auto; padding: 2rem 1.5rem;
    }}
    h1 {{ font-size: 2rem; line-height: 1.3; margin-bottom: 0.5rem; color: #111; }}
    h2 {{ font-size: 1.5rem; margin-top: 2.5rem; color: #1a1a1a; border-bottom: 2px solid #eee; padding-bottom: 0.3rem; }}
    h3 {{ font-size: 1.2rem; margin-top: 1.8rem; color: #333; }}
    p {{ margin: 1rem 0; }}
    ul, ol {{ padding-left: 1.5rem; margin: 1rem 0; }}
    li {{ margin: 0.4rem 0; }}
    a {{ color: #0070f3; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    strong {{ color: #111; }}
    .meta {{ color: #666; font-size: 0.9rem; margin-bottom: 2rem; }}
    .meta span {{ margin-right: 1rem; }}
    .seo-badge {{ display: inline-block; background: #e6f4ea; color: #1e7e34;
                  padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; }}
    hr {{ border: none; border-top: 1px solid #eee; margin: 2rem 0; }}
    @media (max-width: 600px) {{ body {{ font-size: 16px; }} h1 {{ font-size: 1.6rem; }} }}
  </style>
</head>
<body>
  <article>
    <h1>{title}</h1>
    <div class="meta">
      <span>📅 {date}</span>
      <span>🔑 {keyword}</span>
      <span class="seo-badge">SEO {seo_score}/100</span>
    </div>
    <hr/>
    {content}
  </article>
  {schema}
</body>
</html>"""


def save_post(post_data: dict, seo_score: int = 0) -> dict:
    """
    Save post as local HTML file.
    Returns record dict with file path and local URL.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    slug = post_data["slug"]
    filename = f"{slug}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Extract schema tag if present
    content = post_data["content"]
    schema = ""
    if '<script type="application/ld+json">' in content:
        idx = content.index('<script type="application/ld+json">')
        schema = content[idx:]
        content = content[:idx]

    html = HTML_TEMPLATE.format(
        title=post_data["title"],
        meta_description=post_data.get("meta_description", ""),
        keyword=post_data["keyword"],
        date=datetime.now().strftime("%B %d, %Y"),
        seo_score=seo_score,
        content=content,
        schema=schema,
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    console.print(f"[green]Saved:[/green] output/{filename}")

    return {
        "keyword": post_data["keyword"],
        "title": post_data["title"],
        "slug": slug,
        "url": f"output/{filename}",
        "filepath": filepath,
        "word_count": post_data.get("word_count", 0),
        "seo_score": seo_score,
        "published_at": datetime.utcnow().isoformat(),
        "status": "local",
    }


def save_index(published: list[dict]):
    """Generate an index.html listing all published posts."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    rows = ""
    for p in sorted(published, key=lambda x: x.get("published_at", ""), reverse=True):
        rows += f"""
        <tr>
          <td><a href="{p['slug']}.html">{p['title']}</a></td>
          <td>{p['keyword']}</td>
          <td>{p.get('word_count', '-')}</td>
          <td><span class="badge">{p.get('seo_score', '-')}/100</span></td>
          <td>{p.get('published_at', '')[:10]}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>SEO Blog — All Posts</title>
  <style>
    body {{ font-family: sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }}
    h1 {{ color: #111; }} table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
    th {{ background: #f4f4f4; padding: 10px; text-align: left; border-bottom: 2px solid #ddd; }}
    td {{ padding: 10px; border-bottom: 1px solid #eee; }}
    a {{ color: #0070f3; text-decoration: none; }} a:hover {{ text-decoration: underline; }}
    .badge {{ background: #e6f4ea; color: #1e7e34; padding: 2px 8px; border-radius: 4px; font-size: 0.85rem; }}
  </style>
</head>
<body>
  <h1>SEO Blog — {len(published)} Posts</h1>
  <table>
    <thead><tr><th>Title</th><th>Keyword</th><th>Words</th><th>SEO</th><th>Date</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>"""

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    console.print(f"[green]Index updated:[/green] output/index.html ({len(published)} posts)")
