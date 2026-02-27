from django.urls import path
from .views import ProductAPIView, ProductListAPIView, ProductHighlightsAPIView, AIProductSearchAPIView

urlpatterns = [
    path('', ProductAPIView.as_view(), name='product-list'),
    path('created/', ProductAPIView.as_view(), name='product-created'),

    path('<int:pk>/', ProductAPIView.as_view(), name='product-detail'),
    path('<uuid:pk>/update/', ProductAPIView.as_view(), name='product-update'),

    path('list/', ProductListAPIView.as_view(), name='product-list-all'),
    path('highlights/', ProductHighlightsAPIView.as_view(), name='product-highlights'),
    path('search/ai/', AIProductSearchAPIView.as_view(), name='product-ai-search'),
]
