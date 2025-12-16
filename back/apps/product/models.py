# products/models.py

import uuid
import os
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from apps.category.models import Category


def product_image_path(instance, filename):
    """
    Retorna la ruta: users/{vendor_id}/products/{product_id}/images/{filename}
    """
    ext = os.path.splitext(filename)[1]
    timestamp = uuid.uuid4().hex[:8]
    new_filename = f"img_{timestamp}{ext}"
    return f"users/{instance.product.vendor.id}/products/{instance.product.id}/images/{new_filename}"
class Product(models.Model):
    """
    A product sold by a vendor.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Seller"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name="Sub-category"
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveSmallIntegerField(
        default=0,
        help_text="Discount percentage (0–100). E.g. 10 means 10% off."
    )
    currency = models.CharField(
        max_length=3,
        default='COP',
        help_text="ISO 4217 currency code (e.g., 'COP' for Colombian Pesos)"
    )

    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)


    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            # ensure unique slug
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)




class ProductImage(models.Model):
    """
    Multiple images per product.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to=product_image_path, max_length=500)
    alt_text = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveSmallIntegerField(default=0,
                                                     help_text="Defines ordering of images")
    is_primary = models.BooleanField(default=False, help_text="Primary image for product preview")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'display_order', 'uploaded_at']

    def __str__(self):
        return f"Image for {self.product.name} (order {self.display_order})"


# Señales para limpiar archivos huérfanos
@receiver(post_delete, sender=ProductImage)
def delete_product_image_file(sender, instance, **kwargs):
    """
    Elimina el archivo de imagen cuando se borra la instancia de ProductImage.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(pre_save, sender=ProductImage)
def delete_old_product_image_on_update(sender, instance, **kwargs):
    """
    Elimina la imagen antigua cuando se actualiza.
    """
    if not instance.pk:
        return
    
    try:
        old_image = ProductImage.objects.get(pk=instance.pk)
    except ProductImage.DoesNotExist:
        return
    
    if old_image.image and old_image.image != instance.image:
        if os.path.isfile(old_image.image.path):
            os.remove(old_image.image.path)
