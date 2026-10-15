from rest_framework.response import Response
from rest_framework import permissions
from .serializers import (
    UserSerializerEdit,
    OTPRequestSerializer,
    OTPVerifySerializer,
    ExpoPushTokenUpsertSerializer,
    UserProfileSerializer,
    PublicProfileSerializer,
    FollowActionSerializer,
    FollowListEntrySerializer,
    N8NUserStageSerializer,
)
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from .utils.jwt import build_tokens
from .models import (
    UserAccount as User,
    ExpoPushToken,
    UserProfile,
    UserFollow,
    Notification,
    build_default_username,
)
from rest_framework.views import APIView 
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .utils.sendOTP import send_sms_in_background
from django.db import transaction
from .utils.password import strong_random_password
from .utils.phone import normalize
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date
from rest_framework.pagination import LimitOffsetPagination
from datetime import datetime, time, timedelta
import secrets
import jwt, requests  # pyjwt para Apple
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests 
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from apps.product.models import Product
from apps.product.serializers import ProductMinimalSerializer
from apps.utils.pagination import MediumSetPagination
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import LoginLog
from .utils.push import send_push
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from apps.utils.yuancity_stage_templates import build_stage_output
import logging
from django.core.cache import cache
from .models import LoginCode, SocialIdentity, DeletedAccountRecord
from .deletion import AccountDeletionBlocked, client_ip, delete_account
from .utils.avatar import import_remote_avatar

logger = logging.getLogger(__name__)


def log_login(request, user, provider, success=True):
    LoginLog.objects.create(
        user=user,
        provider=provider,
        success=success,
        ip_address=client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:2000],
    )

def normalize_email(email: str) -> str:
    return email.strip().lower()


def resolve_user_identifier(identifier):
    """Resuelve usuario solo por UUID"""
    if not identifier:
        return None
    try:
        return User.objects.get(pk=identifier)
    except Exception:
        return None

