from django.core.paginator import EmptyPage, Paginator
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Case, ProductDraftConversation
from .utils.product_draft.service import (
    ask_openai as ask_product_draft_openai,
    build_reply as build_product_draft_reply,
    default_draft as default_product_draft,
    update_draft_with_validation as update_product_draft_with_validation,
)
from .serializers import CaseSerializer
from .utils.legal_chat.service import ask_legal_chat


class LegalChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get("session_id", "default_session")
        text = request.data.get("text", "").strip()

        if not text:
            return Response({"error": "El mensaje no puede estar vacío"}, status=400)

        try:
            reply = ask_legal_chat(text)
            return Response(
                {
                    "ai_response": {
                        "id": f"ai-{session_id}",
                        "text": reply,
                    }
                },
                status=200,
            )
        except Exception as exc:
            return Response(
                {"error": f"Error en la conversación: {str(exc)}"}, status=500
            )


class CaseListView(APIView):
    """
    Lista los casos creados desde el chat legal usando la paginación de Django.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self, user):
        if getattr(user, "rol", None) == "lawyer":
            return Case.objects.filter(assigned_lawyer=user)
        return Case.objects.filter(client=user)

    def get(self, request):
        queryset = self.get_queryset(request.user).order_by("-updated_at")
        try:
            page_number = int(request.query_params.get("page", "1"))
            if page_number < 1:
                raise ValueError
        except (TypeError, ValueError):
            page_number = 1

        try:
            page_size = int(request.query_params.get("page_size", "10"))
        except (TypeError, ValueError):
            page_size = 10
        page_size = max(1, min(page_size, 50))

        paginator = Paginator(queryset, page_size)
        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        serializer = CaseSerializer(page_obj.object_list, many=True, context={"request": request})
        payload = {
            "count": paginator.count,
            "page": page_obj.number,
            "page_size": paginator.per_page,
            "num_pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
            "previous_page": page_obj.previous_page_number() if page_obj.has_previous() else None,
            "results": serializer.data,
        }
        return Response(payload)


class ProductDraftChatAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        conversation_id = request.data.get("conversation_id")
        message = (request.data.get("message") or "").strip()
        locale = request.data.get("locale") or "es"

        if not conversation_id:
            return Response({"detail": "conversation_id requerido"}, status=400)
        if not message:
            return Response({"detail": "message requerido"}, status=400)

        conv, _ = ProductDraftConversation.objects.get_or_create(
            conversation_id=conversation_id,
            defaults={
                "draft": default_product_draft(),
                "next_field": "nombre",
            },
        )

        if conv.is_complete:
            return Response(
                {
                    "reply": "Este borrador ya fue completado.",
                    "draft": conv.draft,
                    "next_field": None,
                    "is_complete": True,
                }
            )

        try:
            args = ask_product_draft_openai(
                message=message,
                draft=conv.draft,
                next_field=conv.next_field,
                language=locale,
            )
        except Exception as exc:
            return Response(
                {"detail": f"Error al procesar el asistente: {exc}"},
                status=500,
            )

        result = update_product_draft_with_validation(
            conv.draft, conv.next_field, args, locale
        )

        conv.draft = result["draft"]
        conv.next_field = result["next_field"] or conv.next_field
        conv.is_complete = result["is_complete"]
        conv.save(update_fields=["draft", "next_field", "is_complete", "updated_at"])

        reply = build_product_draft_reply(result)

        return Response(
            {
                "reply": reply,
                "draft": conv.draft,
                "next_field": None if conv.is_complete else conv.next_field,
                "is_complete": conv.is_complete,
            }
        )


class CaseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Case, pk=pk)

    def has_access(self, request, case):
        user = request.user
        if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
            return True
        if case.client_id and case.client_id == user.id:
            return True
        if case.assigned_lawyer_id and case.assigned_lawyer_id == user.id:
            return True
        return False

    def get(self, request, pk):
        case = self.get_object(pk)
        if not self.has_access(request, case):
            return Response({"detail": "No tienes permiso para ver este caso."}, status=status.HTTP_403_FORBIDDEN)
        serializer = CaseSerializer(case, context={"request": request})
        return Response(serializer.data)

    def delete(self, request, pk):
        case = self.get_object(pk)
        if not self.has_access(request, case):
            return Response({"detail": "No tienes permiso para modificar este caso."}, status=status.HTTP_403_FORBIDDEN)

        if case.client_id != request.user.id:
            return Response(
                {"detail": "Sólo el cliente que creó el caso puede eliminarlo."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if case.status != "nuevo":
            return Response(
                {"detail": "Sólo puedes eliminar casos en estado 'nuevo'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        case.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
