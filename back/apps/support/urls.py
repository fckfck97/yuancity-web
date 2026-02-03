from django.urls import path
from .views import SupportTicketCreateView, chat_with_assistant, get_chat_history

urlpatterns = [
    path('ticket/create/', SupportTicketCreateView.as_view(), name='create-ticket'),
    path('chat/', chat_with_assistant, name='chat-assistant'),
    path('chat/history/', get_chat_history, name='chat-history'),
]