class SocialLoginView(APIView):
    """
    POST /api/social/login/  { provider: "google"|"apple", id_token, first_name?, last_name? }
    Valida el id_token, vincula la cuenta por `sub` (SocialIdentity) y devuelve los JWT.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        provider = request.data.get("provider")
        raw_token = request.data.get("id_token")
        first_name = str(request.data.get("first_name") or "").strip()
        last_name = str(request.data.get("last_name") or "").strip()

        if provider not in ("google", "apple") or not raw_token:
            return Response({"detail": "Proveedor o token inválido."}, status=400)

        if provider == "google":
            allowed = [client_id for client_id in settings.GOOGLE_CLIENT_IDS if client_id]
            if not allowed:
                return Response({"detail": "Google Sign-In aún no está configurado en el servidor."}, status=503)
            try:
                payload = google_id_token.verify_oauth2_token(raw_token, google_requests.Request())
            except (ValueError, KeyError):
                return Response({"detail": "Token de Google inválido."}, status=400)
            if payload.get("aud") not in allowed:
                return Response({"detail": "Cliente de Google no autorizado."}, status=400)
            if not payload.get("email_verified"):
                return Response({"detail": "Google no verificó el correo."}, status=400)
            subject = payload.get("sub")
            email = payload.get("email")
            first_name = payload.get("given_name") or first_name
            last_name = payload.get("family_name") or last_name
            platform_data = {
                "email_verified": True,
                "picture_url": payload.get("picture", ""),
                "locale": payload.get("locale", ""),
            }
        else:
            try:
                keys = cache.get("apple-jwks")
                if keys is None:
                    jwks_response = requests.get("https://appleid.apple.com/auth/keys", timeout=8)
                    jwks_response.raise_for_status()
                    keys = jwks_response.json().get("keys", [])
                    cache.set("apple-jwks", keys, 86400)
                header = jwt.get_unverified_header(raw_token)
                key_data = next(key for key in keys if key.get("kid") == header.get("kid"))
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_data)
                payload = jwt.decode(
                    raw_token,
                    public_key,
                    algorithms=["RS256"],
                    audience=settings.APPLE_ALLOWED_AUDS,
                    issuer="https://appleid.apple.com",
                )
            except (requests.RequestException, jwt.PyJWTError, StopIteration, KeyError, ValueError):
                # Apple rota sus llaves: si el kid no está en caché se vuelve a descargar la próxima vez.
                cache.delete("apple-jwks")
                return Response({"detail": "Token de Apple inválido."}, status=400)
            subject = payload.get("sub")
            email = payload.get("email")
            # Apple manda los booleanos como texto ("true") en algunos tokens.
            platform_data = {
                "email_verified": str(payload.get("email_verified", "")).lower() == "true",
                "is_private_email": str(payload.get("is_private_email", "")).lower() == "true",
            }

        if not subject:
            return Response({"detail": "El proveedor no entregó un identificador."}, status=400)

        identity = SocialIdentity.objects.select_related("user").filter(provider=provider, subject=subject).first()
        is_new_user = False
        if identity:
            user = identity.user
        else:
            if not email:
                return Response({"detail": "El proveedor no entregó el correo."}, status=400)
            email_norm = normalize_email(email)
            user = User.objects.filter(email__iexact=email_norm).first()
            if user is None:
                # create_user crea también el carrito y la lista de deseos.
                user = User.objects.create_user(
                    email=email_norm,
                    password=strong_random_password(),
                    first_name=first_name,
                    last_name=last_name,
                )
                is_new_user = True
            identity = SocialIdentity.objects.create(user=user, provider=provider, subject=subject)

        if not user.is_active:
            return Response({"detail": "Esta cuenta está desactivada."}, status=403)

        # Apple solo entrega el nombre en el primer inicio: nunca se sobrescribe con vacío.
        identity.email = email or identity.email
        identity.first_name = first_name or identity.first_name
        identity.last_name = last_name or identity.last_name
        for field, value in platform_data.items():
            setattr(identity, field, value or getattr(identity, field))
        identity.last_login_at = timezone.now()
        identity.save()

        # Completa el perfil con lo que dio la plataforma, sin pisar lo que el usuario ya editó.
        updated = []
        if not user.first_name and first_name:
            user.first_name = first_name
            updated.append("first_name")
        if not user.last_name and last_name:
            user.last_name = last_name
            updated.append("last_name")
        if updated:
            user.save(update_fields=updated)
        profile = getattr(user, "social_profile", None)
        if profile and identity.picture_url:
            import_remote_avatar(profile, identity.picture_url)

        log_login(request, user, provider)
        return Response({**build_tokens(user), "is_new_user": is_new_user}, status=200)

class UserEditView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializerEdit(user, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = UserSerializerEdit(
            user,
            data=request.data,
            context={'request': request},
            partial=True,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class ProfilePictureUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        upload = request.FILES.get("file")
        if not upload:
            return Response({"detail": "Archivo 'file' requerido."}, status=status.HTTP_400_BAD_REQUEST)

        profile = getattr(request.user, "social_profile", None)
        if profile is None:
            profile = UserProfile.objects.create(
                user=request.user,
                username=build_default_username(request.user),
            )

        profile.avatar = upload
        profile.save(update_fields=["avatar"])

        avatar_url = None
        if profile.avatar:
            avatar_url = profile.avatar.url
            if hasattr(request, "build_absolute_uri"):
                avatar_url = request.build_absolute_uri(avatar_url)

        return Response({"avatar_url": avatar_url}, status=status.HTTP_200_OK)
      
   
DEMO_ACCOUNTS = {
    "apple.revisor@yuancity.com",
    "google.revisor@yuancity.com",
    "huawei.revisor@yuancity.com",
}


def is_demo_account(email):
    return (email or "").strip().lower() in DEMO_ACCOUNTS


def throttle_login_code(identifier):
    """Devuelve una Response 429 si se piden códigos demasiado seguido; None si se puede enviar."""
    window_start = timezone.now() - timedelta(minutes=OTP_THROTTLE_WINDOW_MINUTES)
    recent = LoginCode.objects.filter(identifier=identifier, created_at__gte=window_start)
    last = recent.first()
    if last:
        wait = LoginCode.RESEND_AFTER_SECONDS - int((timezone.now() - last.created_at).total_seconds())
        if wait > 0:
            return Response(
                {"detail": f"Espera {wait} segundos para pedir otro código.", "resend_in": wait},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
    if recent.count() >= OTP_THROTTLE_MAX_REQUESTS:
        return Response(
            {"detail": "Demasiadas solicitudes. Inténtalo de nuevo en unos minutos."},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )
    return None


def send_login_code_email(email, code):
    minutes = LoginCode.CODE_TTL_MINUTES
    send_mail(
        f"Tu código de acceso a {settings.APP_NAME}",
        (
            f"Tu código para ingresar a {settings.APP_NAME} es: {code}\n\n"
            f"Vence en {minutes} minutos. Si no lo pediste, ignora este correo."
        ),
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )


OTP_THROTTLE_WINDOW_MINUTES = 15
OTP_THROTTLE_MAX_REQUESTS = 5


class OTPLoginRequestView(APIView):
  """
  POST /api/login/otp/request/
    { "email": "...", "code_length": 6 }  ó  { "phone": "3001234567", "channel": "sms|whatsapp" }
  Envía un código (solo se guarda su hash). La cuenta se crea al validarlo.
  `code_length` es 6 en las apps nuevas; las versiones publicadas antes no lo envían y reciben 4.
  """
  permission_classes = [permissions.AllowAny]

  def post(self, request):
    ser = OTPRequestSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    email = ser.validated_data.get("email")
    phone = ser.validated_data.get("phone")
    length = ser.validated_data.get("code_length") or 4

    if email:
      identifier = normalize_email(email)
      # Cuentas de revisión de las tiendas: entran sin código.
      if is_demo_account(identifier):
        user = User.objects.filter(email=identifier).first()
        if user:
          return Response(build_tokens(user), status=200)
      is_new_user = not User.objects.filter(email__iexact=identifier).exists()
    else:
      identifier = normalize(phone)
      if not identifier.isdigit() or len(identifier) < 7:
        return Response({"detail": "Número de teléfono inválido."}, status=400)
      is_new_user = not User.objects.filter(phone=identifier).exists()

    throttled = throttle_login_code(identifier)
    if throttled:
      return throttled

    record, code = LoginCode.issue(identifier, length=length, ip_address=client_ip(request))

    if email:
      try:
        send_login_code_email(identifier, code)
      except Exception:  # noqa: BLE001 - el correo caído no debe dejar un código que nadie recibió
        logger.exception("No se pudo enviar el código de acceso a %s", identifier)
        record.delete()
        return Response({"detail": "No pudimos enviar el correo. Inténtalo de nuevo en unos minutos."}, status=503)
    else:
      send_sms_in_background(
        f"+{identifier}",
        f"Tu código de acceso a {settings.APP_NAME} es: {code}",
      )

    # NUNCA devolver el código en la respuesta (ni con DEBUG).
    return Response({
      "detail": f"Te enviamos un código de {length} dígitos.",
      "is_new_user": is_new_user,
      "code_length": length,
      "expires_in": LoginCode.CODE_TTL_MINUTES * 60,
      "resend_in": LoginCode.RESEND_AFTER_SECONDS,
    }, status=200)


class OTPLoginVerifyView(APIView):
  """
  POST /api/login/otp/verify/
    { "identifier": "correo@dominio.com" ó "+573001234567", "otp": "123456" }
  Valida el código (máx. 5 intentos, vence en 10 min). Si no hay cuenta, la crea.
  """
  permission_classes = [permissions.AllowAny]

  def post(self, request):
    ser = OTPVerifySerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    raw = ser.validated_data["identifier"].strip()
    otp = ser.validated_data["otp"]
    is_email = "@" in raw
    identifier = normalize_email(raw) if is_email else normalize(raw)
    invalid = Response({"detail": "Código incorrecto o vencido. Solicita uno nuevo."}, status=400)

    # Cuentas de revisión de las tiendas: no validan código.
    if is_email and is_demo_account(identifier):
      user = User.objects.filter(email=identifier).first()
      if user:
        return Response(build_tokens(user), status=200)

    record = (
      LoginCode.objects.select_for_update()
      .filter(identifier=identifier, used_at__isnull=True)
      .first()
    )
    if not record or not record.is_usable:
      return invalid
    if not record.check_code(otp):
      record.attempts += 1
      record.save(update_fields=["attempts"])
      left = LoginCode.MAX_ATTEMPTS - record.attempts
      if left <= 0:
        return invalid
      return Response({"detail": f"Código incorrecto. Te quedan {left} intentos.", "attempts_left": left}, status=400)

    record.used_at = timezone.now()
    record.save(update_fields=["used_at"])

    is_new_user = False
    if is_email:
      user = User.objects.filter(email__iexact=identifier).first()
      if user is None:
        user = User.objects.create_user(
          email=identifier,
          password=strong_random_password(),
          first_name="",
          last_name="",
        )
        is_new_user = True
    else:
      user = User.objects.filter(phone=identifier).first()
      if user is None:
        user = User.objects.create_user(
          email=f"{identifier}@yuancity.com",
          password=strong_random_password(),
          phone=identifier,
          first_name="",
          last_name="",
        )
        is_new_user = True
      if not user.phone_verified:
        user.phone_verified = True
        user.save(update_fields=["phone_verified"])

    if not user.is_active:
      return invalid

    log_login(request, user, "otp")
    return Response({**build_tokens(user), "is_new_user": is_new_user}, status=200)



class OTPLoginRequestWebView(APIView):
    """
    POST /api/login/otp/request/web/
      { "email": "usuario@dominio.com" }
    Envía un código de 6 dígitos solo si el usuario existe, está activo y está autorizado para web.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = OTPRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        email_norm = normalize_email(ser.validated_data.get("email") or "")

        # Validar que el correo esté en la lista de autorizados para web
        if email_norm not in settings.WEB_ALLOWED_EMAILS:
            return Response(
                {"detail": "No tienes autorización para acceder a la plataforma web. Contacta al administrador."},
                status=403,
            )

        user = User.objects.filter(email=email_norm, is_active=True).first()
        if not user:
            return Response({"detail": "Correo no autorizado."}, status=403)

        throttled = throttle_login_code(email_norm)
        if throttled:
            return throttled

        record, code = LoginCode.issue(email_norm, length=6, ip_address=client_ip(request))
        try:
            send_login_code_email(email_norm, code)
        except Exception:  # noqa: BLE001
            logger.exception("No se pudo enviar el código web a %s", email_norm)
            record.delete()
            return Response({"detail": "No pudimos enviar el correo. Inténtalo de nuevo en unos minutos."}, status=503)

        return Response({"detail": "OTP enviado."}, status=200)



class ExpoPushTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print(f"🔍 ExpoPushToken request.data: {request.data}")
        print(f"🔍 request.user: {request.user}, is_authenticated: {getattr(request.user, 'is_authenticated', None)}")

        ser = ExpoPushTokenUpsertSerializer(data=request.data)
        try:
            ser.is_valid(raise_exception=True)
        except ValidationError:
            print("❌ Serializer errors:", ser.errors)
            return Response({"detail": ser.errors}, status=400)

        token = ser.validated_data["token"]
        device_os = ser.validated_data["device_os"]
        user = request.user if getattr(request.user, "is_authenticated", False) else None

        # Si no viene autenticado, intentamos user_id (opcional)
        if user is None:
            user_id = ser.validated_data.get("user_id")
            print(f"🔍 user_id extraído del serializer: {user_id}")
            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                    print(f"✅ Usuario encontrado por user_id: {user.id} - {user.email}")
                except User.DoesNotExist:
                    print(f"❌ Usuario con ID {user_id} no encontrado")
                    user = None

        # === Upsert por token ===
        try:
            token_obj = ExpoPushToken.objects.get(token=token)
            # Actualizamos campos
            token_obj.device_os = device_os
            token_obj.active = True

            # Reasignar usuario si procede:
            # - Si antes no tenía usuario y ahora sí → asigna
            # - Si tenía otro usuario y ahora viene uno distinto → reasigna (token pudo “migrar”)
            if user and (token_obj.user_id != getattr(user, "id", None)):
                token_obj.user = user

            token_obj.save(update_fields=["device_os", "active", "user", "last_used"])
            action = "actualizado"
        except ExpoPushToken.DoesNotExist:
            token_obj = ExpoPushToken.objects.create(
                token=token,
                device_os=device_os,
                active=True,
                user=user if user else None,
            )
            action = "creado"

        user_info = f"usuario {token_obj.user_id} ({token_obj.user.email})" if token_obj.user_id else "sin usuario"
        print(f"✅ Push token {action} para {user_info}")

        return Response({"detail": "Token de push actualizado."}, status=200)


