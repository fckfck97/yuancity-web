try:
    import stripe
    StripeError = stripe.error.StripeError
except ImportError:  # pragma: no cover - entorno sin Stripe instalado
    stripe = None

    class StripeError(Exception):
        """
        Fallback para entornos donde la librería de Stripe no está instalada.
        """

        pass

from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cart.models import Cart, CartItem
from apps.coupons.models import FixedPriceCoupon, PercentageCoupon
from apps.orders.models import Order, OrderItem, OrderChatMessage, Countries
from apps.category.models import Category
from apps.product.models import Product
from apps.product.serializers import ProductSerializer
from apps.reviews.models import Review
from apps.user.utils.push import send_push
from apps.user.utils.jwt import build_tokens
from apps.user.utils.password import strong_random_password
from apps.user.models import Notification, UserAccount as User
from apps.payment.models import VendorPayout, VendorBankAccount
from apps.payment.serializers import (
    VendorBankAccountSerializer,
    VendorPayoutSerializer,
    FinanceOrderSerializer,
    FinancePortalLoginSerializer,
    FinanceVendorPayoutSerializer,
    FinancePayoutStatusSerializer,
)
from apps.payment.utils import (
    add_business_days,
    refresh_payout_statuses,
    summarize_amount,
)

from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
import uuid
import logging
from django.utils import timezone
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

# Validar que la clave de Stripe esté configurada
if not settings.STRIPE_SECRET_KEY:
    logger.critical("STRIPE_SECRET_KEY no está configurada en las variables de entorno")
elif stripe is None:
    logger.warning("Stripe SDK no está instalado. Los pagos con tarjeta no estarán disponibles.")
else:
    stripe.api_key = settings.STRIPE_SECRET_KEY
    logger.info("Stripe API key configurada correctamente")

CURRENCY = "COP"
BUYER_TAX_RATE = Decimal("0.15")
SELLER_FEE_RATE = Decimal("0.15")
DELIVERY_NAME = "Entrega a domicilio"
DELIVERY_TIME = "Estamos coordinando el envío"
DELIVERY_PRICE = Decimal("0.00")
STATUS_PUSH_MESSAGES = {
    Order.OrderStatus.not_processed: (
        "Pedido recibido 📦",
        "Tu pedido ha sido recibido y pronto será procesado.",
    ),
    Order.OrderStatus.processed: (
        "Pedido en preparación 📦",
        "El vendedor está preparando tu orden.",
    ),
    Order.OrderStatus.shipping: (
        "Pedido en camino 🚚",
        "Nuestro equipo coordina la entrega en tu dirección.",
    ),
    Order.OrderStatus.delivered: (
        "Pedido completado 🎉",
        "¡Gracias por tu compra! Esperamos que disfrutes tu pedido.",
    ),
    Order.OrderStatus.cancelled: (
        "Pedido cancelado ❌",
        "Tu pedido fue cancelado. Si tienes dudas, contáctanos.",
    ),
}




def _stripe_metadata_base(channel: str = "mobile_app"):
    """
    Metadata común para identificar las órdenes generadas por YuanCity.
    """
    environment_label = "production" if not settings.DEBUG else "development"
    return {
        "platform": "yuancity",
        "channel": channel,
        "environment": environment_label,
        "backend": "django",
    }


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _format_money(value: Decimal) -> str:
    # Para COP no hay centavos - retornar entero sin decimales
    return format(int(_quantize(value)), "d")


def _calculate_subtotals(cart_items, include_breakdown=False):
    original = Decimal("0.00")
    discounted = Decimal("0.00")
    breakdown = []

    for cart_item in cart_items:
        count = Decimal(cart_item.count)
        unit_price = Decimal(cart_item.product.price)
        original_line = unit_price * count
        discount_percent = Decimal(cart_item.product.discount_percent or 0)
        multiplier = Decimal("1.00") - (discount_percent / Decimal("100"))
        if multiplier < Decimal("0.00"):
            multiplier = Decimal("0.00")

        final_unit_price = _quantize(unit_price * multiplier)
        line_total = _quantize(final_unit_price * count)

        original += original_line
        discounted += line_total

        if include_breakdown:
            breakdown.append(
                {
                    "cart_item": cart_item,
                    "unit_price": unit_price,
                    "final_unit_price": final_unit_price,
                    "line_total": line_total,
                    "discount_percent": discount_percent,
                    "count": int(cart_item.count),
                }
            )

    original = _quantize(original)
    discounted = _quantize(discounted)

    if include_breakdown:
        return original, discounted, breakdown
    return original, discounted


def _apply_coupon(total: Decimal, coupon_name: str):
    applied = ""
    normalized = coupon_name.strip() if coupon_name else ""

    if normalized:
        if FixedPriceCoupon.objects.filter(name__iexact=normalized).exists():
            coupon = FixedPriceCoupon.objects.get(name__iexact=normalized)
            discount_amount = Decimal(coupon.discount_price)
            if discount_amount < total:
                total -= discount_amount
                applied = coupon.name
        elif PercentageCoupon.objects.filter(name__iexact=normalized).exists():
            coupon = PercentageCoupon.objects.get(name__iexact=normalized)
            percentage = Decimal(coupon.discount_percentage)
            if Decimal("1") < percentage < Decimal("100"):
                total -= total * (percentage / Decimal("100"))
                applied = coupon.name

    if total < Decimal("0.00"):
        total = Decimal("0.00")

    return total, applied


