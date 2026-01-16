from apps.product.models import Product
from django.db import models
import uuid
from django.conf import settings
User = settings.AUTH_USER_MODEL


class WishList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_items = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Wish List'
        verbose_name_plural = 'Wish Lists'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.user.last_name


class WishListItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wishlist = models.ForeignKey(WishList, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Wish List Item'
        verbose_name_plural = 'Wish List Items'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.product.name