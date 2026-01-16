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