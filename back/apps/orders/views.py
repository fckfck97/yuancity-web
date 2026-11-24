import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.http import Http404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import uuid

User = get_user_model()

from .models import Order, OrderItem, OrderChatMessage
from .serializers import OrderSerializer, OrderChatMessageSerializer
from apps.utils.pagination import MediumSetPagination
from apps.user.utils.push import send_push
from apps.user.models import Notification
from apps.payment.models import VendorPayout
from apps.payment.utils import add_business_days

logger = logging.getLogger(__name__)

STATUS_PUSH_MESSAGES = {
    Order.OrderStatus.not_processed: (
        "Pedido recibido 📦",
        "Tu pedido ha sido recibido y pronto será procesado. Te mantendremos informado.",
    ),
    Order.OrderStatus.processed: (
        "¡Estamos empacando tu pedido! 📦",
        "El vendedor está preparando tu orden con cuidado.",
    ),
    Order.OrderStatus.shipping: (
        "¡Tu pedido va en camino! 🚚",
        "Nuestro equipo coordina la entrega en tu dirección.",
    ),
    Order.OrderStatus.delivered: (
        "Pedido completado 🎉",
        "¡Gracias por tu compra! Esperamos que disfrutes tus nuevas prendas.",
    ),
    Order.OrderStatus.cancelled: (
        "Pedido cancelado ❌",
        "Tu pedido fue cancelado. Si tienes dudas, contáctanos.",
    ),
}
class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, transaction_id):
        try:
            return Order.objects.get(transaction_id=transaction_id)
        except Order.DoesNotExist:
            raise Http404

    def _has_order_access(self, user, order):
        if user.is_staff or user.is_superuser:
            return True
        if order.user_id == user.id:
            return True
        # Verificar si el usuario tiene productos en esta orden (es vendedor activo)
        return OrderItem.objects.filter(
            order=order,
            product__vendor=user,
        ).exists()

    def _can_edit_order(self, user):
        return user.is_staff or user.is_superuser
        
    def get(self, request,*args, **kwargs):
        if "pk" in kwargs:
            order = self.get_object(kwargs["pk"])
            if not self._has_order_access(request.user, order):
                return Response(
                    {'error': 'No tienes permiso para ver esta orden'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        else:
            user = request.user
            if user.is_staff or user.is_superuser:
                orders = Order.objects.all()
            else:
                # Obtener órdenes como comprador y como vendedor (si tiene productos)
                from django.db.models import Q
                orders = (
                    Order.objects
                    .filter(
                        Q(user=user) | Q(orderitem__product__vendor=user)
                    )
                    .distinct()
                )
            paginator = MediumSetPagination()
            result_page = paginator.paginate_queryset(orders, request)
            serializer = OrderSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
    
    def put(self, request, *args, **kwargs):
        order = self.get_object(kwargs["pk"])
        if not self._can_edit_order(request.user):
            return Response(
                {'error': 'Solo el equipo interno puede actualizar pedidos'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
ACTIVE_ORDER_STATUSES = (
    Order.OrderStatus.not_processed,
    Order.OrderStatus.processed,
    Order.OrderStatus.shipping,
)
ORDERS_PAGE_SIZE = 15


def order_page_params(request):
    """
    Paginación opcional (?p=1&page_size=15). Sin `p` se devuelve todo, como antes,
    para no romper las versiones publicadas de la app.
    """
    raw_page = request.query_params.get('p')
    if raw_page is None:
        return None
    try:
        page = max(int(raw_page), 1)
        size = min(max(int(request.query_params.get('page_size', ORDERS_PAGE_SIZE)), 1), 50)
    except ValueError:
        page, size = 1, ORDERS_PAGE_SIZE
    return page, size


def filter_orders_by_status(queryset, request, prefix=''):
    status_value = request.query_params.get('status')
    if request.query_params.get('active') in ('1', 'true'):
        return queryset.filter(**{f'{prefix}status__in': ACTIVE_ORDER_STATUSES})
    if status_value:
        return queryset.filter(**{f'{prefix}status': status_value})
    return queryset


class ListOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = self.request.user
        try:
            orders = filter_orders_by_status(Order.objects.order_by('-date_issued').filter(user=user), request)
            paging = order_page_params(request)
            total = None
            if paging:
                page, size = paging
                total = orders.count()
                orders = orders[(page - 1) * size : page * size]
            result = []

            for order in orders:
                item = {}
                item['status'] = order.status
                item['transaction_id'] = order.transaction_id
                item['amount'] = order.amount
                item['shipping_price'] = order.shipping_price
                item['date_issued'] = order.date_issued
                item['address_line_1'] = order.address_line_1
                item['address_line_2'] = order.address_line_2
                item['city'] = order.city
                item['state_province_region'] = order.state_province_region

                result.append(item)

            payload = {'orders': result}
            if paging:
                payload['count'] = total
                payload['next_page'] = page + 1 if page * size < total else None
            return Response(payload, status=status.HTTP_200_OK)
        except:
            return Response(
                {'error': 'Something went wrong when retrieving orders'},
                status=status.HTTP_404_NOT_FOUND
            )


class ListOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, transactionId, format=None):
        user = self.request.user
        try:
            order = Order.objects.get(transaction_id=transactionId)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order with this transaction ID does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        is_staff = user.is_staff or user.is_superuser
        is_buyer = order.user_id == user.id
        # Verificar si el usuario es vendedor de algún producto en esta orden
        is_vendor = OrderItem.objects.filter(
            order=order,
            product__vendor=user
        ).exists()

        if not any([is_staff, is_buyer, is_vendor]):
            return Response(
                {'error': 'No tienes permiso para consultar este pedido'},
                status=status.HTTP_403_FORBIDDEN
            )

        order_items = (
            OrderItem.objects.select_related('product')
            .order_by('-date_added')
            .filter(order=order)
        )

        # Si solo es vendedor (no comprador), limitar a sus productos
        if is_vendor and not (is_staff or is_buyer):
            order_items = order_items.filter(product__vendor=user)

        result = {
            'status': order.status,
            'transaction_id': order.transaction_id,
            'amount': order.amount,
            'buyer_confirmed_at': order.buyer_confirmed_at,
            'shipped_at': order.shipped_at,
            'completed_at': order.completed_at,
            'full_name': order.full_name,
            'address_line_1': order.address_line_1,
            'address_line_2': order.address_line_2,
            'city': order.city,
            'state_province_region': order.state_province_region,
            'postal_zip_code': order.postal_zip_code,
            'country_region': order.country_region,
            'telephone_number': order.telephone_number,
            'shipping_name': order.shipping_name,
            'shipping_time': order.shipping_time,
            'shipping_price': order.shipping_price,
            'date_issued': order.date_issued,
            'order_items': [],
        }

        for order_item in order_items:
                    result['order_items'].append(
                        {
                            'name': order_item.name,
                            'price': order_item.price,
                            'count': order_item.count,
                            'product_id': str(order_item.product.id),
                            'order_item_id': order_item.id,
                            'has_review': hasattr(order_item, 'review'),
                            'platform_fee': order_item.platform_fee,
                            'vendor_earnings': order_item.vendor_earnings,
                        }
                    )

        return Response({'order': result}, status=status.HTTP_200_OK)


class VendorOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        status_filter = request.query_params.get('status')

        items_qs = (
            OrderItem.objects
            .select_related('order', 'product', 'order__user')
            .filter(product__vendor=user)
            .order_by('-order__date_issued', '-date_added')
        )

        if status_filter:
            items_qs = items_qs.filter(order__status=status_filter)

        # Paginación opcional por pedido (no por producto): se eligen los ids de la página primero.
        paging = order_page_params(request)
        total_orders = None
        if paging:
            page, size = paging
            order_ids = list(
                Order.objects.filter(id__in=items_qs.values('order_id'))
                .order_by('-date_issued')
                .values_list('id', flat=True)
            )
            total_orders = len(order_ids)
            items_qs = items_qs.filter(order_id__in=order_ids[(page - 1) * size : page * size])

        orders_map = {}

        for order_item in items_qs:
            order = order_item.order
            if order.id not in orders_map:
                orders_map[order.id] = {
                    'order_id': str(order.id),
                    'transaction_id': str(order.transaction_id),
                    'status': order.status,
                    'date_issued': order.date_issued.isoformat(),
                    'customer_name': order.full_name,
                    'customer_email': getattr(order.user, 'email', ''),
                    'customer_phone': order.telephone_number,
                    'delivery_address': order.address_line_1,
                    'delivery_city': order.city,
                    'delivery_notes': order.address_line_2,
                    'order_total': format(order.amount, '.2f'),
                    'shipping_price': format(order.shipping_price, '.2f'),
                    'items': [],
                    'vendor_total': Decimal('0.00'),
                    'platform_fee_total': Decimal('0.00'),
                }

            entry = orders_map[order.id]
            vendor_amount = Decimal(order_item.vendor_earnings or 0)
            if vendor_amount <= 0:
                vendor_amount = Decimal(order_item.price) * order_item.count
            platform_fee = Decimal(order_item.platform_fee or 0)
            entry['vendor_total'] += vendor_amount
            entry['platform_fee_total'] += platform_fee
            entry['items'].append({
                'order_item_id': str(order_item.id),
                'product_id': str(order_item.product.id) if order_item.product_id else None,
                'name': order_item.name,
                'price': format(order_item.price, '.2f'),
                'count': order_item.count,
                'subtotal': format(vendor_amount, '.2f'),
                'platform_fee': format(platform_fee, '.2f'),
            })

        payout_map = {
            payout.order_id: payout
            for payout in VendorPayout.objects.filter(
                order_id__in=orders_map.keys(), vendor=user
            )
        }

        orders_list = []
        for entry in orders_map.values():
            payout = payout_map.get(uuid.UUID(entry['order_id']))
            if payout:
                entry['payout'] = {
                    'id': str(payout.id),
                    'status': payout.status,
                    'buyer_confirmed_at': payout.buyer_confirmed_at,
                    'available_on': payout.available_on,
                    'released_at': payout.released_at,
                    'can_withdraw': payout.status == VendorPayout.Status.available,
                    'net_amount': format(payout.net_amount, '.2f'),
                }
                entry['vendor_total'] = format(payout.net_amount, '.2f')
                entry['platform_fee_total'] = format(payout.platform_fee, '.2f')
            else:
                entry['payout'] = None
                entry['vendor_total'] = format(entry['vendor_total'], '.2f')
                entry['platform_fee_total'] = format(
                    entry['platform_fee_total'], '.2f'
                )
            entry['items_count'] = len(entry['items'])
            orders_list.append(entry)

        orders_list.sort(key=lambda o: o['date_issued'], reverse=True)

        payload = {'orders': orders_list}
        if paging:
            payload['count'] = total_orders
            payload['next_page'] = page + 1 if page * size < total_orders else None
        return Response(payload, status=status.HTTP_200_OK)


class VendorOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        try:
            order = (
                Order.objects
                .filter(id=pk, orderitem__product__vendor=user)
                .distinct()
                .get()
            )
        except Order.DoesNotExist:
            return Response(
                {'error': 'Pedido no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validar que el pedido no esté completado o cancelado
        if order.status in [Order.OrderStatus.delivered, Order.OrderStatus.cancelled]:
            return Response(
                {'error': f'No se puede modificar un pedido que ya está {order.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_status = request.data.get('status')
        valid_status = [choice[0] for choice in Order.OrderStatus.choices]

        if new_status not in valid_status:
            return Response(
                {'error': 'Estado no válido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar que no se retroceda en el proceso (excepto cancelar)
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
                {'error': 'No puedes retroceder el estado del pedido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        
        # Registrar timestamps según el estado
        update_fields = ['status', 'updated_at']
        if new_status == Order.OrderStatus.shipping and not order.shipped_at:
            order.shipped_at = timezone.now()
            update_fields.append('shipped_at')
        elif new_status == Order.OrderStatus.delivered and not order.completed_at:
            order.completed_at = timezone.now()
            update_fields.append('completed_at')
            
        order.save(update_fields=update_fields)

        # Preparar mensaje push con información del proceso
        message = STATUS_PUSH_MESSAGES.get(
            order.status,
            ("Actualización de pedido", f"El estado ahora es {order.status}"),
        )
        
        # Agregar información del proceso completo
        process_info = {
            "received": order.status != Order.OrderStatus.not_processed,
            "preparing": order.status in [
                Order.OrderStatus.processed,
                Order.OrderStatus.shipping,
                Order.OrderStatus.delivered
            ],
            "ready": order.status in [
                Order.OrderStatus.shipping,
                Order.OrderStatus.delivered
            ],
            "completed": order.status == Order.OrderStatus.delivered,
            "cancelled": order.status == Order.OrderStatus.cancelled,
        }

        try:
            # Guardar notificación en la base de datos
            Notification.objects.create(
                user=order.user,
                title=message[0],
                body=message[1],
                data={
                    "type": "order_status",
                    "transaction_id": str(order.transaction_id),
                    "order_id": str(order.id),
                    "status": order.status,
                    "process": process_info,
                },
            )
            
            # Enviar notificación push
            send_push(
                title=message[0],
                body=message[1],
                data={
                    "type": "order_status",
                    "transaction_id": str(order.transaction_id),
                    "order_id": str(order.id),
                    "status": order.status,
                    "process": process_info,
                },
                user=order.user,
            )
        except Exception as exc:
            logger.warning("No se pudo enviar push: %s", exc)

        return Response(
            {
                'success': 'Estado actualizado correctamente',
                'status': order.status,
                'order_id': str(order.id),
                'transaction_id': str(order.transaction_id),
                'process': process_info,
            },
            status=status.HTTP_200_OK
        )


CHAT_CLOSED_STATUSES = (Order.OrderStatus.delivered, Order.OrderStatus.cancelled)


def is_chat_open(order):
    return order.status not in CHAT_CLOSED_STATUSES


class OrderChatView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_order(self, transaction_id):
        try:
            return Order.objects.get(transaction_id=transaction_id)
        except Order.DoesNotExist:
            raise Http404

    def has_access(self, user, order):
        if user.is_staff or user.is_superuser:
            return True
        if order.user_id == user.id:
            return True
        return OrderItem.objects.filter(
            order=order,
            product__vendor=user,
        ).exists()

    def peer_for(self, user, order):
        """La otra persona del pedido (para el encabezado del chat). Sin correo."""
        if order.user_id == user.id:
            vendor_id = (
                OrderItem.objects.filter(order=order)
                .values_list("product__vendor_id", flat=True)
                .first()
            )
            peer = User.objects.filter(id=vendor_id).select_related("social_profile").first()
        else:
            peer = order.user
        if not peer:
            return None
        avatar = None
        profile = getattr(peer, "social_profile", None)
        if profile and profile.avatar:
            avatar = self.request.build_absolute_uri(profile.avatar.url)
        return {"id": str(peer.id), "full_name": (peer.full_name or "").strip(), "avatar_url": avatar}

    def get(self, request, transaction_id):
        order = self.get_order(transaction_id)
        if not self.has_access(request.user, order):
            return Response(
                {"detail": "No tienes permiso para ver este chat."},
                status=status.HTTP_403_FORBIDDEN,
            )
        messages = (
            order.chat_messages.select_related("sender").order_by("created_at")
        )
        # ?after=<fecha ISO>: solo lo nuevo (la app consulta cada pocos segundos con el chat abierto).
        after = parse_datetime(request.query_params.get("after") or "")
        if after:
            messages = messages.filter(created_at__gt=after)
        serializer = OrderChatMessageSerializer(
            messages, many=True, context={"request": request}
        )
        payload = {
            "messages": serializer.data,
            "chat_open": is_chat_open(order),
            "status": order.status,
        }
        if not after:
            payload["peer"] = self.peer_for(request.user, order)
            # Leídos de mis mensajes (para ✓✓) solo hace falta al abrir; luego viajan con cada mensaje.
        else:
            payload["read_ids"] = [
                str(pk)
                for pk in order.chat_messages.filter(sender=request.user, read=True)
                .order_by("-created_at")
                .values_list("id", flat=True)[:50]
            ]
        return Response(payload)

    def post(self, request, transaction_id):
        order = self.get_order(transaction_id)
        if not self.has_access(request.user, order):
            return Response(
                {"detail": "No tienes permiso para enviar mensajes en este chat."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # El chat sirve para cerrar la venta: solo mientras el pedido está en proceso.
        if not is_chat_open(order):
            return Response(
                {"detail": "Este pedido ya terminó: el chat está cerrado.", "code": "chat_closed"},
                status=status.HTTP_403_FORBIDDEN,
            )

        text = (request.data.get("text") or "").strip()
        image = request.FILES.get("image")
        audio = request.FILES.get("audio")
        audio_duration = request.data.get("audio_duration") or request.data.get(
            "audio_duration_ms"
        )

        if not any([text, image, audio]):
            return Response(
                {"detail": "Envía un mensaje, imagen o audio."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        duration_value = None
        if audio_duration:
            try:
                duration_value = int(float(audio_duration))
            except (TypeError, ValueError):
                duration_value = None

        message = OrderChatMessage.objects.create(
            order=order,
            sender=request.user,
            message=text,
            image=image,
            audio=audio,
            audio_duration=duration_value,
        )

        # Determinar el destinatario (comprador o vendedor)
        is_buyer = order.user_id == request.user.id
        if is_buyer:
            # El comprador envió el mensaje, notificar a los vendedores
            vendor_ids = set(
                OrderItem.objects.filter(order=order)
                .values_list('product__vendor_id', flat=True)
                .distinct()
            )
            recipients = list(User.objects.filter(id__in=vendor_ids))
        else:
            # Un vendedor envió el mensaje, notificar al comprador
            recipients = [order.user]

        # Enviar notificación push a cada destinatario
        preview = text if text else ("📷 Imagen" if image else "🎤 Audio")
        preview_short = preview[:50] + "..." if len(preview) > 50 else preview
        
        for recipient in recipients:
            try:
                # Guardar notificación en BD
                Notification.objects.create(
                    user=recipient,
                    title=f"Mensaje de {request.user.full_name}",
                    body=preview_short,
                    data={
                        "type": "order_chat",
                        # Quién lo recibe: el vendedor abre el chat en vista de venta.
                        "view": "seller" if is_buyer else "buyer",
                        "transaction_id": str(order.transaction_id),
                        "order_id": str(order.id),
                        "message_id": str(message.id),
                    },
                )
                
                # Enviar push
                send_push(
                    title=f"💬 {request.user.full_name}",
                    body=preview_short,
                    data={
                        "type": "order_chat",
                        # Quién lo recibe: el vendedor abre el chat en vista de venta.
                        "view": "seller" if is_buyer else "buyer",
                        "transaction_id": str(order.transaction_id),
                        "order_id": str(order.id),
                        "message_id": str(message.id),
                    },
                    user=recipient,
                )
            except Exception as exc:
                logger.warning(f"No se pudo notificar a {recipient.id}: {exc}")

        serializer = OrderChatMessageSerializer(
            message, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderChatMessageDeleteView(APIView):
    """Borra un mensaje propio del chat de un pedido en proceso."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, transaction_id, message_id):
        message = (
            OrderChatMessage.objects.select_related("order")
            .filter(id=message_id, order__transaction_id=transaction_id, sender=request.user)
            .first()
        )
        if not message:
            return Response({"detail": "Mensaje no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        if not is_chat_open(message.order):
            return Response(
                {"detail": "Este pedido ya terminó: el chat está cerrado.", "code": "chat_closed"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if message.image:
            message.image.delete(save=False)
        if message.audio:
            message.audio.delete(save=False)
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MarkChatMessagesReadView(APIView):
    """
    Marca todos los mensajes del chat de una orden como leídos por el usuario actual.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, transaction_id):
        try:
            order = Order.objects.get(transaction_id=transaction_id)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Orden no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verificar acceso
        user = request.user
        is_staff = user.is_staff or user.is_superuser
        is_buyer = order.user_id == user.id
        is_vendor = OrderItem.objects.filter(
            order=order, product__vendor=user
        ).exists()

        if not any([is_staff, is_buyer, is_vendor]):
            return Response(
                {"detail": "No tienes permiso para ver este chat."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Marcar como leídos todos los mensajes que NO sean del usuario actual
        updated = OrderChatMessage.objects.filter(
            order=order,
            read=False,
        ).exclude(sender=user).update(
            read=True,
            read_at=timezone.now(),
        )

        return Response(
            {"success": f"{updated} mensajes marcados como leídos."},
            status=status.HTTP_200_OK,
        )


class ConfirmDeliveryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, transactionId):
        user = request.user
        try:
            order = Order.objects.get(transaction_id=transactionId, user=user)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Pedido no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.status == Order.OrderStatus.cancelled:
            return Response(
                {'error': 'El pedido fue cancelado y no puede confirmarse.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Solo permitir confirmar si el pedido está en camino o entregado
        if order.status not in [Order.OrderStatus.shipping, Order.OrderStatus.delivered]:
            return Response(
                {
                    'error': 'Solo puedes confirmar la entrega cuando el pedido está en camino o entregado.',
                    'current_status': order.status,
                    'message': 'La vendedora debe actualizar el estado a "En camino" primero.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.buyer_confirmed_at:
            return Response(
                {
                    'message': 'Ya confirmaste la recepción.',
                    'available_on': order.buyer_confirmed_at,
                },
                status=status.HTTP_200_OK
            )

        confirmation_time = timezone.now()
        order.buyer_confirmed_at = confirmation_time
        if order.status != Order.OrderStatus.delivered:
            order.status = Order.OrderStatus.delivered
        order.save(update_fields=['buyer_confirmed_at', 'status', 'updated_at'])

        release_date = add_business_days(confirmation_time, 5)
        payouts = VendorPayout.objects.filter(order=order)
        updated_rows = payouts.update(
            buyer_confirmed_at=confirmation_time,
            available_on=release_date,
            status=VendorPayout.Status.pending_clearance,
            updated_at=confirmation_time,
        )

        # Notificar a los vendedores que el cliente confirmó la entrega
        vendor_ids = set(
            OrderItem.objects.filter(order=order)
            .exclude(product__vendor=user)
            .values_list('product__vendor_id', flat=True)
        )
        
        for vendor_id in vendor_ids:
            try:
                send_push(
                    user_id=vendor_id,
                    title="✅ Cliente confirmó la entrega",
                    body=f"¡Excelente! Tu pago será liberado el {release_date.strftime('%d/%m/%Y')}",
                    data={
                        "type": "order_confirmed",
                        "transaction_id": str(order.transaction_id),
                        "order_id": str(order.id),
                        "release_date": release_date.isoformat(),
                    }
                )
                
                Notification.objects.create(
                    user_id=vendor_id,
                    title="Cliente confirmó la entrega",
                    message=f"Tu pago será liberado el {release_date.strftime('%d de %B')}",
                    type="order_confirmed",
                )
            except Exception as e:
                logger.error(f"Error notificando al vendedor {vendor_id}: {e}")

        return Response(
            {
                'success': '¡Gracias! Avisaremos al vendedor para liberar el pago.',
                'available_on': release_date,
                'payouts_updated': updated_rows,
            },
            status=status.HTTP_200_OK
        )
