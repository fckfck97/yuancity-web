from django.db import models


class MobileAppVersionQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def for_platform(self, platform: str):
        return self.filter(platform=platform)


class MobileAppVersion(models.Model):
    class Platforms(models.TextChoices):
        IOS = "ios", "iOS"
        ANDROID = "android", "Android"

    platform = models.CharField(
        max_length=20,
        choices=Platforms.choices,
        help_text="Platform the version applies to.",
    )
    minimum_supported_version = models.CharField(
        max_length=32,
        blank=True,
        help_text="Lowest version allowed before forcing an update.",
    )
    latest_version = models.CharField(
        max_length=32,
        help_text="Latest version shown to users as available.",
    )
    store_url = models.URLField(
        blank=True,
        help_text="Optional override for the store URL that should be opened.",
    )
    message = models.TextField(
        blank=True,
        help_text="Optional message shown to users alongside the update prompt.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive configs are ignored when serving version metadata.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MobileAppVersionQuerySet.as_manager()

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Versión de la app móvil"
        verbose_name_plural = "Versiones de la app móvil"

    def __str__(self) -> str:
        return f"{self.get_platform_display()} v{self.latest_version}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_active:
            (
                MobileAppVersion.objects.for_platform(self.platform)
                .exclude(pk=self.pk)
                .update(is_active=False)
            )
