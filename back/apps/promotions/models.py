# promotions/models.py
import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from apps.product.models import Product

class Promotion(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='promotions',
        null=True,
        blank=True
    )
    title       = models.CharField(max_length=120)
    description = models.CharField(max_length=150, blank=True, null=True)
    slug        = models.SlugField(max_length=120, unique=True, blank=True)
    banner      = models.ImageField(upload_to='promotions/banners/')
    start_date  = models.DateField(null=True, blank=True)
    end_date    = models.DateField(null=True, blank=True)
    is_active   = models.BooleanField(default=True)
    products    = models.ManyToManyField(Product, related_name='promotions'
                                         )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-start_date"]
