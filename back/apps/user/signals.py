from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .deletion import build_deletion_record, link_previous_deletion
from .models import DeletedAccountRecord, SocialIdentity, UserAccount


@receiver(pre_delete, sender=UserAccount)
def record_account_deletion(sender, instance, **kwargs):
    # Cualquier borrado que no pase por delete_account (admin, shell) también deja rastro.
    if getattr(instance, "_deletion_recorded", False):
        return
    build_deletion_record(instance, source=DeletedAccountRecord.Source.ADMIN)


@receiver(post_save, sender=UserAccount)
def detect_returning_user(sender, instance, created, **kwargs):
    if created:
        link_previous_deletion(instance)


@receiver(post_save, sender=SocialIdentity)
def detect_returning_social_user(sender, instance, created, **kwargs):
    if created:
        link_previous_deletion(instance.user, provider=instance.provider, subject=instance.subject)
