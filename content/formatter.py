"""Format and enrich HTML content before publishing."""

import re
from bs4 import BeautifulSoup


def inject_internal_links(content: str, published_posts: list[dict]) -> str:
    """Replace matching keywords in content with internal links."""
    if not published_posts:
        return content
    soup = BeautifulSoup(content, "lxml")
    body_text = soup.get_text()

    for post in published_posts:
        keyword = post.get("keyword", "")
        url = post.get("url", "")
        if not keyword or not url:
            continue
        # Only link the first occurrence in paragraph text
        for p_tag in soup.find_all("p"):
            text = p_tag.decode_contents()
            if keyword.lower() in text.lower() and f'href="{url}"' not in text:
                linked = re.sub(
                    re.escape(keyword),
                    f'<a href="{url}">{keyword}</a>',
                    text,
                    count=1,
                    flags=re.IGNORECASE,
                )
                p_tag.clear()
                p_tag.append(BeautifulSoup(linked, "lxml").body or BeautifulSoup(linked, "lxml"))
                break

    return str(soup.body) if soup.body else content


def inject_faq_schema(content: str, keyword: str) -> str:
    """Extract FAQ questions from content and append JSON-LD schema."""
    soup = BeautifulSoup(content, "lxml")
    faqs = []

    # Find FAQ section — look for h2/h3 containing "FAQ" then grab following dt/dd or h3+p pairs
    for tag in soup.find_all(["h2", "h3"]):
        if "faq" in tag.get_text().lower():
            sibling = tag.find_next_sibling()
            while sibling and sibling.name not in ["h2"]:
                if sibling.name == "h3":
                    question = sibling.get_text(strip=True)
                    answer_tag = sibling.find_next_sibling("p")
                    if answer_tag:
                        faqs.append({"question": question, "answer": answer_tag.get_text(strip=True)})
                sibling = sibling.find_next_sibling()
            break

    if not faqs:
        return content

    schema_items = [
        {
            "@type": "Question",
            "name": faq["question"],
            "acceptedAnswer": {"@type": "Answer", "text": faq["answer"]},
        }
        for faq in faqs
    ]
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": schema_items,
    }

    import json
    schema_tag = f'\n<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'
    return content + schema_tag


def clean_html(content: str) -> str:
    """Remove any unwanted tags Claude might add."""
    content = re.sub(r"```html\s*", "", content)
    content = re.sub(r"```\s*", "", content)
    content = content.strip()
    return content
