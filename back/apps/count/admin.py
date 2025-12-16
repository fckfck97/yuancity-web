from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import PageView,NewsLetter
from import_export.admin import ImportExportModelAdmin
@admin.register(PageView)
class PageViewAdmin(ModelAdmin,ImportExportModelAdmin):
    list_display = ('ip_address', 'user_agent', 'country', 'city', 'latitude', 'longitude', 'created_at')
    search_fields = ('ip_address', 'user_agent', 'country', 'city')
    list_filter = ('country', 'city')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
@admin.register(NewsLetter)
class NewsLetterAdmin(ModelAdmin,ImportExportModelAdmin):
    list_display = ('email', 'created_at')
    search_fields = ('email',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)