def _resolve_shipping_address(user, data):
    profile = getattr(user, "social_profile", None)

    def _val(key, fallback_attr=None):
        value = data.get(key)
        if value:
            return str(value).strip()
        if fallback_attr and profile:
            fallback_value = getattr(profile, fallback_attr, "")
            if fallback_value:
                return str(fallback_value).strip()
        return ""

    address_line_1 = _val("address_line_1", "address_line")
    city = _val("city", "city")
    state_province_region = _val("state_province_region", "department")
    postal_zip_code = _val("postal_zip_code", None) or "000000"
    country_region = (
        _val("country_region", None)
        or getattr(profile, "country", "")
        or Order._meta.get_field("country_region").default
        or Countries.Colombia
    )
    instructions = (
        data.get("address_line_2")
        or data.get("pickup_notes")
        or getattr(profile, "location", "")
        or ""
    ).strip()

    missing = []
    if not address_line_1:
        missing.append("dirección")
    if not city:
        missing.append("ciudad")
    if not state_province_region:
        missing.append("departamento")

    if missing:
        raise ValueError(
            f"Completa la {' y '.join(missing)} para coordinar la entrega."
        )

    return {
        "address_line_1": address_line_1,
        "address_line_2": instructions,
        "city": city,
        "state_province_region": state_province_region,
        "postal_zip_code": postal_zip_code,
        "country_region": country_region,
    }


