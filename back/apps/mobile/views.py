from typing import Any, Dict, Optional

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MobileAppVersion
from .serializers import MobileAppVersionSerializer


class MobileAppVersionView(APIView):
    """
    GET  /api/mobile/version/ -> Returns latest config per platform for the mobile app.
    POST /api/mobile/version/ -> Creates a new config (admin only) and archives older ones.
    """

    serializer_class = MobileAppVersionSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]

    @staticmethod
    def _serialize_version(
        version: Optional[MobileAppVersion],
    ) -> Optional[Dict[str, Any]]:
        if not version:
            return None
        return {
            "minimumSupportedVersion": version.minimum_supported_version or None,
            "latestVersion": version.latest_version,
            "storeUrl": version.store_url or None,
            "message": version.message or None,
        }

    def get(self, request, *args, **kwargs):
        ios_version = (
            MobileAppVersion.objects.active()
            .for_platform(MobileAppVersion.Platforms.IOS)
            .order_by("-created_at")
            .first()
        )
        android_version = (
            MobileAppVersion.objects.active()
            .for_platform(MobileAppVersion.Platforms.ANDROID)
            .order_by("-created_at")
            .first()
        )

        latest_timestamp = None
        for candidate in (ios_version, android_version):
            if candidate and (
                not latest_timestamp or candidate.updated_at > latest_timestamp
            ):
                latest_timestamp = candidate.updated_at

        payload = {
            "ios": self._serialize_version(ios_version),
            "android": self._serialize_version(android_version),
            "message": None,
            "updatedAt": latest_timestamp.isoformat() if latest_timestamp else None,
        }

        if not payload["ios"] and not payload["android"]:
            return Response(payload, status=status.HTTP_200_OK)
        # Allow a shared message fallback reusing the newest available one.
        most_recent = ios_version
        if (
            android_version
            and (
                not most_recent
                or android_version.updated_at > most_recent.updated_at
            )
        ):
            most_recent = android_version
        payload["message"] = most_recent.message if most_recent else None
        return Response(payload, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = self.serializer_class(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
