from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import VendorPayout


def add_business_days(start, business_days: int):
    """
    Retorna una fecha sumando n días hábiles (lunes a viernes).
    """
    current = start
    added = 0
    while added < business_days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


def refresh_payout_statuses(vendor):
    """
    Actualiza los payouts de un vendedor que ya cumplieron la fecha de liberación.
    """
    now = timezone.now()
    VendorPayout.objects.filter(
        vendor=vendor,
        status=VendorPayout.Status.pending_clearance,
        available_on__isnull=False,
        available_on__lte=now,
    ).update(status=VendorPayout.Status.available, updated_at=now)


def summarize_amount(queryset):
    """
    Calcula la suma del neto en un queryset de payouts.
    """
    return queryset.aggregate(
        total=Coalesce(Sum("net_amount"), Decimal("0.00"))
    )["total"] or Decimal("0.00")
