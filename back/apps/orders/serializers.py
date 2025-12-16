from rest_framework import serializers
from django.conf import settings
from urllib.parse import urljoin

from .models import Order, OrderItem, OrderChatMessage

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField() 

    class Meta:
        model = Order
        fields = '__all__'

    def get_items(self, obj):

        items = OrderItem.objects.filter(order=obj)
        return OrderItemSerializer(items, many=True).data


class OrderChatMessageSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source="message", read_only=True)
    image_url = serializers.SerializerMethodField()
    audio_url = serializers.SerializerMethodField()
    sender_id = serializers.SerializerMethodField()
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = OrderChatMessage
        fields = (
            "id",
            "text",
            "image_url",
            "audio_url",
            "audio_duration",
            "sender_id",
            "sender_name",
            "created_at",
        )

    def _build_absolute_uri(self, file_field):
        if not file_field:
            return None
        request = self.context.get("request")
        url = file_field.url
        if request:
            return request.build_absolute_uri(url)
        base = getattr(settings, "SITE_URL", "")
        return urljoin(base, url)

    def get_image_url(self, obj):
        return self._build_absolute_uri(obj.image)

    def get_audio_url(self, obj):
        return self._build_absolute_uri(obj.audio)

    def get_sender_id(self, obj):
        return obj.sender_id

    def get_sender_name(self, obj):
        full_name = obj.sender.full_name
        return full_name.strip() or obj.sender.email or obj.sender.username
