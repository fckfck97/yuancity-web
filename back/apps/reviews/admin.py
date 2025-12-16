from django.contrib import admin
from .models import Review
from unfold.admin import ModelAdmin

@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ('id', 'rating', 'comment', )
    list_display_links = ('id', 'rating', 'comment', )
    list_filter = ('rating', )
    search_fields = ('comment', )
    list_per_page = 25

