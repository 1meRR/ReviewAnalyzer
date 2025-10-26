from __future__ import annotations

from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['product_name', 'author', 'content', 'rating']


class CSVUploadForm(forms.Form):
    file = forms.FileField()
