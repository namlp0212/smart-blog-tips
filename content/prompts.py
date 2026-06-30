"""SEO-optimized prompt templates for blog post generation."""


def build_blog_post_prompt(keyword: str, related_keywords: list[str] = None) -> str:
    related = ", ".join(related_keywords) if related_keywords else keyword
    return f"""You are an expert SEO content writer. Write a comprehensive, helpful blog post that answers the following question:

**Target keyword:** {keyword}
**Related keywords to naturally include:** {related}

Requirements:
- Length: 1500-2000 words
- Structure: Use H2 and H3 headings
- Tone: Helpful, clear, authoritative (E-E-A-T principles)
- Include a FAQ section at the end with 3-5 common questions and answers
- Include a clear introduction that hooks the reader
- Include actionable tips and steps where applicable
- Include a conclusion with a call-to-action
- Write naturally — do NOT keyword-stuff
- Do NOT include the title in the output (it will be added separately)

Output format: Return clean HTML with proper tags (h2, h3, p, ul, ol, strong, em).
Start directly with the first paragraph. Do not include <html>, <head>, or <body> tags."""


def build_meta_description_prompt(keyword: str, content_excerpt: str) -> str:
    return f"""Write an SEO meta description for a blog post about: "{keyword}"

Content excerpt: {content_excerpt[:300]}

Requirements:
- Length: 150-160 characters exactly
- Include the keyword naturally
- Be compelling and encourage clicks
- Do not use quotes

Return only the meta description text, nothing else."""


def build_title_prompt(keyword: str) -> str:
    return f"""Generate 3 SEO-optimized blog post titles for the keyword: "{keyword}"

Requirements:
- Include the keyword naturally
- Use power words (Ultimate, Complete, Best, How to, etc.)
- Be specific and clear
- Length: 50-65 characters
- Format: numbered list

Return only the 3 titles, one per line."""
