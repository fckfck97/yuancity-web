"""Sesión y eliminación de cuenta (app y web)."""

import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .deletion import AccountDeletionBlocked, client_ip, delete_account, deletion_blockers, has_commerce_history
from .models import AccountDeletionRequest, DeletedAccountRecord, ExpoPushToken, UserAccount
from .serializers import (
    AccountDeletionConfirmSerializer,
    AccountDeletionRequestSerializer,
    DeleteAccountSerializer,
)

logger = logging.getLogger(__name__)


class LogoutView(APIView):
    """
    POST /api/auth/logout/  { refresh, push_token? }
    Invalida el refresh token y desvincula el dispositivo de las notificaciones de esta cuenta.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        push_token = request.data.get("push_token")
        if push_token:
            ExpoPushToken.objects.filter(user=request.user, token=push_token).update(active=False)
        refresh = request.data.get("refresh")
        if refresh:
            try:
                RefreshToken(refresh).blacklist()
            except Exception:  # noqa: BLE001 - token vencido o ya invalidado: la sesión igual termina
                pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountDeletionStatusView(APIView):
    """
    GET /api/users/me/deletion/
    Lo que la app muestra antes de eliminar: si se puede, por qué no, y si se conservará un registro anónimo.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        blockers = deletion_blockers(user)
        return Response({
            "can_delete": not blockers,
            "blockers": blockers,
            "keeps_orders": has_commerce_history(user),
            "providers": sorted(set(user.social_identities.values_list("provider", flat=True))),
        })


class DeleteMyAccountView(APIView):
    """
    DELETE /api/users/me/  { reason?, apple_authorization_code?, google_revoked? }
    Revoca Google/Apple, deja trazabilidad y elimina la cuenta (o la anonimiza si tiene pedidos).
    """

    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request):
        serializer = DeleteAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            record = delete_account(
                request.user,
                source=DeletedAccountRecord.Source.APP,
                reason=data.get("reason", ""),
                request=request,
                apple_authorization_code=data.get("apple_authorization_code"),
                google_revoked=data.get("google_revoked", False),
            )
        except AccountDeletionBlocked as blocked:
            return Response({"detail": blocked.message, "code": blocked.code}, status=status.HTTP_409_CONFLICT)
        return Response({
            "detail": "Tu cuenta fue eliminada.",
            "mode": record.mode,
            "platform_revocation": record.platform_revocation,
        })

    # Algunos clientes HTTP no envían cuerpo en DELETE.
    post = delete


class AccountDeletionRequestView(APIView):
    """Paso 1 del flujo web (sin sesión): envía un código de confirmación al correo de la cuenta."""

    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    THROTTLE_WINDOW_MINUTES = 15
    THROTTLE_MAX_REQUESTS = 3

    def post(self, request):
        serializer = AccountDeletionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].strip().lower()

        # Respuesta genérica: no revelamos si el correo está registrado.
        generic = {
            "detail": "Si el correo está registrado, te enviamos un código de confirmación.",
            "expires_in": AccountDeletionRequest.CODE_TTL_MINUTES * 60,
        }

        recent = AccountDeletionRequest.objects.filter(
            email=email,
            created_at__gte=timezone.now() - timedelta(minutes=self.THROTTLE_WINDOW_MINUTES),
        ).count()
        if recent >= self.THROTTLE_MAX_REQUESTS:
            return Response(
                {"detail": "Demasiadas solicitudes. Inténtalo de nuevo en unos minutos."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        user = UserAccount.objects.filter(email__iexact=email, is_active=True).first()
        if not user:
            # Se registra igual para que el límite de solicitudes aplique a correos inexistentes.
            AccountDeletionRequest.objects.create(
                email=email,
                status=AccountDeletionRequest.Status.CANCELLED,
                expires_at=timezone.now(),
                ip_address=client_ip(request),
            )
            return Response(generic)

        _, code = AccountDeletionRequest.issue(
            email=email,
            user=user,
            ip_address=client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        try:
            send_mail(
                f"Confirma la eliminación de tu cuenta {settings.APP_NAME}",
                (
                    f"Tu código para eliminar la cuenta es: {code}\n\n"
                    f"Vence en {AccountDeletionRequest.CODE_TTL_MINUTES} minutos. "
                    "Si no solicitaste esto, ignora este correo: tu cuenta seguirá activa."
                ),
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
        except Exception:  # noqa: BLE001 - el correo no debe tumbar la solicitud
            logger.exception("No se pudo enviar el código de eliminación a %s", email)

        return Response(generic)


class AccountDeletionConfirmView(APIView):
    """Paso 2 del flujo web: valida el código y elimina la cuenta."""

    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request):
        serializer = AccountDeletionConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].strip().lower()
        code = serializer.validated_data["otp"]
        reason = serializer.validated_data.get("reason", "")

        deletion_request = (
            AccountDeletionRequest.objects.select_for_update()
            .filter(email=email, status=AccountDeletionRequest.Status.PENDING)
            .order_by("-created_at")
            .first()
        )
        invalid = Response({"detail": "Código inválido o vencido. Solicita uno nuevo."}, status=400)
        if not deletion_request or not deletion_request.is_usable:
            return invalid

        if not deletion_request.check_code(code):
            deletion_request.attempts += 1
            if deletion_request.attempts >= AccountDeletionRequest.MAX_ATTEMPTS:
                deletion_request.status = AccountDeletionRequest.Status.CANCELLED
            deletion_request.save(update_fields=("attempts", "status"))
            return invalid

        user = deletion_request.user or UserAccount.objects.filter(email__iexact=email, is_active=True).first()
        if not user:
            return invalid

        try:
            with transaction.atomic():
                delete_account(user, source=DeletedAccountRecord.Source.WEB, reason=reason, request=request)
                # Con borrado completo la FK quedó en NULL (SET_NULL); se refleja en memoria.
                deletion_request.user = None
                deletion_request.status = AccountDeletionRequest.Status.COMPLETED
                deletion_request.completed_at = timezone.now()
                deletion_request.reason = reason
                deletion_request.code_hash = ""
                deletion_request.save(update_fields=("status", "completed_at", "reason", "code_hash", "user"))
        except AccountDeletionBlocked as blocked:
            return Response({"detail": blocked.message, "code": blocked.code}, status=status.HTTP_409_CONFLICT)

        return Response({"detail": "Tu cuenta fue eliminada. Lamentamos verte partir."})
