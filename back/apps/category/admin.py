from django.contrib import admin
from .models import Category
from unfold.admin import ModelAdmin

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('id','name', 'parent')
    list_display_links = ('id','name', 'parent')
    search_fields = ('name', 'parent')
    list_per_page = 25
