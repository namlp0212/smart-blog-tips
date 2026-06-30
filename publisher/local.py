"""
Local file publisher — saves posts as standalone HTML files in output/.
"""

import os
from datetime import datetime
from rich.console import Console

console = Console()
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")

SITE_NAME = "Smart Blog Tips"
SITE_TAGLINE = "SEO, Blogging & Passive Income Strategies"
PRIMARY = "#0f766e"
PRIMARY_LIGHT = "#14b8a6"

COMMON_CSS = """
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --primary: #0f766e;
    --primary-light: #14b8a6;
    --primary-bg: #f0fdfa;
    --text: #1e293b;
    --text-muted: #64748b;
    --border: #e2e8f0;
    --bg: #ffffff;
    --bg-alt: #f8fafc;
    --radius: 12px;
    --shadow: 0 1px 3px rgba(0,0,0,.08), 0 4px 16px rgba(0,0,0,.06);
  }
  body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         color: var(--text); background: var(--bg); line-height: 1.6; }
  a { color: var(--primary); text-decoration: none; }
  a:hover { color: var(--primary-light); }
  img { max-width: 100%; height: auto; }

  /* NAV */
  nav {
    background: var(--bg);
    border-bottom: 1px solid var(--border);
    position: sticky; top: 0; z-index: 100;
    box-shadow: 0 1px 8px rgba(0,0,0,.06);
  }
  .nav-inner {
    max-width: 1100px; margin: 0 auto;
    padding: 0 1.5rem;
    display: flex; align-items: center; justify-content: space-between;
    height: 60px;
  }
  .nav-brand { font-size: 1.15rem; font-weight: 700; color: var(--primary); display: flex; align-items: center; gap: .5rem; }
  .nav-brand span { font-size: 1.3rem; }
  .nav-links { display: flex; gap: 1.5rem; }
  .nav-links a { font-size: .9rem; color: var(--text-muted); font-weight: 500; transition: color .2s; }
  .nav-links a:hover { color: var(--primary); }

  /* FOOTER */
  footer {
    background: #0f172a; color: #94a3b8;
    text-align: center; padding: 2.5rem 1.5rem;
    font-size: .875rem; margin-top: 5rem;
  }
  footer a { color: var(--primary-light); }
  footer strong { color: #fff; }
"""

NAV_HTML = f"""<nav>
  <div class="nav-inner">
    <a class="nav-brand" href="/index.html"><span>✦</span> {SITE_NAME}</a>
    <div class="nav-links">
      <a href="/index.html">Home</a>
      <a href="/index.html#seo">SEO</a>
      <a href="/index.html#affiliate">Affiliate</a>
      <a href="/index.html#ai">AI Tools</a>
    </div>
  </div>
</nav>"""

FOOTER_HTML = f"""<footer>
  <p><strong>{SITE_NAME}</strong> — {SITE_TAGLINE}</p>
  <p style="margin-top:.5rem">© {datetime.now().year} All rights reserved.</p>
</footer>"""


POST_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="google-site-verification" content="O8DsHWRXRJ1vt3f2Th4q-pxR2StGamaRJZwWFLWQ6-0" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>%%TITLE%% | """ + SITE_NAME + """</title>
  <meta name="description" content="%%META_DESC%%"/>
  <meta name="keywords" content="%%KEYWORD%%"/>
  <meta property="og:title" content="%%TITLE%%"/>
  <meta property="og:description" content="%%META_DESC%%"/>
  <meta property="og:type" content="article"/>
  <meta property="og:url" content="%%CANONICAL%%"/>
  <meta property="og:image" content="%%OG_IMAGE%%"/>
  <meta property="og:site_name" content="%%SITE_NAME%%"/>
  <meta name="twitter:card" content="summary_large_image"/>
  <meta name="twitter:title" content="%%TITLE%%"/>
  <meta name="twitter:description" content="%%META_DESC%%"/>
  <meta name="twitter:image" content="%%OG_IMAGE%%"/>
  <link rel="canonical" href="%%CANONICAL%%"/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"/>
  <style>
