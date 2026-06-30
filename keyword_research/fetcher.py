"""
Fetch related questions for a keyword using free sources:
- AnswerThePublic (scrape)
- AlsoAsked (scrape)
- Google autocomplete (free API)
"""

import requests
import json
from typing import List
from rich.console import Console

console = Console()


def get_google_autocomplete(keyword: str) -> List[str]:
    """Fetch suggestions from Google autocomplete."""
    prefixes = ["how to", "what is", "why does", "when should", "which", "where to", "can i"]
    questions = []

    for prefix in prefixes:
        query = f"{prefix} {keyword}"
        url = "https://suggestqueries.google.com/complete/search"
        params = {"client": "firefox", "q": query, "hl": "en"}
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                suggestions = resp.json()[1]
                questions.extend(suggestions)
        except Exception:
            pass

    return list(set(questions))


def get_questions_from_csv(filepath: str) -> List[dict]:
    """Load pre-researched keywords from CSV file."""
    import pandas as pd
    df = pd.read_csv(filepath)
    required_cols = {"keyword", "volume", "difficulty"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must have columns: {required_cols}")
    return df.to_dict("records")


def suggest_questions(keyword: str) -> List[str]:
    """Main entry point: get question suggestions for a keyword."""
    console.print(f"[cyan]Fetching questions for:[/cyan] {keyword}")
    questions = get_google_autocomplete(keyword)
    # Filter to only question-style queries
    question_words = ("how", "what", "why", "when", "which", "where", "can", "should", "is", "are", "does")
    filtered = [q for q in questions if q.lower().startswith(question_words)]
    console.print(f"[green]Found {len(filtered)} questions[/green]")
    return filtered
