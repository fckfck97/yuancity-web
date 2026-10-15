"""
Eliminación de cuentas con trazabilidad y reconocimiento de quienes vuelven a registrarse.

YuanCity es un marketplace: si la persona compró o vendió, borrar el usuario en cascada
eliminaría pedidos, pagos a vendedores y reseñas de otras personas (y `OrderItem.product`
es DO_NOTHING, así que la base de datos rechazaría el borrado). En ese caso la cuenta se
**anonimiza**: se borran sus datos personales y se conserva solo el registro comercial.
Sin historial comercial, la cuenta se elimina por completo.
"""

import hashlib
import hmac
import logging
import uuid

from django.conf import settings
from django.db import connection, transaction
from django.db.models import Q
from django.utils import timezone

from .models import DeletedAccountRecord, UserAccount, UserProfile
from .utils.apple import revoke_apple_authorization

logger = logging.getLogger(__name__)

ACTIVE_ORDER_STATUSES = ("not_processed", "processed", "shipping")
ANONYMIZED_EMAIL_DOMAIN = "deleted.yuancity.invalid"


class AccountDeletionBlocked(Exception):
    """La cuenta no se puede eliminar todavía (p. ej. pedidos en curso)."""

    def __init__(self, message, code="deletion_blocked"):
        super().__init__(message)
        self.message = message
        self.code = code


def identity_hash(value):
    """HMAC estable de un identificador. Permite comparar sin guardar el dato en claro."""
    if not value:
        return ""
    key = settings.DELETION_HASH_KEY.encode()
    return hmac.new(key, str(value).strip().lower().encode(), hashlib.sha256).hexdigest()


def social_hash(provider, subject):
    return identity_hash(f"{provider}:{subject}")


def mask_email(email):
    local, _, domain = (email or "").partition("@")
    if not domain:
        return ""
    return f"{local[:2]}***@{domain}"


def client_ip(request):
    if request is None:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    return forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")


def _commerce_models():
    from apps.orders.models import Order, OrderItem

    return Order, OrderItem


def deletion_blockers(user):
    """Motivos por los que todavía no se puede eliminar la cuenta (lista vacía = se puede)."""
    Order, OrderItem = _commerce_models()
    blockers = []
    if Order.objects.filter(user=user, status__in=ACTIVE_ORDER_STATUSES).exists():
        blockers.append("Tienes pedidos en curso. Espera a que lleguen o cancélalos antes de eliminar tu cuenta.")
    if OrderItem.objects.filter(product__vendor=user, order__status__in=ACTIVE_ORDER_STATUSES).exists():
        blockers.append("Tienes ventas pendientes de entregar. Complétalas o cancélalas antes de eliminar tu cuenta.")
    return blockers


def has_commerce_history(user):
    Order, OrderItem = _commerce_models()
    return (
        Order.objects.filter(user=user).exists()
        or OrderItem.objects.filter(product__vendor=user).exists()
        or user.vendor_payouts.exists()
    )


def build_deletion_record(user, *, source, reason="", request=None, deleted_by=None, platform_revocation=None, mode=None):
    Order, _ = _commerce_models()
    identities = list(user.social_identities.values_list("provider", "subject"))
    return DeletedAccountRecord.objects.create(
        original_user_id=user.id,
        email_hash=identity_hash(user.email),
        email_hint=mask_email(user.email),
        phone_hash=identity_hash(user.phone),
        social_subject_hashes=[social_hash(provider, subject) for provider, subject in identities],
        social_providers=sorted({provider for provider, _ in identities}),
        role=user.rol or "",
        orders_count=Order.objects.filter(user=user).count(),
        products_count=user.products.count(),
        mode=mode or DeletedAccountRecord.Mode.DELETED,
        account_created_at=user.created_at,
        source=source,
        reason=(reason or "")[:2000],
        platform_revocation=platform_revocation or {},
        deleted_by=deleted_by if deleted_by and deleted_by.pk != user.pk else None,
        ip_address=client_ip(request),
        user_agent=(request.META.get("HTTP_USER_AGENT", "") if request else "")[:2000],
    )


def _delete_profile_files(user):
    """Borra foto y portada del almacenamiento. Nunca interrumpe la eliminación."""
    profile = UserProfile.objects.filter(user=user).first()
    if not profile:
        return
    for field in (profile.avatar, profile.cover_image):
        if field:
            try:
                field.storage.delete(field.name)
            except Exception:  # noqa: BLE001 - almacenamiento remoto caído o archivo ya borrado
                logger.warning("No se pudo borrar el archivo %s", field.name)


