from django.urls import path
from .views import PromotionListAPIView, PromotionDashboardAPIView

urlpatterns = [
    path('', PromotionListAPIView.as_view(), name='promotion-list'),
    path('dashboard/', PromotionDashboardAPIView.as_view(), name='promotion-dashboard'),
    path('dashboard/<uuid:pk>/', PromotionDashboardAPIView.as_view(), name='promotion-dashboard-detail'),
]
