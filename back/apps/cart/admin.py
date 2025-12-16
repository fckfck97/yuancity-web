from .models import Cart, CartItem
from unfold.admin import ModelAdmin
from django.contrib.admin import register
@register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ('user', 'total_items', 'created_at', 'updated_at')
    search_fields = ('user__username',)
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@register(CartItem)
class CartItemAdmin(ModelAdmin):
    list_display = ('cart', 'product', 'count', 'created_at', 'updated_at')
    search_fields = ('cart__user__username', 'product__name')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
