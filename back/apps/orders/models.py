from django.db import models
from apps.product.models import Product
from .countries import Countries
from datetime import datetime
from django.contrib.auth import get_user_model
User = get_user_model()
import uuid

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        not_processed = 'not_processed'
        processed = 'processed'
        shipping = 'shipping'
        delivered = 'delivered'
        cancelled = 'cancelled'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=50, choices=OrderStatus.choices, default=OrderStatus.not_processed)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Cambiado max_digits
    full_name = models.CharField(max_length=255)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255)
    state_province_region = models.CharField(max_length=255)
    postal_zip_code = models.CharField(max_length=20)
    country_region = models.CharField(
        max_length=255, choices=Countries.choices, default=Countries.Colombia)
    telephone_number = models.CharField(max_length=255)
    shipping_name = models.CharField(max_length=255)
    shipping_time = models.CharField(max_length=255)
    shipping_price = models.DecimalField(max_digits=10, decimal_places=2)  # Cambiado max_digits
    date_issued = models.DateTimeField(default=datetime.now)
    buyer_confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)  # Cuando se marcó "en camino"
    completed_at = models.DateTimeField(null=True, blank=True)  # Cuando se marcó "completado"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Ordenes'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.transaction_id


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    count = models.IntegerField()
    platform_fee = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    vendor_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    date_added = models.DateTimeField(default=datetime.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Producto de Orden'
        verbose_name_plural = 'Productos de Orden'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name


def chat_image_upload_path(instance, filename):
    return f"order-chats/images/{instance.order.transaction_id}/{filename}"


def chat_audio_upload_path(instance, filename):
    return f"order-chats/audio/{instance.order.transaction_id}/{filename}"


class OrderChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="chat_messages"
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    image = models.FileField(
        upload_to=chat_image_upload_path, null=True, blank=True
    )
    audio = models.FileField(
        upload_to=chat_audio_upload_path, null=True, blank=True
    )
    audio_duration = models.PositiveIntegerField(null=True, blank=True)
    read = models.BooleanField(default=False)  # Para marcar si el mensaje fue leído
    read_at = models.DateTimeField(null=True, blank=True)  # Cuándo se leyó
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Mensaje {self.id} - {self.order.transaction_id}"
