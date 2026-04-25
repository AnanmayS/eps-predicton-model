from __future__ import annotations

from collections.abc import Iterable
import math
import re

POSITIVE_TERMS = {
    "beat",
    "beats",
    "strong",
    "upside",
    "growth",
    "gain",
    "gains",
    "bullish",
    "optimistic",
    "momentum",
    "record",
    "expands",
    "outperform",
    "improves",
    "surge",
    "surges",
}

NEGATIVE_TERMS = {
    "miss",
    "misses",
    "weak",
    "downside",
    "decline",
    "drops",
    "drop",
    "bearish",
    "cautious",
    "slowdown",
    "risk",
    "cuts",
    "cut",
    "warning",
    "pressure",
    "pressured",
    "fall",
    "falls",
}


def score_headlines(headlines: Iterable[str]) -> float:
    total_score = 0.0
    total_terms = 0

    for headline in headlines:
        words = re.findall(r"[a-zA-Z']+", headline.lower())
        if not words:
            continue
        total_terms += len(words)
        for word in words:
            if word in POSITIVE_TERMS:
                total_score += 1.0
            elif word in NEGATIVE_TERMS:
                total_score -= 1.0

    if total_terms == 0:
        return 0.0

    normalized = total_score / math.sqrt(total_terms)
    return max(-1.0, min(1.0, normalized))


def build_synthetic_headlines(ticker: str, sentiment_signal: float) -> list[str]:
    if sentiment_signal >= 0.2:
        return [
            f"{ticker} sees strong demand ahead of earnings",
            f"Analysts turn bullish on {ticker} growth momentum",
            f"{ticker} outlook improves after upbeat channel checks",
        ]
    if sentiment_signal <= -0.2:
        return [
            f"{ticker} faces pressure as analysts grow cautious",
            f"Weaker demand raises downside risk for {ticker}",
            f"{ticker} sentiment softens before earnings report",
        ]
    return [
        f"Investors weigh mixed signals ahead of {ticker} earnings",
        f"{ticker} outlook remains balanced into the next quarter",
        f"Analysts keep a neutral view on {ticker} before results",
    ]
