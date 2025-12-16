from datetime import timedelta
from typing import Iterable, Optional, Union

from django.utils import timezone

from .models import Cart, CartItem

RESERVATION_DURATION_MINUTES = 60
RESERVATION_DURATION = timedelta(minutes=RESERVATION_DURATION_MINUTES)


def reservation_deadline():
    return timezone.now() + RESERVATION_DURATION


def _cart_id(value: Union[Cart, str, None]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, Cart):
        return value.id
    return value


def sync_cart_total(cart: Union[Cart, str, None]):
    cart_id = _cart_id(cart)
    if not cart_id:
        return
    total = CartItem.objects.filter(cart_id=cart_id).count()
    Cart.objects.filter(pk=cart_id).update(total_items=total)


def cleanup_expired_reservations(
    *, cart: Union[Cart, str, None] = None, product=None
) -> int:
    now = timezone.now()
    qs = CartItem.objects.filter(
        reserved_until__isnull=False, reserved_until__lt=now
    )
    if cart:
        qs = qs.filter(cart_id=_cart_id(cart))
    if product:
        qs = qs.filter(product=product)

    expired_cart_ids: Iterable[str] = qs.values_list("cart_id", flat=True)
    expired_ids = list(expired_cart_ids)
    if not expired_ids:
        return 0

    qs.delete()
    for cart_id in set(expired_ids):
        sync_cart_total(cart_id)
    return len(expired_ids)


def seconds_until(expiration) -> Optional[int]:
    if not expiration:
        return None
    delta = expiration - timezone.now()
    return max(int(delta.total_seconds()), 0)