def _get_cart_with_items(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    cart_items = CartItem.objects.filter(cart=cart).select_related("product")
    return cart, cart_items


def _is_admin_user(user):
    return bool(
        getattr(user, "is_staff", False)
        or getattr(user, "is_superuser", False)
        or getattr(user, "rol", "") == "admin"
    )


def _month_start(value):
    return value.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _add_months(value, months):
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return value.replace(year=year, month=month, day=1)


class CheckoutSummaryView(APIView):
    """
    GET /api/payment/checkout/summary/?coupon=<nombre>
    Devuelve totales, impuestos, ahorros (sin crear orden aún).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        coupon_name = str(request.query_params.get("coupon", "")).strip()

        try:
            cart, cart_items = _get_cart_with_items(user)

            if not cart_items.exists():
                return Response(
                    {"error": "Necesitas tener artículos en el carrito"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            for cart_item in cart_items:
                product = cart_item.product
                if not Product.objects.filter(id=product.id).exists():
                    return Response(
                        {"error": "Un producto del carrito ya no está disponible"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if int(cart_item.count) > int(getattr(product, "stock", 0)):
                    return Response(
                        {"error": f"No hay suficiente stock para {product.name}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            original_total, discounted_subtotal = _calculate_subtotals(cart_items)
            total_after_coupon, applied_coupon = _apply_coupon(
                discounted_subtotal, coupon_name
            )

            estimated_tax = _quantize(total_after_coupon * BUYER_TAX_RATE)
            total_amount = _quantize(total_after_coupon + estimated_tax + DELIVERY_PRICE)
            savings_from_discounts = original_total - discounted_subtotal
            if savings_from_discounts < Decimal("0.00"):
                savings_from_discounts = Decimal("0.00")

            return Response(
                {
                    "currency": CURRENCY,
                    "discounted_subtotal": _format_money(discounted_subtotal),
                    "total_amount": _format_money(total_amount),
                    "estimated_tax": _format_money(estimated_tax),
                    "savings_from_discounts": _format_money(savings_from_discounts),
                    "coupon_name": applied_coupon,
                },
                status=status.HTTP_200_OK,
            )

        except InvalidOperation:
            return Response(
                {"error": "Error al calcular los totales"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Checkout summary error: {e}")
            return Response(
                {"error": "Ocurrió un error al obtener la información del pago"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PaymentSheetView(APIView):
    """
    POST /api/payment/checkout/payment-sheet/
    Body: { amount, checkout }
    Crea un Payment Intent en Stripe para usar con Payment Sheet nativo.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Validar que Stripe esté configurado
        if not settings.STRIPE_SECRET_KEY:
            logger.error("STRIPE_SECRET_KEY no configurada")
            return Response(
                {"error": "Stripe no está configurado correctamente en el servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if stripe is None:
            logger.error("Stripe SDK no disponible en el entorno actual")
            return Response(
                {"error": "Stripe no está disponible en este entorno"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
        user = request.user
        data = request.data
        metadata_base = _stripe_metadata_base()

        amount = data.get("amount")
        checkout = data.get("checkout", {})

        # Validar monto
        try:
            amount_decimal = Decimal(str(amount))
            if amount_decimal <= 0:
                return Response(
                    {"error": "El monto debe ser mayor a 0"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, InvalidOperation):
            return Response(
                {"error": "Monto inválido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar datos de contacto
        full_name = checkout.get("full_name", "").strip()
        telephone = checkout.get("telephone_number", "").strip()

        if not full_name or not telephone:
            return Response(
                {"error": "Datos de contacto incompletos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Para COP: Stripe maneja centavos internamente aunque COP no los usa en la práctica
        # Multiplicar por 100 porque Stripe divide por 100 automáticamente
        # Ejemplo: 66080 pesos → enviamos 6608000 → Stripe muestra $66,080.00 COP
        amount_in_cents = int(amount_decimal * 100)

        # Validar monto mínimo de Stripe para COP (~2000 pesos = 200000 centavos)
        if amount_in_cents < 200000:
            return Response(
                {"error": "El monto mínimo es de $2,000 COP"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Crear customer en Stripe
            customer = stripe.Customer.create(
                name=full_name,
                phone=telephone,
                address={
                    "line1": checkout.get("address_line_1", ""),
                    "line2": checkout.get("address_line_2", ""),
                    "city": checkout.get("city", ""),
                    "state": checkout.get("state_province_region", ""),
                    "postal_code": checkout.get("postal_zip_code", "000000"),
                    "country": checkout.get("country_region", "CO"),
                },
                metadata={
                    **metadata_base,
                    "user_id": str(user.id),
                    "coupon": checkout.get("coupon_name", ""),
                    "notes": checkout.get("pickup_notes", ""),
                },
            )

            # Crear Ephemeral Key
            ephemeral_key = stripe.EphemeralKey.create(
                customer=customer.id,
                stripe_version="2025-11-17.clover",
            )

            # Crear Payment Intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency="cop",
                customer=customer.id,
                automatic_payment_methods={"enabled": True},
                metadata={
                    **metadata_base,
                    "user_id": str(user.id),
                    "checkout_data": str(checkout),
                },
                description=f"Pedido Yuan City - {full_name}",
            )

            return Response(
                {
                    "paymentIntent": payment_intent.client_secret,
                    "ephemeralKey": ephemeral_key.secret,
                    "customer": customer.id,
                    "publishableKey": settings.STRIPE_PUBLISHABLE_KEY,
                },
                status=status.HTTP_200_OK,
            )

        except StripeError as exc:
            logger.error(f"Error creando Payment Intent: {exc}")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class StripeIntentView(APIView):
    """
    POST /api/payment/checkout/stripe-intent/
    Body: { amount, currency, items, coupon_name, checkout }
    Crea una PaymentIntent en Stripe y retorna client_secret.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        payload = request.data
        metadata_base = _stripe_metadata_base()

        if stripe is None:
            logger.error("Stripe SDK no disponible en el entorno actual")
            return Response(
                {"error": "Stripe no está disponible en este entorno"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        amount = Decimal(str(payload.get("amount", "0")))
        raw_currency = payload.get("currency", CURRENCY)
        currency = (raw_currency or CURRENCY).lower()
        items = payload.get("items", [])
        coupon_name = payload.get("coupon_name", "")
        checkout_data = payload.get("checkout") or {}
        pickup_notes = checkout_data.get("pickup_notes", "")

        telephone_number = (
            str(checkout_data.get("telephone_number") or "").strip()
            or getattr(user, "phone", "")
        )
        if not telephone_number:
            return Response(
                {"error": "Debes proporcionar un teléfono de contacto"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        full_name = (
            str(checkout_data.get("full_name") or "").strip()
            or user.get_full_name()
            or user.email
        )

        try:
            shipping_data = _resolve_shipping_address(
                user,
                {
                    **checkout_data,
                    "pickup_notes": pickup_notes,
                },
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"detail": "Monto inválido"}, status=400)

        # Recalcular el total en el backend usando items del carrito
        try:
            cart, cart_items = _get_cart_with_items(user)
            if not cart_items.exists():
                return Response(
                    {"error": "Carrito vacío"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            for cart_item in cart_items:
                product = cart_item.product
                if not Product.objects.filter(id=product.id).exists():
                    return Response(
                        {"error": "Un producto del carrito ya no está disponible"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if int(cart_item.count) > int(getattr(product, "stock", 0)):
                    return Response(
                        {"error": f"No hay suficiente stock para {product.name}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            original_total, discounted_subtotal = _calculate_subtotals(cart_items)
            total_after_coupon, applied_coupon = _apply_coupon(
                discounted_subtotal, coupon_name
            )
            
            estimated_tax = _quantize(total_after_coupon * BUYER_TAX_RATE)
            final_total = _quantize(total_after_coupon + estimated_tax + DELIVERY_PRICE)
            savings_from_discounts = original_total - discounted_subtotal
            if savings_from_discounts < Decimal("0.00"):
                savings_from_discounts = Decimal("0.00")
            
            # Para COP: Stripe maneja centavos internamente
            # Multiplicar por 100 para todas las monedas (Stripe divide internamente)
            if currency == 'cop':
                amount_in_minor = int(final_total * 100)
            else:
                amount_in_minor = int(final_total * 100)
            
            # Validar monto mínimo de Stripe para COP (2000 pesos = 200000 centavos)
            if currency == 'cop' and amount_in_minor < 200000:
                return Response(
                    {"error": "El monto mínimo es de $2,000 COP"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            logger.error(f"Error recalculando total: {e}")
            return Response(
                {"detail": "Error al recalcular el monto"}, 
                status=400
            )

        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_in_minor,
                currency=currency,
                automatic_payment_methods={"enabled": True},
                metadata={
                    **metadata_base,
                    "user_id": str(user.id),
                    "coupon": applied_coupon or "",
                    "items": ",".join([str(i.get("product_id")) for i in items]),
                    "full_name": full_name,
                    "phone": telephone_number,
                    "address": shipping_data["address_line_1"],
                    "city": shipping_data["city"],
                    "state": shipping_data["state_province_region"],
                    "postal_code": shipping_data["postal_zip_code"],
                    "country": shipping_data["country_region"],
                    "notes": pickup_notes,
                },
                description=f"Compra YuanCity ({full_name})",
            )
        except StripeError as exc:
            logger.error(f"Stripe error: {exc}")
            return Response({"detail": str(exc)}, status=400)

        summary_payload = {
            "currency": (raw_currency or CURRENCY).upper(),
            "discounted_subtotal": _format_money(discounted_subtotal),
            "total_amount": _format_money(final_total),
            "estimated_tax": _format_money(estimated_tax),
            "savings_from_discounts": _format_money(savings_from_discounts),
            "coupon_name": applied_coupon,
        }

        return Response(
            {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "summary": summary_payload,
            },
            status=status.HTTP_200_OK,
        )


class CheckoutCompleteView(APIView):
    """
    POST /api/payment/checkout/complete/
    Body: { payment_method, stripe_payment_intent_id, full_name, telephone_number,
            address_line_1, city, state_province_region, postal_zip_code, 
            country_region, coupon_name, pickup_notes }
    Valida la PaymentIntent en Stripe y crea la orden.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        payment_method = data.get("payment_method", "card")
        stripe_payment_intent_id = data.get("stripe_payment_intent_id")
        
        if payment_method not in ("card", "cash"):
            payment_method = "card"

        if payment_method == "card" and not stripe_payment_intent_id:
            return Response(
                {"error": "Falta la PaymentIntent de Stripe"}, 
                status=400
            )

        # Validar PaymentIntent en Stripe
        if payment_method == "card":
            if stripe is None:
                return Response(
                    {"error": "Stripe no está disponible en este entorno"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            try:
                intent = stripe.PaymentIntent.retrieve(stripe_payment_intent_id)
                if intent.status != "succeeded":
                    return Response(
                        {"error": "El pago no ha sido completado en Stripe"}, 
                        status=400
                    )
                metadata = getattr(intent, "metadata", None) or {}
                if hasattr(metadata, "get"):
                    platform_source = metadata.get("platform")
                elif isinstance(metadata, dict):
                    platform_source = metadata.get("platform")
                else:
                    platform_source = None
                if platform_source and platform_source != "yuancity":
                    return Response(
                        {"error": "Esta PaymentIntent no corresponde a YuanCity"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except StripeError as exc:
                logger.error(f"Error validando PaymentIntent: {exc}")
                return Response({"error": str(exc)}, status=400)

        coupon_name = str(data.get("coupon_name", "")).strip()
        pickup_notes = data.get("pickup_notes", "")
        full_name = data.get("full_name") or user.get_full_name() or user.email
        telephone_number = data.get("telephone_number")

        if not telephone_number:
            return Response(
                {"error": "Debes proporcionar un teléfono de contacto"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart, cart_items = _get_cart_with_items(user)

        if not cart_items.exists():
            return Response(
                {"error": "Necesitas tener artículos en el carrito"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for cart_item in cart_items:
            product = cart_item.product
            if not Product.objects.filter(id=product.id).exists():
                return Response(
                    {"error": "Un producto del carrito ya no está disponible"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            available_stock = int(getattr(product, "stock", 0))
            if cart_item.count > available_stock:
                return Response(
                    {"error": f"No hay suficiente stock para {product.name}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        cart_items = list(cart_items)

        original_total, discounted_subtotal, price_breakdown = _calculate_subtotals(
            cart_items, include_breakdown=True
        )
        total_after_coupon, applied_coupon = _apply_coupon(
            discounted_subtotal, coupon_name
        )

        try:
            estimated_tax = _quantize(total_after_coupon * BUYER_TAX_RATE)
            final_total = _quantize(total_after_coupon + estimated_tax + DELIVERY_PRICE)
        except InvalidOperation:
            return Response(
                {"error": "Error al calcular el total del pago"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            shipping_data = _resolve_shipping_address(
                user,
                {
                    **data,
                    "pickup_notes": pickup_notes,
                },
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                order_instance = Order.objects.create(
                    user=user,
                    transaction_id=uuid.uuid4(),
                    amount=final_total,
                    full_name=full_name,
                    address_line_1=shipping_data["address_line_1"],
                    address_line_2=shipping_data.get("address_line_2", ""),
                    city=shipping_data["city"],
                    state_province_region=shipping_data["state_province_region"],
                    postal_zip_code=shipping_data["postal_zip_code"],
                    country_region=shipping_data["country_region"],
                    telephone_number=telephone_number,
                    shipping_name=DELIVERY_NAME,
                    shipping_time=DELIVERY_TIME,
                    shipping_price=DELIVERY_PRICE,
                )

                vendor_totals = defaultdict(
                    lambda: {
                        "gross": Decimal("0.00"),
                        "fee": Decimal("0.00"),
                        "net": Decimal("0.00"),
                        "items": 0,
                    }
                )

                for entry in price_breakdown:
                    cart_item = entry["cart_item"]
                    product = cart_item.product
                    count = entry["count"]
                    final_unit_price = entry["final_unit_price"]
                    line_total = entry["line_total"]
                    platform_fee = _quantize(line_total * SELLER_FEE_RATE)
                    vendor_net = _quantize(line_total - platform_fee)

                    new_stock = max(int(product.stock) - int(count), 0)
                    Product.objects.filter(id=product.id).update(
                        stock=new_stock, is_available=new_stock > 0
                    )

                    OrderItem.objects.create(
                        product=product,
                        order=order_instance,
                        name=product.name,
                        price=final_unit_price,
                        count=count,
                        platform_fee=platform_fee,
                        vendor_earnings=vendor_net,
                    )

                    if product.vendor_id:
                        vendor_data = vendor_totals[product.vendor_id]
                        vendor_data["gross"] += line_total
                        vendor_data["fee"] += platform_fee
                        vendor_data["net"] += vendor_net
                        vendor_data["items"] += count

                if vendor_totals:
                    for vendor_id, totals in vendor_totals.items():
                        VendorPayout.objects.create(
                            vendor_id=vendor_id,
                            order=order_instance,
                            gross_amount=_quantize(totals["gross"]),
                            platform_fee=_quantize(totals["fee"]),
                            net_amount=_quantize(totals["net"]),
                            items_count=totals["items"],
                        )

                CartItem.objects.filter(cart=cart).delete()
                Cart.objects.filter(pk=cart.pk).update(total_items=0)

                # Notificar al comprador
                try:
                    Notification.objects.create(
                        user=user,
                        title="¡Pedido confirmado! 🎉",
                        body=f"Tu pedido #{order_instance.transaction_id} ha sido recibido y está siendo procesado.",
                        data={
                            "type": "order_created",
                            "order_id": str(order_instance.id),
                            "transaction_id": str(order_instance.transaction_id),
                            "amount": str(final_total),
                        },
                    )
                    send_push(
                        title="¡Pedido confirmado! 🎉",
                        body=f"Tu pedido ha sido recibido. Total: ${final_total:,.0f}",
                        data={
                            "type": "order_created",
                            "order_id": str(order_instance.id),
                            "transaction_id": str(order_instance.transaction_id),
                        },
                        user=user,
                    )
                except Exception as e:
                    logger.warning(f"Error enviando notificación al comprador: {e}")

                # Notificar a vendedores
                vendors_notified = set()
                for cart_item in cart_items:
                    vendor = cart_item.product.vendor
                    if vendor and vendor.id not in vendors_notified:
                        vendors_notified.add(vendor.id)
                        try:
                            items_count = vendor_totals.get(vendor.id, {}).get("items", 0)
                            
                            Notification.objects.create(
                                user=vendor,
                                title="¡Nueva venta! 🛍️",
                                body=(
                                    f"Tienes {items_count} producto(s) vendido(s). "
                                    "Contacta a la compradora para coordinar la entrega mientras activamos los envíos desde la app."
                                ),
                                data={
                                    "type": "new_sale",
                                    "order_id": str(order_instance.id),
                                    "items_count": items_count,
                                },
                            )
                            send_push(
                                title="¡Nueva venta! 🛍️",
                                body="Escríbele a la compradora para coordinar la entrega o envío.",
                                data={
                                    "type": "new_sale",
                                    "order_id": str(order_instance.id),
                                },
                                user=vendor,
                            )
                        except Exception as e:
                            logger.warning(f"Error notificando al vendedor {vendor.id}: {e}")

        except Exception as exc:
            logger.error(f"Error processing payment: {exc}")
            return Response(
                {"error": "No pudimos completar tu pedido. Intenta nuevamente."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Enviar email
        try:
            send_mail(
                "Detalles de tu Orden",
                f"Hola {full_name},\n\n¡Hemos recibido tu orden!\n\n"
                f"Te avisaremos cuando salga a entrega hacia tu dirección.\n\n"
                f"Puedes revisar el estado desde tu cuenta.\n\nEquipo YuanCity",
                "no-reply@yuancity.com",
                [user.email],
                fail_silently=True,
            )
        except Exception as exc:
            logger.warning(f"Email send error: {exc}")

        return Response(
            {
                "order_id": str(order_instance.id),
                "status": "confirmed",
                "transaction_id": str(order_instance.transaction_id),
                "amount": _format_money(final_total),
            },
            status=status.HTTP_201_CREATED,
        )


class VendorBankAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            account = request.user.bank_account
        except VendorBankAccount.DoesNotExist:
            account = None
        if not account:
            return Response({"account": None}, status=status.HTTP_200_OK)
        data = VendorBankAccountSerializer(account).data
        return Response({"account": data}, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        try:
            account = request.user.bank_account
        except VendorBankAccount.DoesNotExist:
            account = None
        if account:
            serializer = VendorBankAccountSerializer(account, data=request.data)
        else:
            serializer = VendorBankAccountSerializer(data=request.data)

        if serializer.is_valid():
            if serializer.instance:
                saved = serializer.save()
            else:
                saved = serializer.save(user=request.user)
            return Response(
                {"account": VendorBankAccountSerializer(saved).data},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorPayoutSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        refresh_payout_statuses(user)
        payouts = (
            VendorPayout.objects.filter(vendor=user)
            .select_related("order")
            .order_by("-created_at")
        )

        pending_qs = payouts.filter(
            status__in=[
                VendorPayout.Status.waiting_confirmation,
                VendorPayout.Status.pending_clearance,
            ]
        )
        available_qs = payouts.filter(status=VendorPayout.Status.available)
        released_qs = payouts.filter(status=VendorPayout.Status.released)

        next_release = (
            pending_qs.filter(available_on__isnull=False)
            .order_by("available_on")
            .values_list("available_on", flat=True)
            .first()
        )

        try:
            has_account = bool(user.bank_account)
        except VendorBankAccount.DoesNotExist:
            has_account = False

        summary_payload = {
            "pending_amount": _format_money(summarize_amount(pending_qs)),
            "available_amount": _format_money(summarize_amount(available_qs)),
            "in_transfer_amount": _format_money(summarize_amount(released_qs)),
            "next_release_on": next_release.isoformat() if next_release else None,
            "has_bank_account": has_account,
        }

        recent = payouts[:5]
        serializer = VendorPayoutSerializer(recent, many=True)

        return Response(
            {"summary": summary_payload, "payouts": serializer.data},
            status=status.HTTP_200_OK,
        )


class VendorPayoutWithdrawView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        user = request.user
        try:
            payout = VendorPayout.objects.select_related("order").get(
                id=pk, vendor=user
            )
        except VendorPayout.DoesNotExist:
            return Response(
                {"error": "No encontramos este pago."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payout.refresh_status()
        if payout.status != VendorPayout.Status.available:
            return Response(
                {
                    "error": "El pago aún no está disponible para retirar. Confirma la entrega o espera la fecha de liberación."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            account = user.bank_account
        except VendorBankAccount.DoesNotExist:
            return Response(
                {
                    "error": "Agrega una cuenta bancaria para poder solicitar retiros."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        snapshot = {
            "bank_name": account.bank_name,
            "account_type": account.account_type,
            "account_number": account.account_number,
            "account_holder_name": account.account_holder_name,
            "document_type": account.document_type,
            "document_number": account.document_number,
        }

        payout.status = VendorPayout.Status.released
        payout.released_at = timezone.now()
        payout.bank_account_snapshot = snapshot
        payout.save(
            update_fields=["status", "released_at", "bank_account_snapshot", "updated_at"]
        )

        return Response(
            {
                "success": "Estamos procesando tu retiro. El dinero se enviará a tu cuenta bancaria.",
                "payout": VendorPayoutSerializer(payout).data,
            },
            status=status.HTTP_200_OK,
        )


class FinancePortalLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = FinancePortalLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].strip().lower()


        user = User.objects.filter(email__iexact=email).first()
        if not user:
            user = User.objects.create_user(
                email=email,
                password=strong_random_password(),
                first_name="Finance",
                last_name="YuanCity",
            )

        updates = []
        if not user.is_staff:
            user.is_staff = True
            updates.append("is_staff")
        if not user.is_active:
            user.is_active = True
            updates.append("is_active")
        if user.rol != "admin":
            user.rol = "admin"
            updates.append("rol")

        if updates:
            user.save(update_fields=updates)

        tokens = build_tokens(user)
        payload = {
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
            },
        }
        return Response(payload, status=status.HTTP_200_OK)


class FinanceDashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not _is_admin_user(request.user):
            return Response(
                {"detail": "No tienes permisos para ver este panel."},
                status=status.HTTP_403_FORBIDDEN,
            )

        orders_total = Order.objects.count()
        orders_pending = Order.objects.exclude(
            status=Order.OrderStatus.delivered
        ).count()
        orders_delivered = Order.objects.filter(
            status=Order.OrderStatus.delivered
        ).count()
        orders_cancelled = Order.objects.filter(
            status=Order.OrderStatus.cancelled
        ).count()

        sales_total = Order.objects.aggregate(total=Sum("amount"))["total"] or Decimal(
            "0.00"
        )
        avg_order_value = (
            _quantize(sales_total / orders_total) if orders_total else Decimal("0.00")
        )
        items_sold = (
            OrderItem.objects.aggregate(total=Sum("count"))["total"] or 0
        )

        users_total = User.objects.count()
        users_active = User.objects.filter(is_active=True).count()
        users_vendors = User.objects.filter(rol="vendor").count()
        users_clients = User.objects.filter(rol="client").count()
        vendors_with_products = (
            Product.objects.values("vendor_id").distinct().count()
        )
        vendors_with_sales = (
            OrderItem.objects.exclude(product__vendor_id=None)
            .values("product__vendor_id")
            .distinct()
            .count()
        )
        products_total = Product.objects.count()
        products_available = Product.objects.filter(is_available=True).count()

        support_unread = OrderChatMessage.objects.filter(read=False).count()
        support_threads = (
            OrderChatMessage.objects.values("order_id").distinct().count()
        )

        waiting_qs = VendorPayout.objects.filter(
            status=VendorPayout.Status.waiting_confirmation
        )
        pending_qs = VendorPayout.objects.filter(
            status=VendorPayout.Status.pending_clearance
        )
        available_qs = VendorPayout.objects.filter(
            status=VendorPayout.Status.available
        )
        released_qs = VendorPayout.objects.filter(
            status=VendorPayout.Status.released
        )

        stats = {
            "orders_total": orders_total,
            "orders_pending": orders_pending,
            "orders_delivered": orders_delivered,
            "orders_cancelled": orders_cancelled,
            "payouts_waiting": waiting_qs.count(),
            "payouts_pending": pending_qs.count(),
            "payouts_available": available_qs.count(),
            "payouts_released": released_qs.count(),
            "pending_amount": str(summarize_amount(pending_qs)),
            "available_amount": str(summarize_amount(available_qs)),
            "sales_total": str(_quantize(sales_total)),
            "avg_order_value": str(_quantize(avg_order_value)),
            "items_sold": int(items_sold),
            "users_total": users_total,
            "users_active": users_active,
            "users_vendors": users_vendors,
            "users_clients": users_clients,
            "vendors_with_products": vendors_with_products,
            "vendors_with_sales": vendors_with_sales,
            "products_total": products_total,
            "products_available": products_available,
            "support_unread": support_unread,
            "support_threads": support_threads,
        }

        now = timezone.now()
        start_month = _add_months(_month_start(now), -5)
        month_labels = [
            "Ene",
            "Feb",
            "Mar",
            "Abr",
            "May",
            "Jun",
            "Jul",
            "Ago",
            "Sep",
            "Oct",
            "Nov",
            "Dic",
        ]
        sales_rows = (
            Order.objects.filter(date_issued__gte=start_month)
            .annotate(month=TruncMonth("date_issued"))
            .values("month")
            .annotate(sales=Sum("amount"), clients=Count("user", distinct=True))
            .order_by("month")
        )
        sales_map = {row["month"].date(): row for row in sales_rows}
        sales_series = []
        for offset in range(6):
            month_value = _add_months(start_month, offset)
            row = sales_map.get(month_value.date())
            sales_value = row["sales"] if row else 0
            clients_value = row["clients"] if row else 0
            sales_series.append(
                {
                    "month": month_labels[month_value.month - 1],
                    "sales": float(sales_value or 0),
                    "clients": int(clients_value or 0),
                }
            )

        category_rows = (
            Category.objects.annotate(total=Count("products"))
            .filter(total__gt=0)
            .order_by("-total")[:6]
        )
        category_breakdown = [
            {
                "name": row.name,
                "value": row.total,
            }
            for row in category_rows
        ]

        recent_orders = (
            Order.objects.select_related("user")
            .prefetch_related("orderitem_set__product__vendor")
            .order_by("-date_issued")[:5]
        )
        recent_payouts = (
            VendorPayout.objects.select_related("vendor", "order")
            .order_by("-created_at")[:5]
        )

        return Response(
            {
                "stats": stats,
                "sales_series": sales_series,
                "category_breakdown": category_breakdown,
                "recent_orders": FinanceOrderSerializer(recent_orders, many=True).data,
                "recent_payouts": FinanceVendorPayoutSerializer(
                    recent_payouts, many=True
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class AdminDashboardOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not _is_admin_user(request.user):
            return Response(
                {"detail": "No tienes permisos para ver estas órdenes."},
                status=status.HTTP_403_FORBIDDEN,
            )

        limit = request.query_params.get("limit")
        try:
            limit_value = int(limit) if limit else 100
        except ValueError:
            limit_value = 100
        limit_value = max(1, min(limit_value, 500))

        queryset = (
            Order.objects.select_related("user")
            .annotate(items_count=Count("orderitem"))
            .order_by("-date_issued")[:limit_value]
        )

        orders = []
        for order in queryset:
            customer_name = order.full_name
            if not customer_name and order.user_id:
                customer_name = order.user.full_name
            orders.append(
                {
                    "order_id": str(order.id),
                    "transaction_id": str(order.transaction_id),
                    "status": order.status,
                    "date_issued": order.date_issued.isoformat(),
                    "customer_name": customer_name or "",
                    "customer_email": getattr(order.user, "email", ""),
                    "order_total": format(order.amount, ".2f"),
                    "items_count": order.items_count or 0,
                }
            )

        return Response({"orders": orders}, status=status.HTTP_200_OK)


class AdminDashboardOrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, transaction_id, *args, **kwargs):
        if not _is_admin_user(request.user):
            return Response(
                {"detail": "No tienes permisos para ver esta orden."},
                status=status.HTTP_403_FORBIDDEN,
            )

        order = get_object_or_404(
            Order.objects.select_related("user").prefetch_related("orderitem_set"),
            transaction_id=transaction_id,
        )

        items = []
        for item in order.orderitem_set.all():
            items.append(
                {
                    "order_item_id": str(item.id),
                    "product_id": str(item.product_id) if item.product_id else None,
                    "name": item.name,
                    "price": format(item.price, ".2f"),
                    "count": item.count,
                }
            )

        customer_name = order.full_name
        if not customer_name and order.user_id:
            customer_name = order.user.full_name

        payload = {
            "order_id": str(order.id),
            "transaction_id": str(order.transaction_id),
            "status": order.status,
            "date_issued": order.date_issued,
            "full_name": customer_name or "",
            "customer_email": getattr(order.user, "email", ""),
            "telephone_number": order.telephone_number,
            "address_line_1": order.address_line_1,
            "address_line_2": order.address_line_2,
            "city": order.city,
            "state_province_region": order.state_province_region,
            "postal_zip_code": order.postal_zip_code,
            "country_region": order.country_region,
            "amount": str(order.amount),
            "payment_method": getattr(order, "payment_method", None),
            "items": items,
        }

        return Response({"order": payload}, status=status.HTTP_200_OK)


class AdminDashboardOrderStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        if not _is_admin_user(request.user):
            return Response(
                {"detail": "No tienes permisos para actualizar este pedido."},
                status=status.HTTP_403_FORBIDDEN,
            )

        order = get_object_or_404(Order, pk=pk)

        if order.status in [Order.OrderStatus.delivered, Order.OrderStatus.cancelled]:
            return Response(
                {
                    "error": (
                        "No se puede modificar un pedido que ya está "
                        f"{order.get_status_display()}"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_status = request.data.get("status")
        valid_status = [choice[0] for choice in Order.OrderStatus.choices]
        if new_status not in valid_status:
            return Response(
                {"error": "Estado no válido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        status_order = {
            Order.OrderStatus.not_processed: 1,
            Order.OrderStatus.processed: 2,
            Order.OrderStatus.shipping: 3,
            Order.OrderStatus.delivered: 4,
            Order.OrderStatus.cancelled: 5,
        }
        current_order = status_order.get(order.status, 0)
        new_order = status_order.get(new_status, 0)
        if new_status != Order.OrderStatus.cancelled and new_order < current_order:
            return Response(
                {"error": "No puedes retroceder el estado del pedido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = new_status
        update_fields = ["status", "updated_at"]
        if new_status == Order.OrderStatus.shipping and not order.shipped_at:
            order.shipped_at = timezone.now()
            update_fields.append("shipped_at")
        elif new_status == Order.OrderStatus.delivered and not order.completed_at:
            order.completed_at = timezone.now()
            update_fields.append("completed_at")

        order.save(update_fields=update_fields)

        message = STATUS_PUSH_MESSAGES.get(
            order.status,
            ("Actualización de pedido", f"El estado ahora es {order.status}"),
        )

        try:
            Notification.objects.create(
                user=order.user,
                title=message[0],
                body=message[1],
                data={
                    "type": "order_status",
                    "transaction_id": str(order.transaction_id),
                    "order_id": str(order.id),
                    "status": order.status,
                },
            )
            send_push(
                title=message[0],
                body=message[1],
                data={
                    "type": "order_status",
                    "transaction_id": str(order.transaction_id),
                    "order_id": str(order.id),
                    "status": order.status,
                },
                user=order.user,
            )
        except Exception as exc:
            logger.warning("No se pudo enviar push: %s", exc)

        return Response(
            {
                "success": "Estado actualizado correctamente",
                "status": order.status,
                "order_id": str(order.id),
                "transaction_id": str(order.transaction_id),
            },
            status=status.HTTP_200_OK,
        )


class AdminDashboardProductsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not _is_admin_user(request.user):
            return Response(
                {"detail": "No tienes permisos para ver productos."},
                status=status.HTTP_403_FORBIDDEN,
            )

        limit = request.query_params.get("limit")
        try:
            limit_value = int(limit) if limit else 100
        except ValueError:
            limit_value = 100
        limit_value = max(1, min(limit_value, 500))

        queryset = (
            Product.objects.select_related(
                "vendor", "vendor__social_profile", "category"
            )
            .prefetch_related("images")
            .order_by("-created_at")[:limit_value]
        )

        serializer = ProductSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)


class AdminDashboardReviewsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not _is_admin_user(request.user):
            return Response(
                {"detail": "No tienes permisos para ver reseñas."},
                status=status.HTTP_403_FORBIDDEN,
            )

        limit = request.query_params.get("limit")
        try:
            limit_value = int(limit) if limit else 100
        except ValueError:
            limit_value = 100
        limit_value = max(1, min(limit_value, 500))

        queryset = (
            Review.objects.select_related("product", "user", "order_item__order")
            .order_by("-date_created")[:limit_value]
        )

        data = []
        for review in queryset:
            user = review.user
            customer_name = ""
            if user:
                customer_name = getattr(user, "full_name", "") or user.email
            data.append(
                {
                    "id": str(review.id),
                    "product_id": str(review.product_id),
                    "product_name": review.product.name if review.product_id else "",
                    "rating": float(review.rating),
                    "comment": review.comment,
                    "date_created": review.date_created,
                    "user_name": customer_name,
                    "customer_name": customer_name,
                    "transaction_id": (
                        str(review.order_item.order.transaction_id)
                        if review.order_item_id
                        else None
                    ),
                }
            )

        return Response({"reviews": data}, status=status.HTTP_200_OK)


class AdminDashboardVendorsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not _is_admin_user(request.user):
            return Response(
                {"detail": "No tienes permisos para ver vendedores."},
                status=status.HTTP_403_FORBIDDEN,
            )

        limit = request.query_params.get("limit")
        try:
            limit_value = int(limit) if limit else 100
        except ValueError:
            limit_value = 100
        limit_value = max(1, min(limit_value, 500))

        # Filtramos usuarios que son vendors o que tienen productos
        queryset = (
            User.objects.annotate(products_count=Count("product"))
            .filter(Q(rol="vendor") | Q(products_count__gt=0))
            .select_related("bank_account")
            .order_by("-created_at")[:limit_value]
        )

        data = []
        for user in queryset:
            bank_info = None
            try:
                if hasattr(user, "bank_account") and user.bank_account:
                    bank_info = {
                        "bank_name": user.bank_account.bank_name,
                        "account_type": user.bank_account.get_account_type_display(),
                        "account_number": user.bank_account.account_number,
                        "account_holder_name": user.bank_account.account_holder_name,
                        "document_type": user.bank_account.get_document_type_display(),
                        "document_number": user.bank_account.document_number,
                    }
            except Exception:
                pass

            data.append(
                {
                    "user_id": str(user.id),
                    "full_name": user.full_name,
                    "email": user.email,
                    "phone": user.phone,
                    "products_count": user.products_count,
                    "bank_account": bank_info,
                    "created_at": user.created_at,
                }
            )

        return Response({"vendors": data}, status=status.HTTP_200_OK)


class FinanceOrderListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = (
            Order.objects.select_related("user")
            .prefetch_related("orderitem_set__product__vendor")
            .order_by("-date_issued")
        )

        status_filter = request.query_params.get("status")
        if status_filter:
            statuses = [value.strip() for value in status_filter.split(",") if value]
            queryset = queryset.filter(status__in=statuses)

        search_value = request.query_params.get("search", "").strip()
        if search_value:
            queryset = queryset.filter(
                Q(transaction_id__icontains=search_value)
                | Q(user__email__icontains=search_value)
                | Q(full_name__icontains=search_value)
            )

        limit = request.query_params.get("limit")
        try:
            limit_value = int(limit) if limit else 100
        except ValueError:
            limit_value = 100
        limit_value = max(1, min(limit_value, 500))
        queryset = queryset[:limit_value]

        serializer = FinanceOrderSerializer(queryset, many=True)
        return Response({"orders": serializer.data}, status=status.HTTP_200_OK)


class FinanceOrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(
            Order.objects.select_related("user").prefetch_related(
                "orderitem_set__product__vendor"
            ),
            pk=pk,
        )
        serializer = FinanceOrderSerializer(order)
        return Response({"order": serializer.data}, status=status.HTTP_200_OK)


class FinancePayoutListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = (
            VendorPayout.objects.select_related("vendor", "order")
            .order_by("-created_at")
        )

        status_filter = request.query_params.get("status")
        if status_filter:
            statuses = [value.strip() for value in status_filter.split(",") if value]
            queryset = queryset.filter(status__in=statuses)

        search_value = request.query_params.get("search", "").strip()
        if search_value:
            queryset = queryset.filter(
                Q(vendor__email__icontains=search_value)
                | Q(vendor__first_name__icontains=search_value)
                | Q(vendor__last_name__icontains=search_value)
                | Q(order__transaction_id__icontains=search_value)
            )

        limit = request.query_params.get("limit")
        try:
            limit_value = int(limit) if limit else 100
        except ValueError:
            limit_value = 100
        limit_value = max(1, min(limit_value, 500))
        queryset = queryset[:limit_value]

        serializer = FinanceVendorPayoutSerializer(queryset, many=True)
        return Response({"payouts": serializer.data}, status=status.HTTP_200_OK)


class FinancePayoutStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        payout = get_object_or_404(
            VendorPayout.objects.select_related("vendor"),
            pk=pk,
        )
        serializer = FinancePayoutStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        status_value = serializer.validated_data["status"]
        updates = ["status", "updated_at"]
        payout.status = status_value

        if "notes" in serializer.validated_data:
            payout.notes = serializer.validated_data["notes"]
            updates.append("notes")

        if "available_on" in serializer.validated_data:
            payout.available_on = serializer.validated_data["available_on"]
            updates.append("available_on")

        if serializer.validated_data.get("buyer_confirmed") and not payout.buyer_confirmed_at:
            payout.buyer_confirmed_at = timezone.now()
            updates.append("buyer_confirmed_at")

        if status_value == VendorPayout.Status.released:
            payout.released_at = timezone.now()
            updates.append("released_at")

            snapshot = payout.bank_account_snapshot or {}
            vendor = getattr(payout, "vendor", None)
            if vendor:
                try:
                    account = vendor.bank_account
                except VendorBankAccount.DoesNotExist:
                    account = None
                if account:
                    snapshot = {
                        "bank_name": account.bank_name,
                        "account_type": account.account_type,
                        "account_number": account.account_number,
                        "account_holder_name": account.account_holder_name,
                        "document_type": account.document_type,
                        "document_number": account.document_number,
                    }
            payout.bank_account_snapshot = snapshot
            updates.append("bank_account_snapshot")
        else:
            if payout.released_at:
                payout.released_at = None
                updates.append("released_at")

        payout.save(update_fields=list(dict.fromkeys(updates)))
        refreshed = VendorPayout.objects.select_related("vendor", "order").get(pk=payout.pk)
        return Response(
            {"payout": FinanceVendorPayoutSerializer(refreshed).data},
            status=status.HTTP_200_OK,
        )
