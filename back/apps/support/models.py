from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.orders.models import Order

def ticket_image_upload_path(instance, filename):
    if hasattr(instance, 'ticket'):
        user_id = instance.ticket.user.id
    else:
        user_id = instance.user.id
    return f"support/tickets/{user_id}/{filename}"

class SupportTicket(models.Model):
    STATUS_CHOICES = (
        ('open', _('Abierto')),
        ('in_progress', _('En Progreso')),
        ('closed', _('Cerrado')),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='support_tickets')
    image = models.ImageField(upload_to=ticket_image_upload_path, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Support Ticket')
        verbose_name_plural = _('Support Tickets')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.user.email}"

class SupportTicketImage(models.Model):
    ticket = models.ForeignKey(SupportTicket, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=ticket_image_upload_path)
    
    class Meta:
        verbose_name = _('Support Ticket Image')
        verbose_name_plural = _('Support Ticket Images')

    def __str__(self):
        return f"Image for ticket {self.ticket.id}"

class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    is_from_user = models.BooleanField(default=True) # True if from user, False if from AI
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True, null=True) 

    class Meta:
        verbose_name = _('Chat Message')
        verbose_name_plural = _('Chat Messages')
        ordering = ['timestamp']

    def __str__(self):
        sender = "User" if self.is_from_user else "AI"
        return f"{sender}: {self.message[:50]}..."
