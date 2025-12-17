# chat/models.py
from django.db import models
from django.conf import settings
from apps.user.models import UserAccount
import uuid
class ChatMessage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="El usuario que envía el mensaje (puede ser None para el AI)"
    )
    text = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_ai = models.BooleanField(default=False, help_text="Marca si el mensaje es del AI")

    def __str__(self):
        return f"{'AI' if self.is_ai else 'User'}: {self.text[:50]} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mensaje de Chat"
        verbose_name_plural = "Mensajes de Chat"
        indexes = [
            models.Index(fields=['created_at']),
        ]
        
class Case(models.Model):
    CASE_STATUS = (
        ('nuevo', 'Nuevo'),
        ('en_revision', 'En Revisión'),
        ('asignado', 'Asignado'),
        ('cerrado', 'Cerrado')
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='client_cases',null=True, blank=True)
    assigned_lawyer = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_cases')
    area = models.CharField(max_length=50)
    urgency = models.CharField(max_length=20)
    jurisdiction = models.CharField(max_length=100)
    summary = models.TextField()
    required_documents = models.JSONField(default=list)
    success_probability = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=CASE_STATUS, default='nuevo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class ClientCase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    desctiption = models.TextField(null=True, blank=True)
    jurisdiction = models.CharField(max_length=100, null=True, blank=True)
    documents = models.JSONField(default=list, null=True, blank=True)
    is_draft = models.BooleanField(default=True)
    authorized_for_followup = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    lawyer = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='lawyer_cases',
        null=True,
        blank=True
    )
    class Meta:

        verbose_name = "Caso del Cliente"
        verbose_name_plural = "Casos de Clientes"