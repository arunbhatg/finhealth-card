"""Optional NewsAPI.org integration — requires NEWS_API_KEY."""

from __future__ import annotations

import logging
import os
import re

import requests

logger = logging.getLogger(__name__)

NEWS_API_URL = "https://newsapi.org/v2/everything"

_POSITIVE = re.compile(
    r"\b(growth|expansion|profit|award|partnership|launch|record|boost|wins?|success)\b",
    re.I,
)
_NEGATIVE = re.compile(
    r"\b(fraud|default|litigation|lawsuit|insolvency|penalty|raid|arrest|loss|decline|shutdown)\b",
    re.I,
)


def _sentiment_from_text(text: str) -> str:
    if _NEGATIVE.search(text):
        return "negative"
    if _POSITIVE.search(text):
        return "positive"
    return "neutral"


def fetch_business_news(business_name: str, sector: str) -> dict | None:
    api_key = os.getenv("NEWS_API_KEY") or os.getenv("STREAMLIT_NEWS_API_KEY")
    if not api_key:
        return None

    query = f'"{business_name}" OR {sector} India MSME'
    try:
        resp = requests.get(
            NEWS_API_URL,
            params={
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 12,
                "apiKey": api_key,
            },
            timeout=12,
        )
        resp.raise_for_status()
        raw = resp.json().get("articles", [])
        articles = []
        for item in raw[:10]:
            title = item.get("title") or ""
            if not title or title == "[Removed]":
                continue
            desc = item.get("description") or ""
            sentiment = _sentiment_from_text(f"{title} {desc}")
            published = item.get("publishedAt", "")[:10]
            articles.append({
                "title": title[:160],
                "sentiment": sentiment,
                "source": (item.get("source") or {}).get("name", "News"),
                "published_at": published,
                "published_days_ago": 7,
                "url": item.get("url", ""),
            })

        if not articles:
            return None

        pos = sum(1 for a in articles if a["sentiment"] == "positive")
        neg = sum(1 for a in articles if a["sentiment"] == "negative")
        return {
            "live": True,
            "source": "newsapi.org",
            "articles": articles,
            "positive_count_30d": pos,
            "negative_count_30d": neg,
            "neutral_count_30d": len(articles) - pos - neg,
        }
    except Exception as exc:
        logger.warning("News API fetch failed: %s", exc)
        return None


def mock_business_news(profile: dict) -> dict:
    """Synthetic recent news aligned to borrower persona."""
    name = profile["business_name"]
    sector = profile["sector"]
    courts = profile.get("courts", {})
    litigation = (
        courts.get("civil_cases", 0)
        + courts.get("criminal_cases", 0)
        + courts.get("insolvency_petitions", 0)
    )
    persona = profile.get("persona", "")

    if litigation >= 2 or persona == "distressed":
        articles = [
            {
                "title": f"{name} faces supplier payment dispute in {profile['city']}",
                "sentiment": "negative",
                "source": "Business Standard",
                "published_days_ago": 4,
            },
            {
                "title": f"GST scrutiny intensifies for {sector.lower()} traders in region",
                "sentiment": "negative",
                "source": "Economic Times",
                "published_days_ago": 11,
            },
            {
                "title": f"{name} expands warehouse capacity amid sector recovery",
                "sentiment": "positive",
                "source": "Mint",
                "published_days_ago": 18,
            },
        ]
    elif persona in ("healthy_manufacturer", "retail_strong") or litigation == 0:
        articles = [
            {
                "title": f"{name} reports steady order book growth in Q1",
                "sentiment": "positive",
                "source": "Mint",
                "published_days_ago": 3,
            },
            {
                "title": f"{sector} MSMEs see digital collections surge via UPI",
                "sentiment": "positive",
                "source": "Financial Express",
                "published_days_ago": 9,
            },
            {
                "title": f"RBI MSME outreach programme benefits {profile['state']} units",
                "sentiment": "neutral",
                "source": "RBI Bulletin",
                "published_days_ago": 14,
            },
            {
                "title": f"{name} recognised among top local suppliers",
                "sentiment": "positive",
                "source": "Local Herald",
                "published_days_ago": 21,
            },
        ]
    else:
        articles = [
            {
                "title": f"{name} maintains operations despite sector headwinds",
                "sentiment": "neutral",
                "source": "Trade India",
                "published_days_ago": 6,
            },
            {
                "title": f"Monsoon outlook supportive for {sector.lower()} demand",
                "sentiment": "positive",
                "source": "Agri News",
                "published_days_ago": 12,
            },
        ]

    pos = sum(1 for a in articles if a["sentiment"] == "positive")
    neg = sum(1 for a in articles if a["sentiment"] == "negative")
    return {
        "live": False,
        "source": "synthetic",
        "articles": articles,
        "positive_count_30d": pos,
        "negative_count_30d": neg,
        "neutral_count_30d": len(articles) - pos - neg,
    }
