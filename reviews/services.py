from __future__ import annotations

import csv
import io
import random
from collections import Counter
from typing import Iterable

from django.conf import settings

try:
    from textblob import TextBlob
except Exception:  # pragma: no cover
    TextBlob = None  # type: ignore

try:
    from nltk.sentiment import SentimentIntensityAnalyzer
except Exception:  # pragma: no cover
    SentimentIntensityAnalyzer = None  # type: ignore

SENTIMENT_LABELS = {'pos': 'positive', 'neu': 'neutral', 'neg': 'negative'}


def detect_sentiment(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        return 'neutral'
    if settings.SENTIMENT_BACKEND == 'nltk' and SentimentIntensityAnalyzer is not None:
        scores = SentimentIntensityAnalyzer().polarity_scores(cleaned)
        return SENTIMENT_LABELS[max(scores, key=scores.get)]
    if TextBlob is not None:
        polarity = TextBlob(cleaned).sentiment.polarity
        if polarity > 0.1:
            return 'positive'
        if polarity < -0.1:
            return 'negative'
        return 'neutral'
    random.seed(len(cleaned))
    return random.choice(['positive', 'neutral', 'negative'])


def parse_csv(content: bytes) -> list[tuple[str, str, str]]:
    reader = csv.DictReader(io.StringIO(content.decode('utf-8', 'ignore')))
    rows: list[tuple[str, str, str]] = []
    for row in reader:
        product = (row.get('product_name') or row.get('product') or 'Без названия').strip()
        review_text = (row.get('content') or row.get('review') or '').strip()
        rating = (row.get('rating') or row.get('score') or '').strip()
        rows.append((product, review_text, rating))
    return rows


def build_sentiment_summary(reviews: Iterable['Review']) -> dict:
    sentiments = Counter(review.sentiment for review in reviews)
    total = sum(sentiments.values()) or 1
    counts = [sentiments.get('positive', 0), sentiments.get('neutral', 0), sentiments.get('negative', 0)]
    percentages = {key: round((sentiments.get(key, 0) / total) * 100, 2) for key in ['positive', 'neutral', 'negative']}
    return {'labels': ['positive', 'neutral', 'negative'], 'counts': counts, 'percentages': percentages}
