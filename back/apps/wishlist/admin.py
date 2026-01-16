from django.contrib import admin

from .models import WishList
from unfold.admin import ModelAdmin
@admin.register(WishList)
class WishListAdmin(ModelAdmin):
    list_display = ('user', 'total_items', 'created_at', 'updated_at')
    search_fields = ('user__last_name',)
    list_filter = ('created_at', 'updated_at')
