from rest_framework import serializers
from .models import SupportTicket, ChatMessage
from apps.orders.models import Order

class SupportTicketSerializer(serializers.ModelSerializer):
    order = serializers.SlugRelatedField(
        slug_field='transaction_id',
        queryset=Order.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = SupportTicket
        fields = ['id', 'subject', 'message', 'order', 'image', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'message', 'is_from_user', 'timestamp', 'session_id']
