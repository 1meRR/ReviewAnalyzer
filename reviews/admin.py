from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'author', 'sentiment', 'rating', 'source', 'created_at')
    list_filter = ('sentiment', 'source', 'created_at')
    search_fields = ('product_name', 'author', 'content')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('analyzed_by',)
