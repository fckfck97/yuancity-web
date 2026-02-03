from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import SupportTicket, ChatMessage

@admin.register(SupportTicket)
class SupportTicketAdmin(ModelAdmin):
    list_display = ('subject', 'user', 'status', 'order', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'user__email', 'message', 'order__transaction_id')

@admin.register(ChatMessage)
class ChatMessageAdmin(ModelAdmin):
    list_display = ('user', 'message_preview', 'is_from_user', 'timestamp')
    search_fields = ('user__email', 'message')
    list_filter = ('is_from_user', 'timestamp')

    def message_preview(self, obj):
        return obj.message[:50]
