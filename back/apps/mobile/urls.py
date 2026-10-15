from django.urls import path

from .views import MobileAppVersionView

urlpatterns = [
    path("version/", MobileAppVersionView.as_view(), name="mobile-app-version"),
]
