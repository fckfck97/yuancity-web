from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views_account import (
    AccountDeletionConfirmView,
    AccountDeletionRequestView,
    AccountDeletionStatusView,
    DeleteMyAccountView,
    LogoutView,
)
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
    N8NUserStageListView,
    N8NUserAdvanceView,
    UnsubscribeView,
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
    # Sesión
    path("auth/logout/", LogoutView.as_view(), name="auth_logout"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth_refresh"),
    # Alias: las versiones publicadas de la app renuevan aquí (services/api.ts).
    path("auth/jwt/refresh/", TokenRefreshView.as_view(), name="auth_jwt_refresh_legacy"),
    # Eliminación de cuenta desde la app
    path("users/me/", DeleteMyAccountView.as_view(), name="user_delete_me"),
    path("users/me/deletion/", AccountDeletionStatusView.as_view(), name="user_deletion_status"),
    # Eliminación de cuenta desde la web, sin sesión: código por correo + confirmación
    path("account/deletion/request/", AccountDeletionRequestView.as_view(), name="account_deletion_request"),
    path("account/deletion/confirm/", AccountDeletionConfirmView.as_view(), name="account_deletion_confirm"),
        # N8N Endpoints
    path('n8n/users/', N8NUserStageListView.as_view(), name='n8n_users'),
    path('n8n/users/<uuid:pk>/advance/', N8NUserAdvanceView.as_view(), name='n8n_user_advance'),
        # Unsubscribe
    path('unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'),
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
