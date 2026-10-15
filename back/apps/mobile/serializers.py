from rest_framework import serializers

from .models import MobileAppVersion


class MobileAppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileAppVersion
        fields = (
            "id",
            "platform",
            "minimum_supported_version",
            "latest_version",
            "store_url",
            "message",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
