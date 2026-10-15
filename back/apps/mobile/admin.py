from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import MobileAppVersion


@admin.register(MobileAppVersion)
class MobileAppVersionAdmin(ModelAdmin):
    list_display = (
        "platform",
        "latest_version",
        "minimum_supported_version",
        "is_active",
        "updated_at",
    )
    list_filter = ("platform", "is_active")
    search_fields = ("latest_version", "minimum_supported_version", "message")
    ordering = ("-updated_at",)
