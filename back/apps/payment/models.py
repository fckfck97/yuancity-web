import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.orders.models import Order


class VendorBankAccount(models.Model):
    class AccountType(models.TextChoices):
        savings = "savings", "Ahorros"
        checking = "checking", "Corriente"

    class DocumentType(models.TextChoices):
        cc = "cc", "Cédula de ciudadanía"
        ce = "ce", "Cédula de extranjería"
        nit = "nit", "NIT"
        other = "other", "Otro"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bank_account",
    )
    bank_name = models.CharField(max_length=120)
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.savings,
    )
    account_number = models.CharField(max_length=50)
    account_holder_name = models.CharField(max_length=255)
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.cc,
    )
    document_number = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cuenta bancaria"
        verbose_name_plural = "Cuentas bancarias"

    def __str__(self):
        return f"{self.bank_name} · {self.account_number}"


class VendorPayout(models.Model):
    class Status(models.TextChoices):
        waiting_confirmation = "waiting_confirmation", "Esperando confirmación"
        pending_clearance = "pending_clearance", "En verificación"
        available = "available", "Disponible"
        released = "released", "Transferido"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendor_payouts",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="vendor_payouts",
    )
    items_count = models.PositiveIntegerField(default=0)
    gross_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    platform_fee = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.waiting_confirmation,
    )
    buyer_confirmed_at = models.DateTimeField(null=True, blank=True)
    available_on = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    bank_account_snapshot = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pago a vendedor"
        verbose_name_plural = "Pagos a vendedores"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["vendor", "order"],
                name="unique_payout_per_vendor_order",
            )
        ]

    def __str__(self):
        return f"{self.vendor} · {self.net_amount}"

    def refresh_status(self, commit: bool = True):
        """
        Actualiza el estado del payout cuando alcanza su fecha de disponibilidad.
        """
        if (
            self.status == self.Status.pending_clearance
            and self.available_on
            and timezone.now() >= self.available_on
        ):
            self.status = self.Status.available
            if commit:
                self.save(update_fields=["status", "updated_at"])
        return self
