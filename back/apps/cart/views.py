# apps/cart/views.py
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Cart, CartItem
from apps.product.models import Product
from apps.product.serializers import ProductMinimalSerializer
from .utils import (
    cleanup_expired_reservations,
    reservation_deadline,
    seconds_until,
    sync_cart_total,
)


# --------------------------------------------------
# helpers
# --------------------------------------------------
def _serialize_cart(cart):
    """
    Devuelve una lista de ítems con el formato:
    [
        {"id": <cart_item_id>, "count": <int>, "product": <ProductSerializer>}
    ]
    """
    cleanup_expired_reservations(cart=cart)
    now = timezone.now()
    items = (
        CartItem.objects.filter(cart=cart)
        .select_related("product")
        .order_by("product")
    )

    return [
        {
            "id": ci.id,
            "product_id": ci.product.id,
            "count": ci.count,
            "product": ProductMinimalSerializer(ci.product).data,
            "reservation_expires_at": ci.reserved_until.isoformat()
            if ci.reserved_until
            else None,
            "reservation_seconds_left": seconds_until(ci.reserved_until),
        }
        for ci in items
    ]


# --------------------------------------------------
# GET /api/cart/cart-items
# --------------------------------------------------
class GetItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response({"cart": _serialize_cart(cart)}, status=status.HTTP_200_OK)


