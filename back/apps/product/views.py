# products/views.py

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import Product
from .serializers import ProductSerializer, ProductMinimalSerializer
from ..utils.pagination import LargeSetPagination
from django.http import Http404
from django.db.models import Case, IntegerField, OuterRef, Q, Subquery, Sum, When
from django.utils import timezone
from apps.cart.models import CartItem
from apps.orders.models import OrderItem, Order
from apps.category.models import Category
from .utils.ai_search import (
    execute_product_search,
    product_catalog_index_for_ai,
    call_openai_product_search_interpreter,
    call_openai_product_result_filter,
)


def annotate_reservations(queryset):
    now = timezone.now()
    active_reservations = (
        CartItem.objects.filter(
            product=OuterRef("pk"),
            reserved_until__isnull=False,
            reserved_until__gt=now,
        )
        .order_by("-reserved_until")
    )
    return queryset.annotate(
        reservation_expires_at=Subquery(
            active_reservations.values("reserved_until")[:1]
        ),
        reservation_user_id=Subquery(
            active_reservations.values("cart__user_id")[:1]
        ),
    )


def _is_authorized(user):
    print(f"DEBUG AUTH: User={user.email}, Allowed={settings.WEB_ALLOWED_EMAILS}")
    if user.email and user.email.strip().lower() in settings.WEB_ALLOWED_EMAILS:
        return True
    return user.is_staff


def _normalize_category_ids(category_ids):
    if not category_ids:
        return []
    if isinstance(category_ids, (list, tuple, set)):
        raw_ids = category_ids
    else:
        raw_ids = [category_ids]
    return [cid for cid in raw_ids if cid not in ("", None, "all")]


def apply_product_category_filter(queryset, category_ids):
    category_ids = _normalize_category_ids(category_ids)
    if not category_ids:
        return queryset
    category_filter = Q()
    for category_id in category_ids:
        category_filter |= (
            Q(category__id=category_id)
            | Q(category__parent__id=category_id)
            | Q(category__parent__parent__id=category_id)
        )
    return queryset.filter(category_filter)


def apply_orderitem_category_filter(queryset, category_ids):
    category_ids = _normalize_category_ids(category_ids)
    if not category_ids:
        return queryset
    category_filter = Q()
    for category_id in category_ids:
        category_filter |= (
            Q(product__category__id=category_id)
            | Q(product__category__parent__id=category_id)
            | Q(product__category__parent__parent__id=category_id)
        )
    return queryset.filter(category_filter)
