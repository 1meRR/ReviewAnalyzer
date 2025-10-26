from __future__ import annotations

from django.conf import settings
from django.db import models

from reviews import services


class Review(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Позитивный'),
        ('neutral', 'Нейтральный'),
        ('negative', 'Негативный'),
    ]

    product_name = models.CharField(max_length=255)
    author = models.CharField(max_length=120, blank=True)
    content = models.TextField()
    rating = models.IntegerField(null=True, blank=True)
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='neutral')
    source = models.CharField(max_length=50, default='manual')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    analyzed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='analyzed_reviews',
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.product_name}: {self.sentiment}"

    def analyze(self, *, save: bool = True) -> str:
        sentiment = services.detect_sentiment(self.content)
        self.sentiment = sentiment
        if save:
            self.save(update_fields=['sentiment', 'updated_at'])
        return sentiment

    @property
    def short_content(self) -> str:
        limit = 120
        if len(self.content) <= limit:
            return self.content
        return self.content[:limit] + '...'
