from django.contrib import admin
from .models import FixedPriceCoupon, PercentageCoupon
from unfold.admin import ModelAdmin

@admin.register(FixedPriceCoupon)
class FixedPriceCouponAdmin(ModelAdmin):
    list_display = ('id', 'name', 'discount_price', )
    list_display_links = ('name', )
    list_editable = ('discount_price', )
    search_fields = ('name', )
    list_per_page = 25

@admin.register(PercentageCoupon)
class PercentageCouponAdmin(ModelAdmin):
    list_display = ('id', 'name', 'discount_percentage', )
    list_display_links = ('name', )
    list_editable = ('discount_percentage', )
    search_fields = ('name', )
    list_per_page = 25
