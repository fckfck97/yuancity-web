from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ChatMessage, Case, ClientCase
@admin.register(ChatMessage)
class ChatMessageAdmin(ModelAdmin):
    list_display = [
        "id",
        "user",
        "text",
        "attachment",
        "is_ai",
        "created_at",
    ]
    search_fields = ["text"]
    list_filter = ["is_ai", "created_at"]
    ordering = ["-created_at"]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
      
@admin.register(Case)
class CaseAdmin(ModelAdmin):
    list_display = [
        "id",
        "client",
        "assigned_lawyer",
        "area",
        "urgency",
        "jurisdiction",
        "summary",
        "success_probability",
        "status",
        "created_at",
        "updated_at"
    ]
    search_fields = ["summary"]
    list_filter = ["status", "created_at", "updated_at"]
    ordering = ["-created_at"]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(client=request.user)
      
@admin.register(ClientCase)
class ClientCaseAdmin(ModelAdmin):
    list_display = [
        "id",
        "name",
        "phone",
        "email",
        "jurisdiction",
        "is_draft",
        "authorized_for_followup",
        "created_at"
    ]
    search_fields = ["name", "phone", "email"]
    list_filter = ["is_draft", "authorized_for_followup", "created_at"]
    ordering = ["-created_at"]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(client=request.user)