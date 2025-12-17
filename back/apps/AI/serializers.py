from rest_framework import serializers
from .models import ClientCase

class ClientCaseSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo ClientCase.
    """
    class Meta:
        model = ClientCase
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'jurisdiction': {'required': False},
            'documents': {'required': False},
            'is_draft': {'required': False},
            'authorized_for_followup': {'required': False},
        }
        depth = 1