from django.urls import path
from .views import PageViewCountView,NewsLetterView
urlpatterns = [
		path('page-views/', PageViewCountView.as_view(), name='page-view-count'),
    path('newsletter/', NewsLetterView.as_view(), name='newsletter'),
]