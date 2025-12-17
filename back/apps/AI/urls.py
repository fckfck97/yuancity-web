# chat/urls.py
from django.urls import path
from .views import ChatAPIView,FreeCaseChatAPIView,ClientCaseAPIView

urlpatterns = [
    path('chat/', ChatAPIView.as_view(), name='chat-api'),
    path('free_case/', FreeCaseChatAPIView.as_view(), name='free-case-chat-api'),
    path('client_case/', ClientCaseAPIView.as_view(), name='client-case-api'),
]
