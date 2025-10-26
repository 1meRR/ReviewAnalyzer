from __future__ import annotations

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import CSVUploadForm, ReviewForm
from .models import Review
from .services import build_sentiment_summary, detect_sentiment, parse_csv


@login_required
@require_http_methods(['GET', 'POST'])
def dashboard(request: HttpRequest) -> HttpResponse:
    form = ReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.analyzed_by = request.user
        review.sentiment = detect_sentiment(review.content)
        review.save()
        messages.success(request, 'Отзыв сохранён и проанализирован.'); return redirect('dashboard')

    summary = build_sentiment_summary(Review.objects.all()); chart_data = json.dumps({'labels': summary['labels'], 'datasets': [{'label': 'Отзывы', 'data': summary['counts'], 'backgroundColor': ['#16a34a', '#2563eb', '#dc2626']}]} )
    return render(request, 'reviews/dashboard.html', {
        'form': form,
        'recent_reviews': list(Review.objects.all()[:20]),
        'summary': summary,
        'chart_data': chart_data,
        'upload_form': CSVUploadForm(),
    })


@login_required
@require_http_methods(['POST'])
def upload_reviews(request: HttpRequest) -> HttpResponse:
    form = CSVUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, 'Файл не выбран или повреждён.'); return redirect('dashboard')

    rows = parse_csv(form.cleaned_data['file'].read())
    for product_name, content, rating_raw in rows:
        rating = int(rating_raw) if rating_raw.isdigit() else None
        Review.objects.create(
            product_name=product_name or 'Товар',
            content=content,
            rating=rating,
            analyzed_by=request.user,
            source='csv',
            sentiment=detect_sentiment(content),
        )
    messages.success(request, f'Импортировано {len(rows)} отзывов.'); return redirect('dashboard')
