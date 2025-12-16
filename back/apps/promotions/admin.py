from django.contrib import admin

from .models import Promotion
from unfold.admin import ModelAdmin


@admin.register(Promotion)
class PromotionAdmin(ModelAdmin):
    list_display = ["title", "vendor", "start_date", "end_date", "is_active"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "slug"]
    list_filter = ["is_active", "start_date", "end_date"]
    autocomplete_fields = ["vendor", "products"]
