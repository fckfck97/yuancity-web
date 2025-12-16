from django.contrib import admin
from .models import Order, OrderItem
from unfold.admin import ModelAdmin

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    
    list_display = ('id', 'transaction_id', 'amount', 'status', )
    list_display_links = ('id', 'transaction_id', )
    list_filter = ('status', )
    list_editable = ('status', )
    list_per_page = 25

@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):

    list_display = ('id', 'name', 'price', 'count', )
    list_display_links = ('id', 'name', )
    list_per_page = 25
    