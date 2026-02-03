from django.urls import path
from .views import SupportTicketCreateView, chat_with_assistant, get_chat_history, AdminTicketListView

urlpatterns = [
    path('ticket/create/', SupportTicketCreateView.as_view(), name='create-ticket'),
    path('admin/tickets/', AdminTicketListView.as_view(), name='admin-tickets'),
    path('chat/', chat_with_assistant, name='chat-assistant'),
    path('chat/history/', get_chat_history, name='chat-history'),
]
