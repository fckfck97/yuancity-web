from django.urls import path
from .views import (
    ListOrdersView,
    ListOrderDetailView,
    OrderView,
    VendorOrdersView,
    VendorOrderStatusView,
    ConfirmDeliveryView,
    OrderChatView,
    MarkChatMessagesReadView,
)

app_name="orders"

urlpatterns = [
    path('order/list', ListOrdersView.as_view()),
    path('order/<uuid:pk>/', ListOrderDetailView.as_view()),
    path('order/update/<uuid:pk>/', OrderView.as_view()),
    path('get-orders', ListOrdersView.as_view()),
    path('get-order/<transactionId>', ListOrderDetailView.as_view()),
    path('confirm-delivery/<transactionId>/', ConfirmDeliveryView.as_view()),
    path('chat/<str:transaction_id>/', OrderChatView.as_view()),
    path('chat/<str:transaction_id>/mark-read/', MarkChatMessagesReadView.as_view()),
    path('vendor/orders', VendorOrdersView.as_view()),
    path('vendor/orders/<uuid:pk>/status', VendorOrderStatusView.as_view()),
]
