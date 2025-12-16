# apps/product/admin.py

from django.contrib import admin
from .models import Product, ProductImage
from unfold.admin import ModelAdmin

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = (
        'image',
        'alt_text',
        'display_order',
        'uploaded_at',
    )
    readonly_fields = ('uploaded_at',)
    ordering = ('display_order', 'uploaded_at')


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    inlines = [ProductImageInline]

    list_display = (
        'name',
        'vendor',
        'category',
        'price',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'vendor',
        'category',
        'is_available',
    )
    search_fields = (
        'name',
        'vendor__email',
    )
    ordering = ('-created_at',)
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'description',
                'price',
                'currency',
                'stock',
                'is_available',
                'category',
                'discount_percent'
            )
        }),
        ('Vendor', {
            'fields': ('vendor',),
        }),
        ('Important dates', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser:
            # Para usuarios no superuser, excluir el fieldset de Vendor
            fieldsets = [fs for fs in fieldsets if fs[0] != 'Vendor']
        return fieldsets

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(vendor=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.vendor = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        # impide cambiar el vendor si no es superuser
        if request.user.is_superuser:
            return super().get_readonly_fields(request, obj)
        return ('created_at', 'updated_at', 'vendor')


@admin.register(ProductImage)
class ProductImageAdmin(ModelAdmin):
    list_display = (
        'product',
        'display_order',
        'uploaded_at',
    )
    search_fields = ('product__name',)
    ordering = ('display_order', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

    fieldsets = (
        (None, {
            'fields': (
                'product',
                'image',
                'alt_text',
                'display_order',
            )
        }),
        ('Important dates', {
            'fields': ('uploaded_at',),
        }),
    )
