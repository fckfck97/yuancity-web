# chat/urls.py
from django.urls import path
from .views import (
    CaseDetailView,
    CaseListView,
    ChatAPIView,
    ClientCaseAPIView,
    FreeCaseChatAPIView,
)

urlpatterns = [
    path('chat/', ChatAPIView.as_view(), name='chat-api'),
    path('cases/', CaseListView.as_view(), name='case-list-api'),
    path('cases/<uuid:pk>/', CaseDetailView.as_view(), name='case-detail-api'),
    path('free_case/', FreeCaseChatAPIView.as_view(), name='free-case-chat-api'),
    path('client_case/', ClientCaseAPIView.as_view(), name='client-case-api'),
]
