# core/models.py
import uuid
import os
from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from apps.cart.models import Cart
from apps.wishlist.models import WishList
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils import timezone

def user_avatar_path(instance, filename):
    """
    Retorna la ruta: users/{user_id}/avatar/{filename}
    """
    ext = os.path.splitext(filename)[1]
    new_filename = f"avatar{ext}"
    return f"users/{instance.user.id}/avatar/{new_filename}"


def user_cover_path(instance, filename):
    """
    Retorna la ruta: users/{user_id}/cover/{filename}
    """
    ext = os.path.splitext(filename)[1]
    new_filename = f"cover{ext}"
    return f"users/{instance.user.id}/cover/{new_filename}"
class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        
        shopping_cart = Cart.objects.create(user=user)
        shopping_cart.save()
        
        wishlist = WishList.objects.create(user=user)
        wishlist.save()
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin',      'Administrator'),
        ('client',     'Client'),
        ('vendor',     'Vendor'),
        ('delivery',   'Delivery'),
    )
    SUBSCRIPTION_CHOICES = (
        ('standard', 'Standard'),
        ('premium',  'Premium'),
    )

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email        = models.EmailField(max_length=255, unique=True)
    phone        = models.CharField(max_length=20, blank=True, null=True)
    phone_verified = models.BooleanField(default=False)

    first_name   = models.CharField(max_length=255)
    last_name    = models.CharField(max_length=255)

    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    rol         = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    subscription = models.CharField(max_length=10, choices=SUBSCRIPTION_CHOICES, default='standard')

    otp          = models.CharField(max_length=8, blank=True, null=True)
    stage = models.PositiveSmallIntegerField(default=0)
    next_send_at = models.DateTimeField(blank=True, null=True)
    last_sent_at = models.DateTimeField(blank=True, null=True)
    consent_notifications = models.BooleanField(default=True)
    objects      = UserAccountManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def generate_otp(self, web=False):
        import random, string

        length = 6 if web else 4
        code = ''.join(random.choices(string.digits, k=length))
        self.otp = code
        self.save(update_fields=['otp'])
        return code


    
    def schedule_first(self):
        """Programa el primer mensaje de onboarding si el usuario dio consentimiento"""
        if self.consent_notifications:
            self.stage = 0
            self.next_send_at = timezone.now()
            self.save(update_fields=['stage', 'next_send_at'])

    def advance_schedule(self):
        """Avanza al siguiente stage con los delays configurados"""
        from datetime import timedelta
        
        now = timezone.now()
        self.last_sent_at = now

        delays = {
            0: timedelta(days=1),
            1: timedelta(days=2),
            2: timedelta(days=3),
            3: timedelta(days=4),
            4: timedelta(days=4),
            5: None,
        }

        if self.stage >= 6:
            self.next_send_at = None
            self.save(update_fields=['next_send_at', 'last_sent_at'])
            return

        if self.stage in delays and delays[self.stage] is None:
            self.stage = 6
            self.next_send_at = None
            self.save(update_fields=['stage', 'next_send_at', 'last_sent_at'])
            return

        delay = delays.get(self.stage, timedelta(days=7))
        self.stage = min(self.stage + 1, 6)
        self.next_send_at = now + delay
        self.save(update_fields=['stage', 'next_send_at', 'last_sent_at'])

    def can_restart_stage_cycle(self, now=None, days=3):
        """Retorna True si el ciclo terminó y ya puede reiniciarse."""
        if self.stage < 6 or not self.last_sent_at:
            return False
        current = now or timezone.now()
        return self.last_sent_at <= (current - timezone.timedelta(days=days))

    def restart_stage_cycle(self, now=None):
        """Reinicia el ciclo de mensajes para reenviar desde el stage 0."""
        current = now or timezone.now()
        self.stage = 0
        self.next_send_at = current
        self.save(update_fields=['stage', 'next_send_at'])


