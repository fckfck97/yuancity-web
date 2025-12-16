from django.urls import path

from .views import ListCategoriesView, CategoriesView

urlpatterns = [
    path('categories', ListCategoriesView.as_view()),
    path('categories/list/', CategoriesView.as_view()),
    path('categories/<uuid:pk>/', CategoriesView.as_view()),
    path('categories/create/', CategoriesView.as_view()),
    path('categories/update/<uuid:pk>/', CategoriesView.as_view()),

]