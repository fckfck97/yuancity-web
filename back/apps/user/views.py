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
    N8NUserSerializer,
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
from datetime import datetime, time
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


def _parse_bool(value: str):
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in ("true", "1", "yes"):
        return True
    if normalized in ("false", "0", "no"):
        return False
    raise ValueError("Invalid boolean")


def _parse_dt(value: str):
    if not value:
        return None
    parsed = parse_datetime(value)
    if parsed is None:
        parsed_date = parse_date(value)
        if parsed_date is None:
            return None
        parsed = datetime.combine(parsed_date, time.min)
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


class N8NUserPagination(LimitOffsetPagination):
    default_limit = 200
    max_limit = 500


class N8NUserListView(APIView):
    permission_classes = [IsN8NHeader]
    authentication_classes = []

    def get(self, request):
        try:
            qs = User.objects.all().order_by("created_at")

            ids_param = request.query_params.get("ids")
            if ids_param:
                ids = [item.strip() for item in ids_param.split(",") if item.strip()]
                qs = qs.filter(id__in=ids)

            emails_param = request.query_params.get("emails")
            if emails_param:
                emails = [item.strip().lower() for item in emails_param.split(",") if item.strip()]
                qs = qs.filter(email__in=emails)

            is_active_param = request.query_params.get("is_active")
            if is_active_param is not None:
                try:
                    is_active = _parse_bool(is_active_param)
                except ValueError:
                    return Response(
                        {"detail": "is_active debe ser true/false/1/0."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                qs = qs.filter(is_active=is_active)

            created_since = request.query_params.get("created_since")
            if created_since:
                parsed = _parse_dt(created_since)
                if not parsed:
                    return Response(
                        {"detail": "created_since debe ser una fecha ISO válida."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                qs = qs.filter(created_at__gte=parsed)

            updated_since = request.query_params.get("updated_since")
            if updated_since:
                parsed = _parse_dt(updated_since)
                if not parsed:
                    return Response(
                        {"detail": "updated_since debe ser una fecha ISO válida."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                qs = qs.filter(updated_at__gte=parsed)

            paginator = N8NUserPagination()
            page = paginator.paginate_queryset(qs, request, view=self)
            serializer = N8NUserSerializer(page if page is not None else qs, many=True)
            data = [
                item for item in serializer.data
                if item.get("email") or item.get("phone")
            ]
            if page is not None:
                return paginator.get_paginated_response(data)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            print(f"❌ N8NUserListView error: {exc}")
            return Response(
                {"detail": "N8N users error", "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
  

class SocialLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        provider = request.data.get("provider")
        raw_token = request.data.get("id_token")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")

        if not provider or not raw_token:
            return Response({"detail": "Faltan parámetros"}, status=400)

        if provider == "google":
            try:
                payload = google_id_token.verify_oauth2_token(
                    raw_token,
                    google_requests.Request(),          # sin audience fija
                )
                if payload["aud"] not in settings.GOOGLE_CLIENT_IDS:
                    return Response({"detail": "audience no permitido"}, status=400)
            except ValueError:
                return Response({"detail": "Token Google inválido"}, status=400)

            email       = payload["email"]
            first_name  = payload.get("given_name", "")
            last_name   = payload.get("family_name", "")

        elif provider == "apple":
            # Descarga las claves públicas de Apple (cachea 24 h)
            jwks = requests.get("https://appleid.apple.com/auth/keys").json()   # :contentReference[oaicite:1]{index=1}
            header = jwt.get_unverified_header(raw_token)
            key = next((k for k in jwks["keys"] if k["kid"] == header["kid"]), None)
            if not key:
                return Response({"detail": "Clave Apple no encontrada"}, status=400)

            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
            try:
                payload = jwt.decode(
                    raw_token,
                    public_key,
                    algorithms=["RS256"],
                    audience=settings.APPLE_ALLOWED_AUDS,
                    issuer="https://appleid.apple.com",
                )
            except jwt.PyJWTError:
                return Response({"detail": "Token Apple inválido"}, status=400)

            email       = payload.get("email")
            first_name  = first_name
            last_name   = last_name

        else:
            return Response({"detail": "Proveedor no soportado"}, status=400)

        # Crear / actualizar usuario
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name":  last_name,
                "password":   strong_random_password(),
            },
        )
        return Response(build_tokens(user), status=200)
      
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
      
   
class OTPLoginRequestView(APIView):
  """
  POST /auth/login/otp/request/
    { "email": "..."}  ó  { "phone": "3001234567", "channel": "sms|whatsapp" }
  Crea usuario si no existe y envía OTP.
  """
  permission_classes = [permissions.AllowAny]

  @transaction.atomic
  def post(self, request):
    print(request.data)
    ser = OTPRequestSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    email   = ser.validated_data.get("email")
    phone   = ser.validated_data.get("phone")

    user = None
    created = False

    if email:
      email_norm = normalize_email(email)
      
      # Check for demo account
      if email_norm == "apple.revisor@yuancity.com" or email_norm == "google.revisor@yuancity.com" or email_norm == "huawei.revisor@yuancity.com":
        user = User.objects.filter(email=email_norm).first()
        if user:
          return Response(build_tokens(user), status=200)
      
      user, created = User.objects.get_or_create(
        email=email_norm,
        defaults={
          "password": strong_random_password(),
          "first_name": "",
          "last_name": "",
        },
      )
    else:
      phone_norm = normalize(phone)
      user = User.objects.filter(phone=phone_norm).first()
      if not user:
        pseudo_email = f"{phone_norm}@yuancity.com"
        user = User.objects.create_user(
          email=pseudo_email,
          password=strong_random_password(),
          phone=phone_norm,
          first_name="",
          last_name="",
        )
        created = True

    if created:
      user.rol = "client"
      user.save(update_fields=["rol"])

    # OTP
    otp = user.generate_otp()

    if email:
      send_mail(
        "Código de acceso a YuanCity",
        f"Tu código es: {otp}",
        settings.DEFAULT_FROM_EMAIL,
        [email],
      )
    else:
      send_sms_in_background(
        f"+{normalize(phone)}",
        f"Tu código de acceso a YuanCity es: {otp}",
      )

    return Response({"detail": "OTP enviado.", "is_new_user": created}, status=200)

class OTPLoginVerifyView(APIView):
  """
  POST /auth/login/otp/verify/
    { "identifier": "correo@dominio.com" ó "+573001234567", "otp": "12345678" }
  """
  permission_classes = [permissions.AllowAny]

  def post(self, request):
    ser = OTPVerifySerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    ident = ser.validated_data["identifier"]
    otp   = ser.validated_data["otp"]
    
    # localizar usuario
    if "@" in ident:                             # es un correo
      email_norm = normalize_email(ident)
      user = User.objects.filter(email__iexact=email_norm).first()
    else:                                        # es teléfono
      user = User.objects.filter(phone=normalize(ident)).first()

    if not user:
      print("No se encontró el usuario.")
      return Response({"detail": "Usuario no encontrado."}, status=404)

    # Check for demo account - skip OTP verification
    if hasattr(user, 'email') and (user.email == "apple.revisor@yuancity.com" or user.email ==  "google.revisor@yuancity.com" or user.email == "huawei.revisor@yuancity.com"):
      return Response(build_tokens(user), status=200)

    if user.otp != otp:
      return Response({"detail": "OTP inválido."}, status=400)
      
    # invalidar OTP y marcar verificado
    user.otp = None
    if not user.phone_verified and user.phone:
      user.phone_verified = True
    user.save(update_fields=["otp", "phone_verified"])

    return Response(build_tokens(user), status=200)



class OTPLoginRequestWebView(APIView):
    """
    POST /auth/login/otp/request/
      { "email": "usuario@dominio.com" }
    Envia OTP solo si el usuario existe, está activo y está autorizado para web.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = OTPRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        email_norm = normalize_email(ser.validated_data["email"])
        
        # Validar que el correo esté en la lista de autorizados para web
        if email_norm not in settings.WEB_ALLOWED_EMAILS:
            return Response(
                {"detail": "No tienes autorización para acceder a la plataforma web. Contacta al administrador."},
                status=403,
            )
        
        user = User.objects.filter(email=email_norm, is_active=True).first()

        if not user:
            return Response(
                {"detail": "Correo no autorizado."},
                status=403,
            )

        # Generar y enviar OTP
        otp = user.generate_otp("web")
        send_mail(
            "Código de acceso",
            f"Tu código es: {otp}",
            settings.DEFAULT_FROM_EMAIL,
            [email_norm],
        )

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
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        if pk != request.user.pk:          # evita borrar cuentas ajenas
            raise Http404
        request.user.delete()
        return Response(status=204)