""" + COMMON_CSS + """
    .post-hero {
      background: linear-gradient(135deg, var(--primary) 0%, #0d9488 100%);
      color: white; padding: 4rem 1.5rem 3rem;
      text-align: center;
    }
    .post-hero .category {
      display: inline-block; background: rgba(255,255,255,.2);
      padding: .3rem .9rem; border-radius: 20px;
      font-size: .8rem; font-weight: 600; letter-spacing: .05em;
      text-transform: uppercase; margin-bottom: 1.2rem;
    }
    .post-hero h1 {
      font-size: clamp(1.6rem, 4vw, 2.4rem);
      font-weight: 700; line-height: 1.25;
      max-width: 750px; margin: 0 auto .8rem; letter-spacing: -.02em;
    }
    .post-hero .post-meta {
      font-size: .875rem; opacity: .85; display: flex;
      justify-content: center; gap: 1.5rem; flex-wrap: wrap; margin-top: 1rem;
    }
    .post-hero .post-meta span { display: flex; align-items: center; gap: .3rem; }

    .post-body {
      max-width: 760px; margin: 0 auto;
      padding: 3rem 1.5rem 4rem;
    }
    .post-body h2 {
      font-size: 1.45rem; font-weight: 700; color: #0f172a;
      margin: 2.5rem 0 .75rem; padding-bottom: .5rem;
      border-bottom: 2px solid var(--primary-bg);
    }
    .post-body h3 { font-size: 1.15rem; font-weight: 600; color: #1e293b; margin: 1.8rem 0 .5rem; }
    .post-body p { margin-bottom: 1.1rem; color: #334155; font-size: 1.05rem; line-height: 1.75; }
    .post-body ul, .post-body ol { padding-left: 1.5rem; margin-bottom: 1.2rem; }
    .post-body li { margin-bottom: .5rem; color: #334155; line-height: 1.7; }
    .post-body strong { color: #0f172a; font-weight: 600; }
    .post-body a { color: var(--primary); border-bottom: 1px solid transparent; transition: border-color .2s; }
    .post-body a:hover { border-color: var(--primary); }
    .post-body img { border-radius: var(--radius); margin: 1.5rem 0; box-shadow: var(--shadow); }

    .tip-box {
      background: var(--primary-bg); border-left: 4px solid var(--primary);
      padding: 1.1rem 1.3rem; border-radius: 0 var(--radius) var(--radius) 0;
      margin: 1.8rem 0;
    }
    .tip-box strong { color: var(--primary); }

    .back-link {
      display: inline-flex; align-items: center; gap: .4rem;
      background: var(--bg-alt); border: 1px solid var(--border);
      padding: .5rem 1rem; border-radius: 8px; font-size: .875rem;
      color: var(--text-muted); font-weight: 500; margin-bottom: 2.5rem;
      transition: all .2s;
    }
    .back-link:hover { background: var(--primary-bg); color: var(--primary); border-color: var(--primary); }

    @media (max-width: 640px) {
      .post-hero { padding: 3rem 1rem 2.5rem; }
      .post-body { padding: 2rem 1rem 3rem; }
    }
  </style>
</head>
<body>
""" + NAV_HTML + """
  <div class="post-hero">
    <div class="category">%%NICHE%%</div>
    <h1>%%TITLE%%</h1>
    <div class="post-meta">
      <span>📅 %%DATE%%</span>
      <span>⏱ %%READ_TIME%% min read</span>
      <span>🔑 %%KEYWORD%%</span>
    </div>
  </div>

  <div class="post-body">
    <a class="back-link" href="/index.html">← Back to all posts</a>
    %%CONTENT%%
  </div>
  %%SCHEMA%%
""" + FOOTER_HTML + """
</body>
</html>"""


INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="google-site-verification" content="O8DsHWRXRJ1vt3f2Th4q-pxR2StGamaRJZwWFLWQ6-0" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>""" + SITE_NAME + """ — """ + SITE_TAGLINE + """</title>
  <meta name="description" content="Expert guides on SEO, blogging, affiliate marketing and making passive income online."/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
  <style>
""" + COMMON_CSS + """
    .hero {
      background: linear-gradient(135deg, #0f172a 0%, #0f766e 100%);
      color: white; text-align: center;
      padding: 5rem 1.5rem 4rem;
    }
    .hero h1 {
      font-size: clamp(2rem, 5vw, 3.2rem); font-weight: 800;
      letter-spacing: -.03em; line-height: 1.15; margin-bottom: 1rem;
    }
    .hero h1 span { color: #5eead4; }
    .hero p { font-size: 1.1rem; opacity: .8; max-width: 520px; margin: 0 auto 2rem; }
    .hero-stats {
      display: flex; justify-content: center; gap: 2.5rem; flex-wrap: wrap;
      margin-top: 2.5rem;
    }
    .hero-stats .stat { text-align: center; }
    .hero-stats .stat strong { display: block; font-size: 1.8rem; font-weight: 800; color: #5eead4; }
    .hero-stats .stat span { font-size: .8rem; opacity: .7; text-transform: uppercase; letter-spacing: .08em; }

    .section { max-width: 1100px; margin: 0 auto; padding: 3.5rem 1.5rem; }
    .section-title {
      font-size: 1.5rem; font-weight: 700; color: #0f172a;
      margin-bottom: 1.5rem; display: flex; align-items: center; gap: .6rem;
    }
    .section-title::after {
      content: ''; flex: 1; height: 2px; background: var(--border);
    }

    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem; }

    .card {
      background: var(--bg); border: 1px solid var(--border);
      border-radius: var(--radius); overflow: hidden;
      transition: transform .2s, box-shadow .2s;
      display: flex; flex-direction: column;
    }
    .card:hover { transform: translateY(-3px); box-shadow: var(--shadow); }
    .card-niche {
      padding: .8rem 1.2rem;
      font-size: .7rem; font-weight: 700; text-transform: uppercase;
      letter-spacing: .1em;
    }
    .card-body { padding: 0 1.2rem 1.4rem; flex: 1; display: flex; flex-direction: column; }
    .card-title {
      font-size: 1rem; font-weight: 600; color: #0f172a;
      line-height: 1.4; margin-bottom: .6rem;
    }
    .card-title a { color: inherit; }
    .card-title a:hover { color: var(--primary); }
    .card-meta {
      margin-top: auto; display: flex; align-items: center;
      justify-content: space-between; font-size: .78rem; color: var(--text-muted);
      padding-top: .9rem; border-top: 1px solid var(--border);
    }
    .card-seo {
      background: #dcfce7; color: #15803d;
      padding: .15rem .5rem; border-radius: 20px; font-weight: 600; font-size: .72rem;
    }

    .niche-colors { --c: var(--primary); }
    .niche-seo       { background: #eff6ff; color: #1d4ed8; }
    .niche-blogging  { background: #fdf4ff; color: #7c3aed; }
    .niche-affiliate { background: #fff7ed; color: #c2410c; }
    .niche-ai        { background: #f0fdf4; color: #15803d; }
    .niche-income    { background: #fefce8; color: #a16207; }
    .niche-marketing { background: #fff1f2; color: #be123c; }

    @media (max-width: 640px) {
      .hero { padding: 3.5rem 1rem 3rem; }
      .hero-stats { gap: 1.5rem; }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
""" + NAV_HTML + """
  <div class="hero">
    <h1>Master SEO, Blogging &<br/><span>Passive Income</span></h1>
    <p>Practical guides to grow your traffic, monetize your blog, and build income streams that work while you sleep.</p>
    <div class="hero-stats">
      <div class="stat"><strong>%%TOTAL%%</strong><span>Articles</span></div>
      <div class="stat"><strong>100%</strong><span>Free</span></div>
      <div class="stat"><strong>SEO</strong><span>Optimized</span></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">📚 All Articles</div>
    <div class="grid">
      %%CARDS%%
    </div>
  </div>
""" + FOOTER_HTML + """
</body>
</html>"""

NICHE_MAP = {
    "seo": ("niche-seo", "SEO"),
    "blogging": ("niche-blogging", "Blogging"),
    "affiliate": ("niche-affiliate", "Affiliate"),
    "ai tools": ("niche-ai", "AI Tools"),
    "passive income": ("niche-income", "Passive Income"),
    "marketing": ("niche-marketing", "Marketing"),
    "monetization": ("niche-ai", "Monetization"),
}


def _extract_first_image(content: str) -> str | None:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, "lxml")
    img = soup.find("img", src=True)
    return img["src"] if img else None


def _niche_class(keyword: str) -> tuple[str, str]:
    kw = keyword.lower()
    for k, v in NICHE_MAP.items():
        if k in kw:
            return v
    return ("niche-seo", "Guide")


def save_post(post_data: dict, seo_score: int = 0) -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    slug = post_data["slug"]
    filename = f"{slug}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)

    content = post_data["content"]
    schema = ""
    if '<script type="application/ld+json">' in content:
        idx = content.index('<script type="application/ld+json">')
        schema = content[idx:]
        content = content[:idx]

    word_count = post_data.get("word_count", 0)
    read_time = max(1, word_count // 200)
    niche_cls, niche_label = _niche_class(post_data["keyword"])

    from config.settings import SITE_URL
    canonical_url = f"{SITE_URL.rstrip('/')}/{slug}.html"
    # Use first image in content as OG image, fallback to a generic placeholder
    og_image = _extract_first_image(content) or f"{SITE_URL.rstrip('/')}/og-default.png"

    html = (POST_TEMPLATE
        .replace("%%TITLE%%", post_data["title"])
        .replace("%%META_DESC%%", post_data.get("meta_description", ""))
        .replace("%%KEYWORD%%", post_data["keyword"])
        .replace("%%DATE%%", datetime.now().strftime("%B %d, %Y"))
        .replace("%%SEO_SCORE%%", str(seo_score))
        .replace("%%CONTENT%%", content)
        .replace("%%SCHEMA%%", schema)
        .replace("%%READ_TIME%%", str(read_time))
        .replace("%%NICHE%%", niche_label)
        .replace("%%CANONICAL%%", canonical_url)
        .replace("%%OG_IMAGE%%", og_image)
        .replace("%%SITE_NAME%%", SITE_NAME)
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
        "word_count": word_count,
        "seo_score": seo_score,
        "published_at": datetime.utcnow().isoformat(),
        "status": "local",
    }


def save_index(published: list[dict]):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cards = ""
    for p in sorted(published, key=lambda x: x.get("published_at", ""), reverse=True):
        kw = p.get("keyword", "")
        niche_cls, niche_label = _niche_class(kw)
        date_str = p.get("published_at", "")[:10]
        words = p.get("word_count", 0)
        seo = p.get("seo_score", 0)
        read_time = max(1, words // 200)

        cards += f"""
      <div class="card">
        <div class="card-niche {niche_cls}">{niche_label}</div>
        <div class="card-body">
          <div class="card-title">
            <a href="{p['slug']}.html">{p['title']}</a>
          </div>
          <div class="card-meta">
            <span>📅 {date_str} &nbsp;·&nbsp; ⏱ {read_time} min</span>
            <span class="card-seo">{seo}/100</span>
          </div>
        </div>
      </div>"""

    html = (INDEX_TEMPLATE
        .replace("%%TOTAL%%", str(len(published)))
        .replace("%%CARDS%%", cards)
    )

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    console.print(f"[green]Index updated:[/green] output/index.html ({len(published)} posts)")
