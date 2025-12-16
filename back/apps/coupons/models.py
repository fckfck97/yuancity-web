from django.db import models
import uuid

class FixedPriceCoupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    discount_price = models.DecimalField(max_digits=5, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cupón de precio fijo'
        verbose_name_plural = 'Cupones de precio fijo'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name


class PercentageCoupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    discount_percentage = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'Cupón de porcentaje'
        verbose_name_plural = 'Cupones de porcentaje'
        ordering = ['-created_at']
        
    
    def __str__(self):
        return self.name