"""
Vendedores cerca de un punto (tab «Comprar» de la app: lista y mapa).

GET /api/products/nearby/?lat=10.96&lng=-74.78&radius_km=25&category=<uuid>&search=texto&p=1

Una sola consulta paginada por vendedores (antes la app pedía 60 productos en cada movimiento del mapa
y los agrupaba en el teléfono). Cada vendedor trae sus primeros productos para la tarjeta y el mapa.
"""
from math import asin, cos, radians, sin, sqrt

from django.db.models import Count
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.user.models import UserProfile
from .models import Product
from .serializers import ProductMinimalSerializer
from .views import apply_product_category_filter, apply_product_search

EARTH_RADIUS_KM = 6371.0
DEFAULT_RADIUS_KM = 25.0
MAX_RADIUS_KM = 300.0
PAGE_SIZE = 20
PRODUCTS_PER_SELLER = 6


def haversine_km(lat1, lng1, lat2, lng2):
    d_lat = radians(lat2 - lat1)
    d_lng = radians(lng2 - lng1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(a))


def _float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class NearbySellersAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        lat = _float(request.query_params.get("lat"))
        lng = _float(request.query_params.get("lng"))
        if lat is None or lng is None or not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return Response({"detail": "Envía lat y lng válidos."}, status=status.HTTP_400_BAD_REQUEST)
        radius = min(max(_float(request.query_params.get("radius_km")) or DEFAULT_RADIUS_KM, 1.0), MAX_RADIUS_KM)
        try:
            page = max(int(request.query_params.get("p", 1)), 1)
        except ValueError:
            page = 1

        # Productos visibles que cumplen el filtro: definen qué vendedores aparecen.
        products = Product.objects.filter(is_available=True, stock__gt=0)
        category_ids = request.query_params.getlist("category")
        if category_ids:
            products = apply_product_category_filter(products, category_ids)
        search = request.query_params.get("search", "").strip()
        if search:
            products = apply_product_search(products, search)

        # Prefiltro rectangular en la base de datos; la distancia exacta se calcula después.
        d_lat = radius / 111.0
        d_lng = radius / (111.0 * max(cos(radians(lat)), 0.01))
        profiles = (
            UserProfile.objects.filter(
                user__is_active=True,
                latitude__isnull=False,
                longitude__isnull=False,
                latitude__range=(lat - d_lat, lat + d_lat),
                longitude__range=(lng - d_lng, lng + d_lng),
                user_id__in=products.values("vendor_id"),
            )
            .select_related("user")
        )

        ranked = []
        for profile in profiles:
            distance = haversine_km(lat, lng, float(profile.latitude), float(profile.longitude))
            if distance <= radius:
                ranked.append((distance, profile))
        ranked.sort(key=lambda row: row[0])

        start = (page - 1) * PAGE_SIZE
        page_rows = ranked[start : start + PAGE_SIZE]
        vendor_ids = [profile.user_id for _, profile in page_rows]

        counts = dict(
            products.filter(vendor_id__in=vendor_ids)
            .values("vendor_id")
            .annotate(total=Count("id"))
            .values_list("vendor_id", "total")
        )
        by_vendor = {vendor_id: [] for vendor_id in vendor_ids}
        page_products = (
            products.filter(vendor_id__in=vendor_ids)
            .select_related("category")
            .prefetch_related("images")
            .order_by("-created_at")
        )
        for product in page_products:
            bucket = by_vendor[product.vendor_id]
            if len(bucket) < PRODUCTS_PER_SELLER:
                bucket.append(product)

        serializer_context = {"request": request}
        sellers = []
        for distance, profile in page_rows:
            user = profile.user
            avatar = None
            if profile.avatar:
                avatar = request.build_absolute_uri(profile.avatar.url)
            items = by_vendor.get(user.id, [])
            sellers.append(
                {
                    "id": str(user.id),
                    "full_name": f"{user.first_name} {user.last_name}".strip() or profile.username,
                    "avatar_url": avatar,
                    "city": profile.city,
                    "department": profile.department,
                    "country": profile.country,
                    "latitude": float(profile.latitude),
                    "longitude": float(profile.longitude),
                    "distance_km": round(distance, 2),
                    "products_count": counts.get(user.id, 0),
                    "products": [
                        {
                            "id": str(item.id),
                            "name": item.name,
                            "price": str(item.price),
                            "discount_percent": item.discount_percent,
                            "stock": item.stock,
                            "first_image": ProductMinimalSerializer(item, context=serializer_context).get_first_image(item),
                        }
                        for item in items
                    ],
                }
            )

        has_next = start + PAGE_SIZE < len(ranked)
        return Response(
            {
                "count": len(ranked),
                "radius_km": radius,
                "next_page": page + 1 if has_next else None,
                "sellers": sellers,
            }
        )