class ProductAPIView(APIView):
    """
    GET  /api/products/           -> list own products + total
    GET  /api/products/{pk}/      -> detail (only if owner or admin)
    POST /api/products/           -> create (only vendor)
    PUT  /api/products/{pk}/      -> update (only owner or admin)
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        base_qs = (
            Product.objects.all()
            .select_related('vendor', 'vendor__social_profile', 'category')
            .prefetch_related('images')
        )
        return annotate_reservations(base_qs)

    def get(self, request, *args, **kwargs):
        user = request.user

        # Detail view
        if 'pk' in kwargs:
            try:
                product = self.get_queryset().get(pk=kwargs['pk'])
            except Product.DoesNotExist:
                return Response(
                    {'detail': 'Product not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            # Users only see their own products
            if product.vendor != user and not _is_authorized(user):
                return Response(
                    {'detail': 'Not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = ProductSerializer(product, context={'request': request})
            return Response(serializer.data)

        # List view - filter to user's own products
        qs = self.get_queryset().filter(vendor=user)

        paginator = LargeSetPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        serializer = ProductSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
      
      
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            prod = serializer.save(vendor=user)
            
            return Response(
                ProductSerializer(prod, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        user = request.user
        try:
            product = Product.objects.get(pk=kwargs['pk'])
        except Product.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not (_is_authorized(user) or product.vendor == user):
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductSerializer(
            product, data=request.data, partial=False, context={'request': request}
        )
        if serializer.is_valid():
            # If authorized admin and not owner, preserve original vendor
            if product.vendor != user and _is_authorized(user):
                prod = serializer.save()
            else:
                prod = serializer.save(vendor=user)
            return Response(ProductSerializer(prod, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        user = request.user
        try:
            product = Product.objects.get(pk=kwargs['pk'])
        except Product.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not (_is_authorized(user) or product.vendor == user):
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductSerializer(
            product, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            # If authorized admin and not owner, preserve original vendor
            if product.vendor != user and _is_authorized(user):
                prod = serializer.save()
            else:
                prod = serializer.save(vendor=user)
            return Response(ProductSerializer(prod, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductListAPIView(APIView):
  """
  Lista productos públicos, permite búsqueda por nombre y filtrado por categoría.
  """
  permission_classes = [AllowAny]
  def get_objects(self):
    base_qs = (
      Product.objects.filter(is_available=True)
      .select_related('vendor', 'vendor__social_profile', 'category')
      .prefetch_related('images')
    )
    return annotate_reservations(base_qs)
    
  def get(self, request, *args, **kwargs):
    identificador = request.query_params.get('id')
    if identificador:
      product = self.get_objects().filter(pk=identificador).first()
      if not product:
        return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
      serializer = ProductSerializer(product, context={'request': request})
      return Response(serializer.data)
    
    else:
      search = request.query_params.get('search', '')
      category_ids = request.query_params.getlist('category')
      vendor_id = request.query_params.get('vendor')
      qs = self.get_objects()
      if search:
        qs = qs.filter(name__icontains=search)
      if category_ids:
        qs = apply_product_category_filter(qs, category_ids)
      if vendor_id:
        qs = qs.filter(vendor__id=vendor_id)
      paginator = LargeSetPagination()
      page = paginator.paginate_queryset(qs, request, view=self)
      serializer = ProductMinimalSerializer(page, many=True, context={'request': request})
      return paginator.get_paginated_response(serializer.data)


class ProductHighlightsAPIView(APIView):
  """
  Retorna clasificación top (más vendidos) y ofertas diarias.
  """
  permission_classes = [AllowAny]

  def get(self, request, *args, **kwargs):
    category_id = request.query_params.get('category')
    top_limit = int(request.query_params.get('top_limit', 6))
    offers_limit = int(request.query_params.get('offers_limit', 6))
    categories_limit = int(request.query_params.get('categories_limit', 6))

    base_qs = (
      Product.objects.filter(is_available=True, stock__gt=0)
      .select_related('vendor', 'vendor__social_profile', 'category')
      .prefetch_related('images')
    )
    base_qs = annotate_reservations(base_qs)
    base_qs = apply_product_category_filter(base_qs, category_id)

    sold_items = OrderItem.objects.filter(
      order__status__in=[
        Order.OrderStatus.processed,
        Order.OrderStatus.shipping,
        Order.OrderStatus.delivered,
      ],
      product__is_available=True,
      product__stock__gt=0,
    )
    sold_items = apply_orderitem_category_filter(sold_items, category_id)

    top_ids = list(
      sold_items.values('product')
      .annotate(total_sold=Sum('count'))
      .order_by('-total_sold')
      .values_list('product', flat=True)[:top_limit]
    )

    random_fallback_products = None
    if top_ids:
      preserved_order = Case(
        *[When(id=pk, then=pos) for pos, pk in enumerate(top_ids)],
        output_field=IntegerField(),
      )
      top_products_qs = base_qs.filter(id__in=top_ids).order_by(preserved_order)
      top_products = ProductMinimalSerializer(
        top_products_qs, many=True, context={'request': request}
      ).data
    else:
      # Si no hay ventas, mostrar productos al azar
      random_fallback_products = base_qs.order_by('?')[:top_limit]
      top_products = ProductMinimalSerializer(
        random_fallback_products, many=True, context={'request': request}
      ).data

    if top_ids:
      top_categories = [
        {
          'id': str(row['product__category__id']),
          'name': row['product__category__name'],
          'sold_count': row['total_sold'],
        }
        for row in sold_items.values(
          'product__category__id',
          'product__category__name',
        )
        .annotate(total_sold=Sum('count'))
        .order_by('-total_sold')[:categories_limit]
        if row.get('product__category__id')
      ]
    else:
      # Sin ventas: categorías al azar (derivadas de productos al azar)
      fallback_qs = random_fallback_products or base_qs.order_by('?')[:top_limit]
      seen = set()
      top_categories = []
      for product in fallback_qs:
        if not product.category_id or product.category_id in seen:
          continue
        seen.add(product.category_id)
        top_categories.append({
          'id': str(product.category_id),
          'name': product.category.name,
          'sold_count': 0,
        })
        if len(top_categories) >= categories_limit:
          break

    # Ofertas diarias: últimos publicados
    daily_offers_qs = base_qs.order_by('-created_at')[:offers_limit]
    daily_offers = ProductMinimalSerializer(
      daily_offers_qs, many=True, context={'request': request}
    ).data

    return Response({
      'top_classification': {
        'categories': top_categories,
        'products': top_products,
      },
      'daily_offers': daily_offers,
    })


class AIProductSearchAPIView(APIView):
    """
    Búsqueda de productos interpretada por IA (OpenAI).

    FLUJO:
    1. Usuario envía texto natural (?q=...).
    2. OpenAI interpreta el prompt y devuelve query optimizado + categorías.
    3. Se buscan CANDIDATOS amplios en la BD (nombre y descripción).
    4. OpenAI valida los candidatos y devuelve los UUIDs más relevantes.
    5. Se consultan esos UUIDs en la BD → resultados finales.

    Parámetros:
      ?q=<prompt>   texto libre (mín. 2 caracteres)
      &limit=<int>  máx resultados (1-50, default 20)

    Respuesta incluye objeto ``ai`` con:
      - answer:      mensaje breve para mostrar al usuario
      - suggestions: búsquedas relacionadas sugeridas
      - error:       mensaje de error si la IA falló (opcional)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        prompt = (request.query_params.get("q") or "").strip()
        if len(prompt) < 2:
            raise ValidationError({"q": "Ingresa al menos 2 caracteres para buscar."})

        per_limit = 20
        limit_param = request.query_params.get("limit")
        if limit_param not in (None, ""):
            try:
                per_limit = max(1, min(int(limit_param), 50))
            except (TypeError, ValueError):
                raise ValidationError({"limit": "Debe ser un entero positivo."})

        # ── PASO 1: Preparar categorías y contexto para la IA ───────────
        categories = list(
            Category.objects.values("id", "name").order_by("name")
        )
        # Serializar IDs como strings
        categories = [{"id": str(c["id"]), "name": c["name"]} for c in categories]

        catalog_index = product_catalog_index_for_ai(
            max_desc_chars=150,
            max_products=100,
        )

        # ── PASO 2: OpenAI interpreta el prompt ─────────────────────────
        ai_error = None
        try:
            ai_filters = call_openai_product_search_interpreter(
                user_prompt=prompt,
                categories=categories,
                catalog_index=catalog_index,
            )
        except Exception as exc:
            ai_error = str(exc)
            ai_filters = {
                "query": prompt,
                "category_ids": [],
                "suggestions": [],
                "answer": f"Buscando: {prompt}",
            }

        # ── PASO 3: Búsqueda amplia en BD para obtener candidatos ────────
        candidates_payload = execute_product_search(
            query=ai_filters["query"],
            category_ids=ai_filters.get("category_ids") or [],
            per_limit=50,
            request=request,
        )
        candidates = candidates_payload["results"]["products"]

        # ── PASO 4: OpenAI filtra candidatos y devuelve UUIDs ────────────
        filter_result = None
        try:
            filter_result = call_openai_product_result_filter(
                user_prompt=prompt,
                candidates=list(candidates),
            )
        except Exception as exc:
            ai_error = str(exc) if not ai_error else f"{ai_error}; {exc}"

        # ── PASO 5: Resultados finales por UUIDs seleccionados ───────────
        if filter_result and filter_result.get("selected_ids"):
            selected_ids = filter_result["selected_ids"]
            qs = (
                Product.objects.filter(
                    id__in=selected_ids,
                    is_available=True,
                    stock__gt=0,
                )
                .select_related("vendor", "vendor__social_profile", "category", "category__parent")
                .prefetch_related("images")
            )
            # Preservar orden de relevancia decidido por la IA
            from django.db.models import Case as DbCase, When as DbWhen, IntegerField as DbInt
            preserved = DbCase(
                *[DbWhen(id=pk, then=pos) for pos, pk in enumerate(selected_ids)],
                output_field=DbInt(),
            )
            qs = qs.order_by(preserved)
            items = list(qs[:per_limit])
            serialized = ProductMinimalSerializer(
                items, many=True, context={"request": request}
            ).data

            payload = {
                "query": ai_filters["query"],
                "limit": per_limit,
                "total": len(serialized),
                "results": {"products": list(serialized)},
                "ai": {
                    "answer": filter_result.get("answer") or ai_filters.get("answer") or "",
                    "suggestions": ai_filters.get("suggestions", []),
                },
            }
        else:
            # Fallback: usar candidatos originales limitados
            fallback = list(candidates)[:per_limit]
            payload = {
                "query": ai_filters["query"],
                "limit": per_limit,
                "total": len(fallback),
                "results": {"products": fallback},
                "ai": {
                    "answer": ai_filters.get("answer") or "",
                    "suggestions": ai_filters.get("suggestions", []),
                },
            }

        if ai_error:
            payload["ai"]["error"] = ai_error

        return Response(payload)