class UserProfile(models.Model):
    """
    Perfil público estilo red social para cualquier usuario.
    Separa los datos sociales de la información de autenticación.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="social_profile",
    )
    username = models.SlugField(max_length=40, unique=True)
    bio = models.TextField(blank=True, default="")
    department = models.CharField(max_length=80, blank=True, default="")
    city = models.CharField(max_length=120, blank=True, default="")
    location = models.CharField(max_length=160, blank=True, default="")
    address_line = models.CharField(max_length=255, blank=True, default="")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    avatar = models.ImageField(upload_to=user_avatar_path, blank=True, null=True)
    cover_image = models.ImageField(upload_to=user_cover_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Perfil de {self.user.email}"


def build_default_username(user: "UserAccount") -> str:
    """
    Genera automáticamente un identificador de perfil basado en el correo.
    Siempre retorna un valor único dentro de UserProfile.
    """
    max_length = UserProfile._meta.get_field("username").max_length or 40
    email = (getattr(user, "email", "") or "").strip().lower()
    base_source = email
    if email and "@" in email:
        local, domain = email.split("@", 1)
        base_source = f"{local}-{domain}"
    base_source = base_source.replace(".", "-")
    base_slug = slugify(base_source)
    fallback = f"user-{str(user.id).replace('-', '')[:8]}"
    candidate_root = (base_slug or slugify(user.full_name or "") or fallback)[: max_length - 4]
    if not candidate_root:
        candidate_root = fallback[: max_length - 4] or str(user.id).replace("-", "")[: max_length - 4]
    candidate = candidate_root
    suffix = 1
    queryset = UserProfile.objects.exclude(user=user)
    while queryset.filter(username=candidate).exists():
        suffix += 1
        suffix_str = f"-{suffix}"
        trimmed = candidate_root[: max_length - len(suffix_str)]
        candidate = f"{trimmed}{suffix_str}"
    return candidate[:max_length]


class UserFollow(models.Model):
    """
    Relación seguidor/seguido para habilitar followers & following.
    """
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.follower.email} → {self.following.email}"


class LoginLog(models.Model):
    user       = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     on_delete=models.CASCADE,
                     related_name='login_logs'
                 )
    provider   = models.CharField(max_length=16, default="otp")  # otp, google, apple, biometric…
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    success    = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        timestamp = self.created_at.strftime('%Y-%m-%d %H:%M')
        return f"{self.user.email} @ {self.ip_address} – {timestamp}"



class ExpoPushToken(models.Model):
    user        = models.ForeignKey(UserAccount, on_delete=models.CASCADE,
                                    related_name="push_tokens",null=True, blank=True)
    token       = models.CharField(max_length=255, unique=True)
    device_os   = models.CharField(max_length=10, blank=True)  # ios / android
    active      = models.BooleanField(default=True)
    last_used   = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [models.Index(fields=["token"])]
        verbose_name = "Expo Push Token"
        verbose_name_plural = "Expo Push Tokens"
        

class Notification(models.Model):
    user = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    data = models.JSONField(blank=True, null=True)  # Para datos adicionales
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notificación de {self.title} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
      


@receiver(post_save, sender=UserAccount)
def create_social_profile(sender, instance, created, **kwargs):
    """
    Garantiza que todo usuario tenga un UserProfile para exponer datos sociales.
    """
    desired_username = build_default_username(instance)
    profile, _ = UserProfile.objects.get_or_create(
        user=instance,
        defaults={"username": desired_username},
    )
    if profile.username != desired_username:
        profile.username = desired_username
        profile.save(update_fields=["username"])


@receiver(pre_save, sender=UserProfile)
def delete_old_profile_images(sender, instance, **kwargs):
    """
    Elimina las imágenes antiguas de avatar y cover cuando se actualizan.
    """
    if not instance.pk:
        return
    
    try:
        old_profile = UserProfile.objects.get(pk=instance.pk)
    except UserProfile.DoesNotExist:
        return
    
    # Eliminar avatar antiguo si cambió
    if old_profile.avatar and old_profile.avatar != instance.avatar:
        if os.path.isfile(old_profile.avatar.path):
            os.remove(old_profile.avatar.path)
    
    # Eliminar cover antiguo si cambió
    if old_profile.cover_image and old_profile.cover_image != instance.cover_image:
        if os.path.isfile(old_profile.cover_image.path):
            os.remove(old_profile.cover_image.path)

class LawyerProfile(models.Model):
    SPECIALTIES = (
        ('Derecho Penal', 'Derecho Penal'),
        ('Derecho Laboral', 'Derecho Laboral'),
        ('Derecho Civil', 'Derecho Civil'),
        ('Derecho Comercial', 'Derecho Comercial')
    )
    
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='lawyer_profile')
    specialties = models.CharField(max_length=100, choices=SPECIALTIES, blank=True, null=True)
    bar_association_id = models.CharField(max_length=50, blank=True, null=True)
    experience_years = models.IntegerField(blank=True, null=True)
    current_caseload = models.IntegerField(default=0, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'Perfil de Abogado'
        verbose_name_plural = 'Perfiles de Abogados'
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.user.email} - {self.specialties}"
    def current_cases(self):
        return self.user.cases_assigned.all().order_by('-created_at')

# ---------------------------------------------------------------------------
# Acceso sin contraseña, identidades sociales y eliminación de cuentas
# (portado de base-project y adaptado a YuanCity)
# ---------------------------------------------------------------------------

class LoginCode(models.Model):
    """
    Código de acceso por correo o SMS. Solo se guarda su hash.
    Las apps nuevas piden 6 dígitos; las versiones publicadas antes siguen recibiendo 4.
    """

    CODE_TTL_MINUTES = 10
    MAX_ATTEMPTS = 5
    RESEND_AFTER_SECONDS = 60
    ALLOWED_LENGTHS = (4, 6)

    identifier = models.CharField(max_length=255)  # correo en minúsculas o teléfono normalizado
    code_hash = models.CharField(max_length=128)
    attempts = models.PositiveSmallIntegerField(default=0)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Código de acceso"
        verbose_name_plural = "Códigos de acceso"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["identifier", "created_at"])]

    def __str__(self):
        return f"{self.identifier} ({self.created_at:%Y-%m-%d %H:%M})"

    @property
    def is_usable(self):
        return self.used_at is None and timezone.now() < self.expires_at and self.attempts < self.MAX_ATTEMPTS

    def check_code(self, code):
        from django.contrib.auth.hashers import check_password

        return check_password(code, self.code_hash)

    @classmethod
    def issue(cls, identifier, length=6, ip_address=None):
        """Invalida los códigos anteriores y crea uno nuevo. Devuelve (registro, código en claro)."""
        import secrets
        from datetime import timedelta
        from django.contrib.auth.hashers import make_password

        length = length if length in cls.ALLOWED_LENGTHS else 6
        now = timezone.now()
        cls.objects.filter(identifier=identifier, used_at__isnull=True).update(used_at=now)
        code = f"{secrets.randbelow(10 ** length):0{length}d}"
        record = cls.objects.create(
            identifier=identifier,
            code_hash=make_password(code),
            expires_at=now + timedelta(minutes=cls.CODE_TTL_MINUTES),
            ip_address=ip_address,
        )
        return record, code


class SocialIdentity(models.Model):
    """Cuenta de Google o Apple vinculada. Se identifica por `sub`, no por el correo."""

    class Provider(models.TextChoices):
        GOOGLE = "google", "Google"
        APPLE = "apple", "Apple"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="social_identities")
    provider = models.CharField(max_length=16, choices=Provider.choices)
    subject = models.CharField(max_length=255)
    # Datos tal como los entregó la plataforma (Apple solo envía el nombre la primera vez).
    email = models.EmailField(max_length=255, blank=True, default="")
    email_verified = models.BooleanField(default=False)
    is_private_email = models.BooleanField(default=False, help_text="Correo de reenvío privado de Apple.")
    first_name = models.CharField(max_length=120, blank=True, default="")
    last_name = models.CharField(max_length=120, blank=True, default="")
    picture_url = models.URLField(max_length=500, blank=True, default="")
    locale = models.CharField(max_length=16, blank=True, default="")
    last_login_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cuenta vinculada"
        verbose_name_plural = "Cuentas vinculadas"
        constraints = [models.UniqueConstraint(fields=("provider", "subject"), name="unique_social_provider_subject")]

    def __str__(self):
        return f"{self.provider}:{self.email or self.subject}"


class AccountDeletionRequest(models.Model):
    """Solicitud de eliminación iniciada desde la web (sin sesión): código por correo + confirmación."""

    CODE_TTL_MINUTES = 15
    MAX_ATTEMPTS = 5

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        COMPLETED = "completed", "Completada"
        CANCELLED = "cancelled", "Cancelada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deletion_requests",
    )
    code_hash = models.CharField(max_length=128, blank=True, default="")
    reason = models.TextField(blank=True, default="")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    attempts = models.PositiveSmallIntegerField(default=0)
    expires_at = models.DateTimeField()
    completed_at = models.DateTimeField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Solicitud de eliminación de cuenta"
        verbose_name_plural = "Solicitudes de eliminación de cuenta"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["email", "status"])]

    def __str__(self):
        return f"{self.email} ({self.status})"

    @property
    def is_usable(self):
        return self.status == self.Status.PENDING and timezone.now() < self.expires_at and self.attempts < self.MAX_ATTEMPTS

    def check_code(self, code):
        from django.contrib.auth.hashers import check_password

        return check_password(code, self.code_hash)

    @classmethod
    def issue(cls, email, user=None, ip_address=None, user_agent=""):
        """Cancela las solicitudes previas, crea una nueva y devuelve (solicitud, código)."""
        import secrets
        from datetime import timedelta
        from django.contrib.auth.hashers import make_password

        email = email.strip().lower()
        cls.objects.filter(email=email, status=cls.Status.PENDING).update(status=cls.Status.CANCELLED)
        code = f"{secrets.randbelow(10 ** 6):06d}"
        deletion_request = cls.objects.create(
            email=email,
            user=user,
            code_hash=make_password(code),
            expires_at=timezone.now() + timedelta(minutes=cls.CODE_TTL_MINUTES),
            ip_address=ip_address,
            user_agent=(user_agent or "")[:2000],
        )
        return deletion_request, code


class DeletedAccountRecord(models.Model):
    """
    Rastro de una cuenta eliminada. No guarda datos personales en claro: correo,
    teléfono e identificadores de Google/Apple se guardan como HMAC para reconocer
    a la persona si vuelve a registrarse, sin poder reconstruirlos.
    """

    class Source(models.TextChoices):
        APP = "app", "App"
        WEB = "web", "Web"
        ADMIN = "admin", "Administrador"

    class Mode(models.TextChoices):
        DELETED = "deleted", "Eliminada por completo"
        ANONYMIZED = "anonymized", "Anonimizada (tenía pedidos)"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_user_id = models.UUIDField(db_index=True)
    email_hash = models.CharField(max_length=64, db_index=True)
    email_hint = models.CharField(max_length=120, blank=True, default="", help_text="Correo enmascarado, solo de referencia.")
    phone_hash = models.CharField(max_length=64, blank=True, default="", db_index=True)
    social_subject_hashes = models.JSONField(default=list, blank=True)
    social_providers = models.JSONField(default=list, blank=True)
    role = models.CharField(max_length=20, blank=True, default="")
    orders_count = models.PositiveIntegerField(default=0, help_text="Pedidos como comprador.")
    products_count = models.PositiveIntegerField(default=0, help_text="Productos publicados como vendedor.")
    mode = models.CharField(max_length=12, choices=Mode.choices, default=Mode.DELETED)
    account_created_at = models.DateTimeField(blank=True, null=True)
    source = models.CharField(max_length=10, choices=Source.choices)
    reason = models.TextField(blank=True, default="")
    platform_revocation = models.JSONField(default=dict, blank=True, help_text="Resultado de revocar el acceso en Google/Apple.")
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_accounts",
        help_text="Administrador que eliminó la cuenta.",
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, default="")
    deleted_at = models.DateTimeField(auto_now_add=True)
    rejoined_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="previous_deletions",
    )
    rejoined_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Cuenta eliminada"
        verbose_name_plural = "Cuentas eliminadas"
        ordering = ["-deleted_at"]

    def __str__(self):
        return f"{self.email_hint or self.original_user_id} ({self.get_source_display()})"
