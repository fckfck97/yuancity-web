from rest_framework import serializers
from .models import SupportTicket, ChatMessage, SupportTicketImage
from apps.orders.models import Order

class SupportTicketImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicketImage
        fields = ['id', 'image']

class SupportTicketSerializer(serializers.ModelSerializer):
    order = serializers.SlugRelatedField(
        slug_field='transaction_id',
        queryset=Order.objects.all(),
        required=False,
        allow_null=True
    )
    images = SupportTicketImageSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    order_id = serializers.CharField(source='order.transaction_id', read_only=True, allow_null=True)

    class Meta:
        model = SupportTicket
        fields = ['id', 'subject', 'message', 'order', 'order_id', 'status', 'created_at', 'updated_at', 'images', 'user_email', 'user_name']
        read_only_fields = ['status', 'created_at', 'updated_at', 'user_email', 'user_name', 'order_id']

    def create(self, validated_data):
        ticket = super().create(validated_data)
        request = self.context.get('request')

        if request:
            # Check for single 'image' (legacy/simple) - though we removed the field from model, 
            # if we didn't remove it in DB, we could still use it. 
            # But here we are using the new model.
            
            # Check for 'media_count' pattern
            media_count = int(request.data.get('media_count', 0))
            if media_count > 0:
                for i in range(media_count):
                    image_file = request.FILES.get(f'media_{i}')
                    if image_file:
                        SupportTicketImage.objects.create(ticket=ticket, image=image_file)
            
            # Fallback for single 'image' in FormData (if frontend sends it that way)
            elif 'image' in request.FILES:
                 SupportTicketImage.objects.create(ticket=ticket, image=request.FILES['image'])
        
        return ticket

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'message', 'is_from_user', 'timestamp', 'session_id']
        read_only_fields = ['id', 'timestamp', 'is_from_user', 'session_id']