def _anonymize(user):
    """Borra los datos personales y conserva pedidos, pagos y reseñas sin identificar a la persona."""
    _, OrderItem = _commerce_models()

    # Productos: los que nunca se vendieron se eliminan; los vendidos se ocultan (el pedido los referencia).
    sold_ids = set(OrderItem.objects.filter(product__vendor=user).values_list("product_id", flat=True))
    user.products.exclude(id__in=sold_ids).delete()
    user.products.filter(id__in=sold_ids).update(is_available=False, stock=0)

    # Datos personales y de uso.
    for relation in (
        "social_identities",
        "push_tokens",
        "notifications",
        "login_logs",
        "following",
        "followers",
        "support_tickets",
        "chat_messages",
        "client_cases",
    ):
        manager = getattr(user, relation, None)
        if manager is not None:
            manager.all().delete()
    for one_to_one in ("bank_account", "lawyer_profile", "cart", "wishlist"):
        related = getattr(user, one_to_one, None) if hasattr(user, one_to_one) else None
        if related is not None:
            related.delete()

    _delete_profile_files(user)
    # update() evita la señal que intenta borrar archivos con `.path` (no existe en S3).
    UserProfile.objects.filter(user=user).update(
        bio="",
        department="",
        city="",
        location="",
        address_line="",
        latitude=None,
        longitude=None,
        avatar=None,
        cover_image=None,
    )

    user.email = f"deleted-{uuid.uuid4().hex}@{ANONYMIZED_EMAIL_DOMAIN}"
    user.first_name = "Usuario"
    user.last_name = "eliminado"
    user.phone = None
    user.phone_verified = False
    user.otp = None
    user.is_active = False
    user.is_staff = False
    user.consent_notifications = False
    user.next_send_at = None
    user.set_unusable_password()
    user.save()


def delete_account(user, *, source, reason="", request=None, deleted_by=None, apple_authorization_code=None, google_revoked=False, force=False):
    """
    Revoca el acceso en las plataformas vinculadas, deja el registro y elimina (o anonimiza) la cuenta.
    Google se revoca desde la app; Apple desde el servidor con el authorization_code.
    `force=True` (solo administración) ignora los pedidos en curso.
    """
    if not force:
        blockers = deletion_blockers(user)
        if blockers:
            raise AccountDeletionBlocked(blockers[0])

    providers = set(user.social_identities.values_list("provider", flat=True))
    revocation = {}
    if "google" in providers:
        revocation["google"] = "revoked_by_client" if google_revoked else "not_revoked"
    if "apple" in providers:
        revocation["apple"] = revoke_apple_authorization(apple_authorization_code)

    with transaction.atomic():
        anonymize = has_commerce_history(user)
        record = build_deletion_record(
            user,
            source=source,
            reason=reason,
            request=request,
            deleted_by=deleted_by,
            platform_revocation=revocation,
            mode=DeletedAccountRecord.Mode.ANONYMIZED if anonymize else DeletedAccountRecord.Mode.DELETED,
        )
        if anonymize:
            _anonymize(user)
        else:
            _delete_profile_files(user)
            # El receptor pre_delete no debe crear un segundo registro.
            user._deletion_recorded = True
            user.delete()
    return record


def link_previous_deletion(user, *, provider=None, subject=None):
    """Si la persona ya había eliminado una cuenta, enlaza el registro con la cuenta nueva."""
    email_hash = identity_hash(user.email)
    phone_hash = identity_hash(user.phone)
    target = social_hash(provider, subject) if provider and subject else None
    candidates = DeletedAccountRecord.objects.filter(rejoined_user__isnull=True)
    if connection.features.supports_json_field_contains:
        lookup = Q(email_hash=email_hash)
        if phone_hash:
            lookup |= Q(phone_hash=phone_hash)
        if target:
            lookup |= Q(social_subject_hashes__contains=[target])
        records = list(candidates.filter(lookup))
    else:
        # SQLite no soporta `contains` sobre JSON: se compara en Python.
        records = [
            record
            for record in candidates
            if record.email_hash == email_hash
            or (phone_hash and record.phone_hash == phone_hash)
            or (target and target in record.social_subject_hashes)
        ]
    for record in records:
        record.rejoined_user = user
        record.rejoined_at = timezone.now()
        record.save(update_fields=("rejoined_user", "rejoined_at"))
    return records


def has_previous_deletion(user: UserAccount):
    return user.previous_deletions.exists()
