from rest_framework import serializers
from .models import Case, ClientCase

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


class CaseSerializer(serializers.ModelSerializer):
    """Serializa los casos legales generados por el asistente."""

    assigned_lawyer_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = (
            'id',
            'area',
            'urgency',
            'jurisdiction',
            'summary',
            'required_documents',
            'success_probability',
            'status',
            'created_at',
            'updated_at',
            'assigned_lawyer_name',
            'client_name',
        )
        read_only_fields = fields

    def get_assigned_lawyer_name(self, obj):
        lawyer = getattr(obj, 'assigned_lawyer', None)
        return getattr(lawyer, 'full_name', None)

    def get_client_name(self, obj):
        client = getattr(obj, 'client', None)
        return getattr(client, 'full_name', None)