# --------------------------------------------------
# POST /api/cart/add-item
# (versión simplificada que ya revisaste)
# --------------------------------------------------
class AddItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response(
                {"error": "product_id es requerido"}, status=status.HTTP_400_BAD_REQUEST
            )

        product = get_object_or_404(Product, id=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cleanup_expired_reservations(cart=cart, product=product)

        now = timezone.now()
        blocking_item = (
            CartItem.objects.select_related("cart")
            .filter(product=product, reserved_until__gt=now)
            .exclude(cart=cart)
            .first()
        )
        if blocking_item:
            return Response(
                {
                    "detail": "Esta prenda está reservada por otra persona en este momento.",
                    "reservation_expires_at": blocking_item.reserved_until,
                    "reservation_seconds_left": seconds_until(
                        blocking_item.reserved_until
                    ),
                },
                status=status.HTTP_409_CONFLICT,
            )

        # Verificar si el item ya existe en el carrito
        existing_item = CartItem.objects.filter(cart=cart, product=product).first()
        
        if existing_item:
            # Si ya existe, aumentar la cantidad
            new_count = existing_item.count + 1
            
            # Validar stock si existe el campo
            if hasattr(product, 'stock') and new_count > product.stock:
                return Response(
                    {"error": "Stock insuficiente"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            existing_item.count = new_count
            existing_item.reserved_until = reservation_deadline()
            existing_item.save(update_fields=["count", "reserved_until"])
            
            return Response({"cart": _serialize_cart(cart)}, status=status.HTTP_200_OK)
        else:
            # Si no existe, crear nuevo item
            CartItem.objects.create(
                cart=cart,
                product=product,
                count=1,
                reserved_until=reservation_deadline(),
            )
            sync_cart_total(cart)
            
            return Response({"cart": _serialize_cart(cart)}, status=status.HTTP_201_CREATED)


# --------------------------------------------------
# GET /api/cart/get-total
# --------------------------------------------------
class GetTotalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cleanup_expired_reservations(cart=cart)

        cart_items = CartItem.objects.filter(cart=cart).select_related("product")
        discounted_total = Decimal("0.00")
        regular_total = Decimal("0.00")

        for cart_item in cart_items:
            unit_price = Decimal(cart_item.product.price)
            regular_total += unit_price * cart_item.count

            discount_percent = Decimal(cart_item.product.discount_percent or 0)
            multiplier = Decimal("1.00") - (discount_percent / Decimal("100"))
            line_total = (unit_price * multiplier) * cart_item.count
            discounted_total += line_total

        def _fmt(value: Decimal) -> float:
            return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

        return Response(
            {
                "total_cost": _fmt(discounted_total),
                "total_compare_cost": _fmt(regular_total),
            },
            status=status.HTTP_200_OK,
        )


# --------------------------------------------------
# GET /api/cart/get-item-total
# --------------------------------------------------
class GetItemTotalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cleanup_expired_reservations(cart=cart)
        return Response(
            {"total_items": cart.total_items}, status=status.HTTP_200_OK
        )


# --------------------------------------------------
# PUT /api/cart/update-item
# --------------------------------------------------
class UpdateItemView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        product_id = request.data.get("product_id")
        count      = request.data.get("count")

        if not (product_id and isinstance(count, int)):
            return Response(
                {"error": "product_id y count son requeridos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = get_object_or_404(Product, id=product_id)
        cart    = get_object_or_404(Cart, user=request.user)
        item    = get_object_or_404(CartItem, cart=cart, product=product)
        cleanup_expired_reservations(cart=cart, product=product)

        # (opcional) validar stock
        # Reemplaza 'stock' por el nombre correcto del campo de stock en tu modelo Product si es diferente
        if count < 1 or count > product.stock:
            return Response(
                {"error": "Cantidad no permitida"}, status=status.HTTP_400_BAD_REQUEST
            )

        item.count = count
        item.reserved_until = reservation_deadline()
        item.save(update_fields=["count", "reserved_until"])

        return Response({"cart": _serialize_cart(cart)}, status=status.HTTP_200_OK)


# --------------------------------------------------
# DELETE /api/cart/remove-item
# --------------------------------------------------
class RemoveItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response(
                {"error": "product_id es requerido"}, status=status.HTTP_400_BAD_REQUEST
            )

        product = get_object_or_404(Product, id=product_id)
        cart    = get_object_or_404(Cart, user=request.user)
        cleanup_expired_reservations(cart=cart, product=product)
        item    = get_object_or_404(CartItem, cart=cart, product=product)

        item.delete()
        sync_cart_total(cart)

        return Response({"cart": _serialize_cart(cart)}, status=status.HTTP_200_OK)


# --------------------------------------------------
# DELETE /api/cart/empty-cart
# --------------------------------------------------
class EmptyCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        CartItem.objects.filter(cart=cart).delete()
        Cart.objects.filter(pk=cart.pk).update(total_items=0)

        return Response(
            {"success": "Cart emptied successfully"}, status=status.HTTP_200_OK
        )


# --------------------------------------------------
# PUT /api/cart/synch-cart
# --------------------------------------------------
class SynchCartView(APIView):
    """
    Sincroniza el carrito del dispositivo con el del backend.

    request.data = {
        "cart_items": [
            {"product_id": "<uuid>", "count": 2},
            ...
        ]
    }
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        incoming = request.data.get("cart_items", [])
        cart, _  = Cart.objects.get_or_create(user=request.user)
        cleanup_expired_reservations(cart=cart)
        now = timezone.now()

        for entry in incoming:
            pid   = entry.get("product_id")
            qty   = entry.get("count", 1)
            if not pid:
                continue

            product = Product.objects.filter(id=pid).first()
            if not product:
                continue

            blocking_item = (
                CartItem.objects.select_related("cart")
                .filter(product=product, reserved_until__gt=now)
                .exclude(cart=cart)
                .first()
            )
            if blocking_item:
                continue

            item, created = CartItem.objects.get_or_create(
                cart=cart, product=product, defaults={"count": qty}
            )
            if not created:
                # sumamos cantidades respetando stock
                max_stock = getattr(product, "stock", None)
                limit = (
                    max_stock
                    if isinstance(max_stock, int) and max_stock > 0
                    else item.count + qty
                )
                item.count = min(item.count + qty, limit)
                item.reserved_until = reservation_deadline()
                item.save(update_fields=["count", "reserved_until"])
            else:
                item.reserved_until = reservation_deadline()
                item.save(update_fields=["reserved_until"])

        sync_cart_total(cart)

        return Response(
            {"success": "Cart synchronized", "cart": _serialize_cart(cart)},
            status=status.HTTP_201_CREATED,
        )
