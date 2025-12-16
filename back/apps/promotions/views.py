# promotions/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Prefetch

from .models import Promotion
from .serializers import (
    PromotionListSerializer,
    PromotionDetailSerializer,
    PromotionDashboardSerializer,
    PromotionSuggestionSerializer,
)
from ..utils.pagination import SmallSetPagination
from apps.product.models import Product


class PromotionListAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        today = timezone.now().date()
        return (
            Promotion.objects
            .select_related("vendor")
            .filter(is_active=True)
            .filter(start_date__lte=today)
            .filter(end_date__gte=today)
            .filter(products__is_available=True)
            .prefetch_related(
                Prefetch('products', queryset=Product.objects.filter(is_available=True))
            )
            .distinct()
        )

    def get(self, request, *args, **kwargs):
        slug = request.query_params.get('slug')
        qs   = self.get_queryset()

        # Detalle
        if slug:
            promo = qs.filter(slug=slug).first()
            if not promo:
                return Response({"detail": "Promotion not found"}, status=status.HTTP_404_NOT_FOUND)
            data = PromotionDetailSerializer(promo, context={'request': request}).data
            suggestions_qs = qs.exclude(id=promo.id)
            if promo.vendor_id:
                suggestions_qs = suggestions_qs.filter(vendor=promo.vendor)
            suggestions = suggestions_qs[:6]
            data["suggested_promotions"] = PromotionSuggestionSerializer(
                suggestions, many=True, context={'request': request}
            ).data
            return Response(data)

        # Listado
        paginator  = SmallSetPagination()
        page       = paginator.paginate_queryset(qs, request, view=self)
        data       = PromotionListSerializer(page, many=True, context={'request': request}).data
        return paginator.get_paginated_response(data)


class PromotionDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self, request):
        qs = (
            Promotion.objects.select_related("vendor")
            .prefetch_related(
                Prefetch("products", queryset=Product.objects.select_related("vendor"))
            )
            .order_by("-start_date")
        )
        if request.user.rol == "vendor":
            qs = qs.filter(vendor=request.user)
        return qs.distinct()

    def get_object(self, request, pk):
        return get_object_or_404(self.get_queryset(request), pk=pk)

    def get(self, request, pk=None):
        qs = self.get_queryset(request)
        if pk:
            promo = self.get_object(request, pk)
            serializer = PromotionDashboardSerializer(
                promo, context={"request": request}
            )
            return Response(serializer.data)

        paginator = SmallSetPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        serializer = PromotionDashboardSerializer(
            page, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if request.user.rol != "vendor" and not request.user.is_staff:
            return Response(
                {"detail": "Solo los vendedores pueden crear promociones."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = PromotionDashboardSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            promotion = serializer.save(vendor=request.user)
            return Response(
                PromotionDashboardSerializer(
                    promotion, context={"request": request}
                ).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if not pk:
            return Response({"detail": "Promotion ID required."}, status=400)
        promotion = self.get_object(request, pk)
        if request.user.rol == "vendor" and promotion.vendor != request.user:
            return Response({"detail": "No autorizado."}, status=403)

        serializer = PromotionDashboardSerializer(
            promotion, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if not pk:
            return Response({"detail": "Promotion ID required."}, status=400)
        promotion = self.get_object(request, pk)
        if request.user.rol == "vendor" and promotion.vendor != request.user:
            return Response({"detail": "No autorizado."}, status=403)
        promotion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
