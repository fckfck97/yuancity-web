from datetime import datetime
from apps.product.models import Product
from apps.orders.models import OrderItem
from django.db import models

from django.conf import settings
from django.db.models import JSONField
User = settings.AUTH_USER_MODEL
import uuid

class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    comment = models.TextField()
    date_created = models.DateTimeField(default=datetime.now)
    date_updated = models.DateTimeField(auto_now=True)
    order_item = models.OneToOneField(
        OrderItem,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="review"
    )
    extra_feedback = JSONField(default=list, blank=True)
    
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-date_created']
    def __str__(self):
        return self.comment
