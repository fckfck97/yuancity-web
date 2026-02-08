# chat/urls.py
from django.urls import path
from .views import (
    CaseDetailView,
    CaseListView,
    LegalChatAPIView,
    ProductDraftChatAPIView,
)

urlpatterns = [
    path('AI/chat/', LegalChatAPIView.as_view(), name='chat-api'),
    path('AI/cases/', CaseListView.as_view(), name='case-list-api'),
    path('AI/cases/<uuid:pk>/', CaseDetailView.as_view(), name='case-detail-api'),
    path('assistant/product-draft/chat/', ProductDraftChatAPIView.as_view(), name='product-draft-chat-api'),
]