class SocialProfileView(APIView):
    """
    Devuelve el perfil social de cualquier usuario (con sus publicaciones/productos).
    - /social/profile/me/            -> perfil propio (requiere login)
    - /social/profile/<id>/ -> perfil público únicamente por UUID
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, identifier=None):
        target = self._resolve_target(request, identifier)

        profile = getattr(target, "social_profile", None)
        if profile is None:
            profile = UserProfile.objects.create(
                user=target,
                username=build_default_username(target),
                bio="",
            )
        else:
            desired_username = build_default_username(target)
            if profile.username != desired_username:
                profile.username = desired_username
                profile.save(update_fields=["username"])

        profile_data = UserProfileSerializer(profile, context={"request": request}).data

        products_qs = (
            Product.objects.filter(vendor=target, is_available=True)
            .select_related("vendor", "vendor__social_profile", "category")
            .prefetch_related("images")
            .order_by("-created_at")
        )
        posts_count = products_qs.count()
        products_data = ProductMinimalSerializer(
            products_qs[:24], many=True, context={"request": request}
        ).data

        is_following = False
        if request.user.is_authenticated and request.user != target:
            is_following = UserFollow.objects.filter(
                follower=request.user, following=target
            ).exists()

        # Construir location segura (solo ciudad, departamento, país)
        department = profile_data.get("department") or ""
        city = profile_data.get("city") or ""
        safe_location_parts = []
        if city:
            safe_location_parts.append(city)
        if department:
            safe_location_parts.append(department)
        if safe_location_parts:
            safe_location_parts.append("Colombia")
        safe_location = ", ".join(safe_location_parts) if safe_location_parts else None

        payload = {
            "id": target.id,
            "email": target.email,
            "first_name": target.first_name or "",
            "last_name": target.last_name or "",
            "full_name": target.full_name,
            "bio": profile_data.get("bio", ""),
            "location": safe_location,
            "department": department,
            "city": city,
            "avatar_url": profile_data.get("avatar_url"),
            "cover_url": profile_data.get("cover_url"),
            "followers_count": target.followers.count(),
            "following_count": target.following.count(),
            "posts_count": posts_count,
            "is_following": is_following,
            "products": products_data,
        }

        serializer = PublicProfileSerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _resolve_target(self, request, identifier):
        if identifier in (None, "", "me"):
            if not request.user.is_authenticated:
                raise PermissionDenied("Debes iniciar sesión para ver tu perfil.")
            return request.user

        # Buscar solo por UUID
        try:
            user = User.objects.filter(pk=identifier).first()
        except Exception:
            user = None

        if not user:
            raise NotFound("El perfil solicitado no existe.")

        return user


class FollowToggleView(APIView):
    """
    Activa o desactiva el seguimiento de un usuario.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = FollowActionSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        target = serializer.validated_data["target"]
        action = serializer.validated_data["action"]
        follower = request.user

        if action == "follow":
            UserFollow.objects.get_or_create(follower=follower, following=target)
            following = True
            
            # Notificar al usuario que fue seguido
            try:
                Notification.objects.create(
                    user=target,
                    title="Nuevo seguidor 👋",
                    body=f"{follower.first_name} {follower.last_name} comenzó a seguirte.",
                    data={
                        "type": "new_follower",
                        "follower_id": str(follower.id),
                        "follower_name": follower.full_name,
                    },
                )
                send_push(
                    title="Nuevo seguidor 👋",
                    body=f"{follower.first_name} comenzó a seguirte.",
                    data={
                        "type": "new_follower",
                        "follower_id": str(follower.id),
                    },
                    user=target,
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error enviando notificación de seguidor: {e}")
        elif action == "unfollow":
            UserFollow.objects.filter(follower=follower, following=target).delete()
            following = False
        else:  # toggle
            relation, created = UserFollow.objects.get_or_create(
                follower=follower, following=target
            )
            if created:
                following = True
            else:
                relation.delete()
                following = False

        data = {
            "following": following,
            "followers_count": target.followers.count(),
            "following_count": follower.following.count(),
        }
        return Response(data, status=status.HTTP_200_OK)


class FollowersListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        target = self._get_target_user(request)
        search = request.query_params.get("search", "").strip()

        qs = (
            User.objects.filter(following__following=target)
            .select_related("social_profile")
            .distinct()
            .order_by("first_name", "last_name")
        )

        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )

        paginator = MediumSetPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        context = self._serializer_context(request, page)
        serializer = FollowListEntrySerializer(page, many=True, context=context)
        response = paginator.get_paginated_response(serializer.data)
        response.data["counts"] = {
            "followers": target.followers.count(),
            "following": target.following.count(),
        }
        response.data["owner"] = {
            "id": str(target.id),
            "full_name": target.full_name,
        }
        return response

    def _get_target_user(self, request):
        identifier = (
            request.query_params.get("user_id")
            or request.query_params.get("user")
            or request.query_params.get("target")
        )
        if identifier:
            user = resolve_user_identifier(identifier)
            if user:
                return user
            raise NotFound("El perfil solicitado no existe.")
        if request.user.is_authenticated:
            return request.user
        raise PermissionDenied("Debes indicar un usuario para consultar seguidores.")

    def _serializer_context(self, request, page):
        viewer_ids = set()
        if request.user.is_authenticated and page:
            ids = [user.id for user in page]
            if ids:
                viewer_ids = set(
                    UserFollow.objects.filter(
                        follower=request.user, following_id__in=ids
                    ).values_list("following_id", flat=True)
                )
        return {"request": request, "viewer_following_ids": viewer_ids}


class FollowingListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        target = self._get_target_user(request)
        search = request.query_params.get("search", "").strip()

        qs = (
            User.objects.filter(followers__follower=target)
            .select_related("social_profile")
            .distinct()
            .order_by("first_name", "last_name")
        )

        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )

        paginator = MediumSetPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        context = self._serializer_context(request, page)
        serializer = FollowListEntrySerializer(page, many=True, context=context)
        response = paginator.get_paginated_response(serializer.data)
        response.data["counts"] = {
            "followers": target.followers.count(),
            "following": target.following.count(),
        }
        response.data["owner"] = {
            "id": str(target.id),
            "full_name": target.full_name,
        }
        return response

    def _get_target_user(self, request):
        identifier = (
            request.query_params.get("user_id")
            or request.query_params.get("user")
            or request.query_params.get("target")
        )
        if identifier:
            user = resolve_user_identifier(identifier)
            if user:
                return user
            raise NotFound("El perfil solicitado no existe.")
        if request.user.is_authenticated:
            return request.user
        raise PermissionDenied("Debes indicar un usuario para consultar seguidos.")

    def _serializer_context(self, request, page):
        viewer_ids = set()
        if request.user.is_authenticated and page:
            ids = [user.id for user in page]
            if ids:
                viewer_ids = set(
                    UserFollow.objects.filter(
                        follower=request.user, following_id__in=ids
                    ).values_list("following_id", flat=True)
                )
        return {"request": request, "viewer_following_ids": viewer_ids}


class DiscoverPeopleView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        viewer = request.user if request.user.is_authenticated else None
        search = request.query_params.get("search", "").strip()

        qs = (
            User.objects.filter(is_active=True)
            .select_related("social_profile")
            .order_by("-created_at")
        )
        if viewer:
            qs = qs.exclude(pk=viewer.pk)

        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )

        paginator = MediumSetPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        context = self._serializer_context(request, page)
        serializer = FollowListEntrySerializer(page, many=True, context=context)
        response = paginator.get_paginated_response(serializer.data)
        if viewer:
            response.data["counts"] = {
                "followers": viewer.followers.count(),
                "following": viewer.following.count(),
            }
        return response

    def _serializer_context(self, request, page):
        viewer_ids = set()
        if request.user.is_authenticated and page:
            ids = [user.id for user in page]
            if ids:
                viewer_ids = set(
                    UserFollow.objects.filter(
                        follower=request.user, following_id__in=ids
                    ).values_list("following_id", flat=True)
                )
        return {"request": request, "viewer_following_ids": viewer_ids}

class NotificationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        limit_param = request.query_params.get("limit")
        try:
            limit = int(limit_param) if limit_param is not None else 50
        except (TypeError, ValueError):
            limit = 50
        limit = max(1, min(limit, 100))

        notifications_qs = request.user.notifications.order_by("-created_at")[:limit]
        payload = [
            {
                "id": notif.id,
                "title": notif.title,
                "body": notif.body,
                "data": notif.data or {},
                "created_at": notif.created_at.isoformat(),
                "read": notif.read,
            }
            for notif in notifications_qs
        ]
        return Response({"results": payload})


class NotificationMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, notification_id):
        notif = get_object_or_404(
            Notification, pk=notification_id, user=request.user
        )
        if not notif.read:
            notif.read = True
            notif.save(update_fields=["read"])
        return Response({"read": True})


class NotificationMarkAllView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.notifications.filter(read=False).update(read=True)
        return Response({"marked": True})


class NotificationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, notification_id):
        notif = get_object_or_404(
            Notification, pk=notification_id, user=request.user
        )
        notif.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AccountDeleteView(APIView):
    """
    DELETE /api/delete/account/<uuid>/  — ruta de las versiones anteriores de la app.
    Usa el mismo flujo que /api/users/me/ (registro, revocación y anonimización si hay pedidos).
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        if pk != request.user.pk:          # evita borrar cuentas ajenas
            raise Http404
        try:
            delete_account(request.user, source=DeletedAccountRecord.Source.APP, request=request)
        except AccountDeletionBlocked as blocked:
            return Response({"detail": blocked.message, "code": blocked.code}, status=409)
        return Response(status=204)


N8N_SHARED_TOKEN = "n8n_9c7b2f1a5d6e4c3b"
class IsN8NHeader(permissions.BasePermission):
    message = "Missing X-N8N-Token header."

    def has_permission(self, request, view):
        token = request.headers.get("X-N8N-Token", "").strip()
        if not token:
            return False
        if not secrets.compare_digest(token, N8N_SHARED_TOKEN):
            self.message = "Invalid X-N8N-Token header."
            return False
        return True

class N8NUserPagination(LimitOffsetPagination):
    default_limit = 200
    max_limit = 500



class N8NUserStageListView(APIView):
    """
    Vista unificada para obtener usuarios con todos sus datos de stage.
    Devuelve la lista completa de usuarios con email/phone + datos de stage (subject, html, sms).

    Nota: los usuarios que ya completaron el ciclo (stage >= 6) se excluyen
    completamente de la respuesta para evitar reenvíos involuntarios. Después
    de 3 días de haber alcanzado el stage 6, el ciclo se reinicia a 0
    automáticamente en la misma petición GET.

    Parámetros opcionales:
    - pending_only: Si es 'true', solo devuelve usuarios con mensajes pendientes
    - updated_since: Filtrar por fecha de actualización
    """
    permission_classes = [IsN8NHeader]
    authentication_classes = []
    STAGE_RESTART_AFTER_DAYS = 3

    def _restart_completed_cycles_if_due(self, now):
        """Reinicia en stage 0 usuarios que completaron el ciclo hace >= N días."""
        restart_before = now - timedelta(days=self.STAGE_RESTART_AFTER_DAYS)
        due_users = User.objects.filter(
            is_active=True,
            consent_notifications=True,
            stage__gte=6,
            last_sent_at__isnull=False,
            last_sent_at__lte=restart_before,
        ).only("id", "stage", "next_send_at", "last_sent_at")

        restarted = 0
        for user in due_users:
            user.restart_stage_cycle(now=now)
            restarted += 1
        return restarted

    def get(self, request):
        try:
            now = timezone.now()
            self._restart_completed_cycles_if_due(now)
            
            # Iniciar con todos los usuarios activos que tienen nombre completo
            qs = User.objects.filter(
                is_active=True,
                first_name__isnull=False,
                last_name__isnull=False,
            ).exclude(first_name='').exclude(last_name='')

            # Nunca devolvemos usuarios que ya completaron el ciclo (stage >= 6).
            # De esta forma N8N no los reenviará accidentalmente antes de que
            # pasen los 3 días y se reinicien automáticamente en stage 0.
            qs = qs.filter(stage__lt=6)

            # Filtro opcional: solo usuarios con mensajes pendientes
            pending_only = request.GET.get('pending_only', '').lower() == 'true'
            if pending_only:
                qs = qs.filter(
                    consent_notifications=True,
                    next_send_at__isnull=False,
                    next_send_at__lte=now,
                    # stage__lt=6 ya aplicado arriba
                )
            
            # Filtro por fecha de actualización
            updated_since = request.GET.get('updated_since')
            if updated_since:
                try:
                    parsed = parse_datetime(updated_since)
                    if not parsed:
                        return Response(
                            {"detail": "updated_since debe ser una fecha ISO válida."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    qs = qs.filter(updated_at__gte=parsed)
                except Exception:
                    return Response(
                        {"detail": "updated_since debe ser una fecha ISO válida."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            
            # Ordenar por fecha de próximo envío o creación
            qs = qs.order_by('-next_send_at', '-created_at')

            # Paginación
            paginator = N8NUserPagination()
            page = paginator.paginate_queryset(qs, request, view=self)
            serializer = N8NUserStageSerializer(page if page is not None else qs, many=True)
            
            # Filtrar usuarios sin email ni phone
            data = [
                item for item in serializer.data
                if item and (item.get("email") or item.get("phone"))
            ]
            
            if page is not None:
                return paginator.get_paginated_response(data)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            print(f"❌ N8NUserStageListView error: {exc}")
            return Response(
                {"detail": "N8N user stages error", "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



class N8NUserAdvanceView(APIView):
    """Vista para avanzar al siguiente stage de un usuario y enviar notificación push.

    - Si el usuario está en stage 6 y no han pasado 3 días desde el último envío,
      la petición devuelve un objeto con `blocked: True` y no avanza el stage.
    - Cuando se cumplen los 3 días el stage se reinicia a 0 y se envía un push con
      `restarted: True` en la respuesta.
    """
    permission_classes = [IsN8NHeader]
    authentication_classes = []

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)

            # Si ya completó todos los stages (6), verificar si han pasado 3 días para reiniciar
            if user.can_restart_stage_cycle(days=3):
                now = timezone.now()
                user.restart_stage_cycle(now=now)
                
                user_name = f"{user.first_name} {user.last_name}".strip().title()
                payload = build_stage_output(
                    {
                        "id": str(user.id),
                        "email": user.email,
                        "phone": user.phone,
                        "stage": user.stage,
                        "next_send_at": user.next_send_at.isoformat() if user.next_send_at else None,
                        "last_sent_at": user.last_sent_at.isoformat() if user.last_sent_at else None,
                    },
                    user_name=user_name,
                )
                
                # Enviar notificación push al reiniciar
                self._send_stage_push_notification(user, payload, restarted=True)
                
                return Response(
                    {
                        **payload,
                        "restarted": True,
                    },
                    status=status.HTTP_200_OK,
                )
            elif user.stage >= 6 and user.last_sent_at:
                now = timezone.now()
                days_since_last = (now - user.last_sent_at).days
                # Enviar push de "espera" según el día del ciclo bloqueado
                self._send_blocked_push_notification(user, days_since_last=days_since_last)
                # No han pasado 3 días aún: informamos a N8N para que lo bloquee.
                return Response(
                    {
                        "detail": f"Ciclo completado. Reinicio disponible en {max(0, 3 - days_since_last)} días.",
                        "id": str(user.id),
                        "stage": user.stage,
                        "blocked": True,                # marca explícita para que N8N no intente avanzar
                        "can_restart": days_since_last >= 3,
                        "days_since_last": days_since_last,
                    },
                    status=status.HTTP_200_OK,
                )

            # Avanzar al siguiente stage
            user.advance_schedule()
            print(f"🔍 Usuario {user.id} avanzado a stage: {user.stage}")
            
            user_name = f"{user.first_name} {user.last_name}".strip().title()
            payload = build_stage_output(
                {
                    "id": str(user.id),
                    "email": user.email,
                    "phone": user.phone,
                    "stage": user.stage,
                    "next_send_at": user.next_send_at.isoformat() if user.next_send_at else None,
                    "last_sent_at": user.last_sent_at.isoformat() if user.last_sent_at else None,
                },
                user_name=user_name,
            )
            print(f"🔍 Payload construido con stage: {payload.get('stage')}")
            
            # Enviar notificación push
            self._send_stage_push_notification(user, payload)

            return Response(payload, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            print(f"❌ N8NUserAdvanceView error: {exc}")
            return Response(
                {"detail": "error", "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _send_stage_push_notification(self, user: User, payload: dict, restarted: bool = False) -> None:
      try:
          has_active_tokens = user.push_tokens.filter(active=True).exists()
          if not has_active_tokens:
              print(f"ℹ️ Usuario {user.id} sin tokens push activos, omitiendo notificación")
              return

          if not user.consent_notifications:
              print(f"ℹ️ Usuario {user.id} sin consentimiento, omitiendo notificación")
              return

          from apps.utils.yuancity_stage_templates import build_stage_push_notification

          user_name = f"{user.first_name} {user.last_name}".strip().title()

          stage = int(getattr(user, "stage", 0) or 0)

          # ✅ Si es 6, no enviar push
          if stage >= 6:
              print(f"ℹ️ Usuario {user.id} en stage {stage} (ciclo completo), no se envía push")
              return

          # ✅ Para stage 1..5 usar template stage-1 (para que coincida con “lo que acaba de pasar”)
          push_stage = max(0, stage - 1)

          print(f"🔍 DEBUG push stage: user.stage={stage} payload.stage={payload.get('stage', None)} push_stage={push_stage}")

          push_notification = build_stage_push_notification(stage=push_stage, user_name=user_name)

          title = push_notification.get("title") or "Nuevos productos en YuanCity"
          body = push_notification.get("body") or "Tenemos algo especial para ti"

          push_data = {
              "type": "stage_update",
              "stage": stage,            # real
              "push_stage": push_stage,  # template usado
              "user_id": str(user.id),
              "restarted": restarted,
          }

          send_push(title=title, body=body, data=push_data, user=user)

          print(f"✅ Notificación push enviada a usuario {user.id} (stage {stage} push_stage {push_stage})")

      except Exception as exc:
          print(f"⚠️ Error al enviar push a usuario {user.id}: {exc}")

    def _send_blocked_push_notification(self, user: User, days_since_last: int = 0) -> None:
        """Envía una notificación push a usuarios bloqueados (stage 6) según el día de espera."""
        try:
            has_active_tokens = user.push_tokens.filter(active=True).exists()
            if not has_active_tokens:
                print(f"ℹ️ Usuario {user.id} sin tokens push activos, omitiendo push bloqueado")
                return

            if not user.consent_notifications:
                print(f"ℹ️ Usuario {user.id} sin consentimiento, omitiendo push bloqueado")
                return

            from apps.utils.yuancity_stage_templates import build_blocked_push_notification

            user_name = f"{user.first_name} {user.last_name}".strip().title()
            push_notification = build_blocked_push_notification(
                days_since_last=days_since_last,
                user_name=user_name,
            )

            title = push_notification.get("title") or "Nuevos productos en YuanCity"
            body = push_notification.get("body") or "Tenemos algo especial para ti"

            push_data = {
                "type": "stage_blocked",
                "stage": user.stage,
                "days_since_last": days_since_last,
                "user_id": str(user.id),
            }

            send_push(title=title, body=body, data=push_data, user=user)
            print(f"✅ Push bloqueado enviado a usuario {user.id} (día {days_since_last} de espera)")

        except Exception as exc:
            print(f"⚠️ Error al enviar push bloqueado a usuario {user.id}: {exc}")


class UnsubscribeView(APIView):
    """Vista pública para darse de baja de notificaciones por email"""
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @staticmethod
    def _extract_identifiers(request):
        email = (request.GET.get('email') or request.data.get('email') or '').strip()
        user_id = (
            request.GET.get('id')
            or request.GET.get('user_id')
            or request.GET.get('uid')
            or request.data.get('id')
            or request.data.get('user_id')
            or request.data.get('uid')
            or ''
        )
        user_id = str(user_id).strip()
        return email, user_id

    def get(self, request):
        """
        GET /api/user/unsubscribe/?email=user@example.com
        o
        GET /api/user/unsubscribe/?id=uuid
        """
        email, user_id = self._extract_identifiers(request)

        if not email and not user_id:
            return Response(
                {"detail": "Se requiere email o id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if user_id:
                user = User.objects.get(pk=user_id)
            else:
                user = User.objects.get(email__iexact=email)

            # Verificar si ya está desuscrito
            if not user.consent_notifications:
                return Response(
                    {
                        "detail": "Ya estás desuscrito",
                        "id": str(user.id),
                        "email": user.email,
                        "unsubscribed": True
                    },
                    status=status.HTTP_200_OK
                )

            return Response(
                {
                    "detail": "Usuario encontrado",
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": f"{user.first_name} {user.last_name}".strip(),
                    "unsubscribed": False
                },
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"detail": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as exc:
            print(f"❌ UnsubscribeView GET error: {exc}")
            return Response(
                {"detail": "Error al procesar solicitud", "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """
        POST /api/user/unsubscribe/
        Body: { "email": "user@example.com" } o { "id": "uuid" }
        """
        email, user_id = self._extract_identifiers(request)

        if not email and not user_id:
            return Response(
                {"detail": "Se requiere email o id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if user_id:
                user = User.objects.get(pk=user_id)
            else:
                user = User.objects.get(email__iexact=email)

            # Desuscribir al usuario
            user.consent_notifications = False
            user.next_send_at = None
            user.save(update_fields=['consent_notifications', 'next_send_at'])

            return Response(
                {
                    "detail": "Te has desuscrito exitosamente",
                    "id": str(user.id),
                    "email": user.email,
                    "unsubscribed": True
                },
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"detail": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as exc:
            print(f"❌ UnsubscribeView POST error: {exc}")
            return Response(
                {"detail": "Error al desuscribir", "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
