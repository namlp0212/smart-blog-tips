"""Filter and score keywords by SEO potential."""

from typing import List, Dict


def score_keyword(keyword: str, volume: int = 0, difficulty: int = 100) -> float:
    """Score keyword: higher volume + lower difficulty = better score."""
    if difficulty == 0:
        difficulty = 1
    return (volume / difficulty) * 10


def filter_keywords(keywords: List[Dict], max_difficulty: int = 30, min_volume: int = 100) -> List[Dict]:
    """Filter keyword list by difficulty and volume thresholds."""
    filtered = [
        kw for kw in keywords
        if kw.get("difficulty", 100) <= max_difficulty
        and kw.get("volume", 0) >= min_volume
    ]
    return sorted(filtered, key=lambda x: score_keyword(
        x["keyword"], x.get("volume", 0), x.get("difficulty", 100)
    ), reverse=True)


def deduplicate(questions: List[str]) -> List[str]:
    """Remove duplicate or near-duplicate questions."""
    seen = set()
    result = []
    for q in questions:
        normalized = q.lower().strip().rstrip("?")
        if normalized not in seen:
            seen.add(normalized)
            result.append(q)
    return result
