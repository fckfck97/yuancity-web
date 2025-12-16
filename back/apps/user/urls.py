from django.urls import path
from .views import (
    SocialLoginView,
    UserEditView,
    ProfilePictureUploadView,
    OTPLoginRequestView,
    OTPLoginVerifyView,
    OTPLoginRequestWebView,
    ExpoPushTokenView,
    SocialProfileView,
    FollowToggleView,
    FollowersListView,
    FollowingListView,
    DiscoverPeopleView,
    NotificationListView,
    NotificationDetailView,
    NotificationMarkReadView,
    NotificationMarkAllView,
    AccountDeleteView,
)

urlpatterns = [
    path("social/login/", SocialLoginView.as_view(), name="social_login"),
    path('edit/', UserEditView.as_view(), name='user_edit'),
    path("login/otp/request/", OTPLoginRequestView.as_view(),name="otp_login_request"),
    path("login/otp/verify/",  OTPLoginVerifyView.as_view(),name="otp_login_verify"),
    
    path("login/otp/request/web/", OTPLoginRequestWebView.as_view(),name="otp_login_request_web"),
    path('expo/push/token/', ExpoPushTokenView.as_view(), name='expo_push_token'),
    path('profile/picture/', ProfilePictureUploadView.as_view(), name='profile_picture_upload'),
    path('delete/account/<uuid:pk>/', AccountDeleteView.as_view(), name='account_delete'),
    # Social Profile endpoints
    path('social/profile/me/', SocialProfileView.as_view(), name='social_profile_me'),
    path('social/profile/<str:identifier>/', SocialProfileView.as_view(), name='social_profile_public'),
    path('social/follow/', FollowToggleView.as_view(), name='social_follow'),
    path('social/followers/', FollowersListView.as_view(), name='social_followers'),
    path('social/following/', FollowingListView.as_view(), name='social_following'),
    path('social/people/', DiscoverPeopleView.as_view(), name='social_people'),
    path("notifications/", NotificationListView.as_view(), name="notifications-list"),
    path("notifications/mark-all-read/", NotificationMarkAllView.as_view(), name="notifications-mark-all"),
    path("notifications/<int:notification_id>/", NotificationDetailView.as_view(), name="notifications-detail"),
    path("notifications/<int:notification_id>/read/", NotificationMarkReadView.as_view(), name="notifications-read"),
]
