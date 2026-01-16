# products/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Product
from .serializers import ProductSerializer,ProductMinimalSerializer
from ..utils.pagination import LargeSetPagination
from django.http import Http404
from django.db.models import Case, IntegerField, OuterRef, Q, Subquery, Sum, When
from django.utils import timezone
from apps.cart.models import CartItem
from apps.orders.models import OrderItem, Order


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


def apply_product_category_filter(queryset, category_id):
    if not category_id:
        return queryset
    return queryset.filter(
        Q(category__id=category_id)
        | Q(category__parent__id=category_id)
        | Q(category__parent__parent__id=category_id)
    )


def apply_orderitem_category_filter(queryset, category_id):
    if not category_id:
        return queryset
    return queryset.filter(
        Q(product__category__id=category_id)
        | Q(product__category__parent__id=category_id)
        | Q(product__category__parent__parent__id=category_id)
    )
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
            if product.vendor != user and not user.is_staff:
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

        if not (user.is_staff or product.vendor == user):
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        
        serializer = ProductSerializer(
            product, data=request.data, partial=False, context={'request': request}
        )
        if serializer.is_valid():
            prod = serializer.save(vendor=user)
            return Response(ProductSerializer(prod, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        user = request.user
        try:
            product = Product.objects.get(pk=kwargs['pk'])
        except Product.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not (user.is_staff or product.vendor == user):
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductSerializer(
            product, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            prod = serializer.save()
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
      category = request.query_params.get('category', '')
      vendor_id = request.query_params.get('vendor')
      qs = self.get_objects()
      if search:
        qs = qs.filter(name__icontains=search)
      if category:
        qs = qs.filter(category__id=category)
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
      top_products = []

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

    daily_offers_qs = (
      base_qs.filter(discount_percent__gt=0)
      .order_by('-discount_percent', '-updated_at')[:offers_limit]
    )
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
