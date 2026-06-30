"""SEO-optimized prompt templates for blog post generation."""


def build_blog_post_prompt(keyword: str, related_keywords: list[str] = None, cluster_context: str = None) -> str:
    related = ", ".join(related_keywords) if related_keywords else keyword
    cluster_hint = f"\n**Topic cluster context:** {cluster_context}" if cluster_context else ""
    return f"""You are a senior SEO content strategist and experienced blogger with 10+ years of hands-on experience.
Write a comprehensive, deeply helpful blog post that demonstrates genuine expertise and first-hand knowledge.

**Target keyword:** {keyword}
**LSI / related keywords to weave in naturally:** {related}{cluster_hint}

## E-E-A-T Requirements (Google's quality signals — critical):
- **Experience**: Include real-world examples, personal observations, or "In practice..." / "Based on testing..." statements
- **Expertise**: Show deep domain knowledge — cite specific data points, statistics, or tool names where relevant
- **Authoritativeness**: Reference well-known sources, standards, or widely accepted best practices
- **Trustworthiness**: Be balanced — acknowledge limitations, tradeoffs, or when something does NOT work

## Content Structure (follow exactly):
1. **Hook introduction** (2-3 paragraphs): Start with a surprising fact, stat, or counter-intuitive insight. State clearly what the reader will learn and why it matters.
2. **H2: What is [topic] / Why it matters** — foundational context
3. **H2: [Main actionable section 1]** with H3 subsections and specific steps
4. **H2: [Main actionable section 2]** with H3 subsections
5. **H2: [Main actionable section 3]** with H3 subsections
6. **H2: Common Mistakes to Avoid** — 3-5 mistakes with brief explanations (readers love this)
7. **H2: Expert Tips** — 3-5 advanced insights that go beyond the basics
8. **H2: Frequently Asked Questions** — 5 questions with direct, helpful answers
9. **Conclusion** — summarize key takeaways + one clear CTA

## Writing Guidelines:
- Length: 2500-3000 words (comprehensive coverage, not padding)
- Tone: Conversational yet authoritative — write like a knowledgeable friend, not a textbook
- Use **bold** for key terms and important concepts
- Include at least 2 specific statistics or data points (you may use plausible, general figures)
- Add at least 1 comparison table or feature list using HTML table or ul/ol
- Break up long text with short paragraphs (2-4 sentences max per paragraph)
- Use transition phrases between sections for flow
- Do NOT keyword-stuff — keyword density should feel natural (target ~1-1.5%)
- Do NOT include the H1 title in the output (it will be added separately)

## Output Format:
Return clean HTML only. Use: h2, h3, p, ul, ol, li, strong, em, table, thead, tbody, tr, th, td.
Start directly with the first <p> tag of the introduction.
Do not include <html>, <head>, <body>, or <h1> tags."""


def build_meta_description_prompt(keyword: str, content_excerpt: str) -> str:
    return f"""Write an SEO-optimized meta description for a blog post about: "{keyword}"

Content excerpt: {content_excerpt[:400]}

Requirements:
- Length: 150-158 characters exactly (count carefully)
- Include the keyword "{keyword}" naturally in the first half
- Lead with a benefit or value proposition (what will the reader gain?)
- End with a soft CTA or compelling hook (e.g., "Learn how", "Discover", "Find out")
- Be specific — avoid vague phrases like "great tips" or "useful information"
- Do not use quotes or special characters

Return only the meta description text, nothing else."""


def build_title_prompt(keyword: str) -> str:
    return f"""Generate 3 SEO-optimized blog post titles for the keyword: "{keyword}"

Requirements:
- Include the keyword naturally (ideally near the start)
- Use proven power words: Ultimate, Complete, Proven, Step-by-Step, Expert, Beginner's, etc.
- Be specific — include a number, year (2026), or outcome where natural
- Length: 55-65 characters (fits Google SERP without truncation)
- Target search intent: informational (how-to, guide, tips) or commercial (best, top, review)
- Format: numbered list, one title per line

Return only the 3 titles, nothing else."""


def build_cluster_titles_prompt(pillar_keyword: str, cluster_keywords: list[str]) -> str:
    kw_list = "\n".join(f"- {kw}" for kw in cluster_keywords)
    return f"""You are an SEO content strategist building a topic cluster.

Pillar page topic: "{pillar_keyword}"

Cluster page keywords:
{kw_list}

For each cluster keyword, write a short internal link anchor text (3-6 words) that would fit naturally
in a sentence linking from the pillar page to that cluster page.

Format your response as a JSON object where keys are the cluster keywords and values are the anchor texts.
Example: {{"keyword one": "anchor text here", "keyword two": "another anchor text"}}

Return only the JSON object, nothing else."""


def build_refresh_prompt(keyword: str, old_content: str, current_year: int = 2026) -> str:
    excerpt = old_content[:800]
    return f"""You are updating an existing blog post to be current, more comprehensive, and better optimized for SEO.

**Keyword:** {keyword}
**Current year:** {current_year}

**Existing content excerpt (first 800 chars):**
{excerpt}

Rewrite and expand this blog post with these improvements:
1. Update any outdated information or statistics to reflect {current_year}
2. Add more depth and specific examples where the original is thin
3. Strengthen the E-E-A-T signals (Experience, Expertise, Authoritativeness, Trust)
4. Add a "Common Mistakes" or "Pro Tips" section if missing
5. Ensure the FAQ section has at least 5 questions
6. Minimum length: 2500 words

Follow the same HTML output format as the original. Do not include <h1> or full page HTML tags."""
