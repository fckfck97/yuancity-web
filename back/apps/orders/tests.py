from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.category.models import Category
from apps.orders.models import Order, OrderItem
from apps.product.models import Product
from apps.user.models import UserAccount


def make_order(user, index, status=Order.OrderStatus.delivered):
    return Order.objects.create(
        user=user,
        status=status,
        transaction_id=f"tx-{user.email}-{index}",
        amount=1000,
        full_name="Ana",
        address_line_1="Calle 1",
        city="Barranquilla",
        state_province_region="Atlántico",
        postal_zip_code="080001",
        telephone_number="300",
        shipping_name="Normal",
        shipping_time="2 días",
        shipping_price=0,
        date_issued=timezone.now() - timedelta(minutes=index),
    )


class OrdersPaginationTests(APITestCase):
    def setUp(self):
        self.buyer = UserAccount.objects.create_user(email="comprador@correo.com", password="x", first_name="A", last_name="B")
        self.vendor = UserAccount.objects.create_user(email="vendedor@correo.com", password="x", first_name="V", last_name="D", rol="vendor")
        product = Product.objects.create(vendor=self.vendor, category=Category.objects.create(name="Ropa"), name="Camisa", price=1000, stock=50)
        for index in range(20):
            status = Order.OrderStatus.shipping if index == 5 else Order.OrderStatus.delivered
            order = make_order(self.buyer, index, status)
            OrderItem.objects.create(product=product, order=order, name="Camisa", price=1000, count=1)

    def test_sin_p_devuelve_todo_como_antes(self):
        self.client.force_authenticate(self.buyer)
        data = self.client.get("/api/orders/get-orders").data
        self.assertEqual(len(data["orders"]), 20)
        self.assertNotIn("next_page", data)

    def test_paginas_de_comprador(self):
        self.client.force_authenticate(self.buyer)
        first = self.client.get("/api/orders/get-orders", {"p": 1, "page_size": 15}).data
        self.assertEqual((len(first["orders"]), first["count"], first["next_page"]), (15, 20, 2))
        second = self.client.get("/api/orders/get-orders", {"p": 2, "page_size": 15}).data
        self.assertEqual((len(second["orders"]), second["next_page"]), (5, None))

    def test_solo_activos(self):
        self.client.force_authenticate(self.buyer)
        data = self.client.get("/api/orders/get-orders", {"active": 1, "p": 1, "page_size": 1}).data
        self.assertEqual([o["status"] for o in data["orders"]], ["shipping"])

    def test_paginas_de_vendedor(self):
        self.client.force_authenticate(self.vendor)
        first = self.client.get("/api/orders/vendor/orders", {"p": 1, "page_size": 15}).data
        self.assertEqual((len(first["orders"]), first["count"], first["next_page"]), (15, 20, 2))
        second = self.client.get("/api/orders/vendor/orders", {"p": 2, "page_size": 15}).data
        ids = {o["order_id"] for o in first["orders"]} | {o["order_id"] for o in second["orders"]}
        self.assertEqual(len(ids), 20)


class OrderChatTests(APITestCase):
    def setUp(self):
        self.buyer = UserAccount.objects.create_user(email="chat-c@correo.com", password="x", first_name="Ana", last_name="B")
        self.vendor = UserAccount.objects.create_user(email="chat-v@correo.com", password="x", first_name="Vera", last_name="D", rol="vendor")
        product = Product.objects.create(vendor=self.vendor, category=Category.objects.create(name="Hogar"), name="Lámpara", price=1000, stock=5)
        self.order = make_order(self.buyer, 1, Order.OrderStatus.processed)
        OrderItem.objects.create(product=product, order=self.order, name="Lámpara", price=1000, count=1)
        self.url = f"/api/orders/chat/{self.order.transaction_id}/"

    def test_comprador_escribe_y_vendedor_lee_lo_nuevo(self):
        self.client.force_authenticate(self.buyer)
        first = self.client.post(self.url, {"text": "Hola"}, format="json")
        self.assertEqual(first.status_code, 201, first.data)
        self.client.force_authenticate(self.vendor)
        opened = self.client.get(self.url).data
        self.assertTrue(opened["chat_open"])
        self.assertEqual(opened["peer"]["full_name"], "Ana B")
        self.assertNotIn("@", str(opened))
        self.client.post(self.url, {"text": "¿A qué hora?"}, format="json")
        newer = self.client.get(self.url, {"after": first.data["created_at"]}).data
        self.assertEqual([m["text"] for m in newer["messages"]], ["¿A qué hora?"])

    def test_chat_cerrado_al_terminar_el_pedido(self):
        self.order.status = Order.OrderStatus.delivered
        self.order.save()
        self.client.force_authenticate(self.buyer)
        response = self.client.post(self.url, {"text": "Hola"}, format="json")
        self.assertEqual((response.status_code, response.data["code"]), (403, "chat_closed"))
        self.assertFalse(self.client.get(self.url).data["chat_open"])

    def test_borrar_solo_mensaje_propio(self):
        self.client.force_authenticate(self.buyer)
        message_id = self.client.post(self.url, {"text": "Ups"}, format="json").data["id"]
        self.client.force_authenticate(self.vendor)
        self.assertEqual(self.client.delete(f"{self.url}{message_id}/").status_code, 404)
        self.client.force_authenticate(self.buyer)
        self.assertEqual(self.client.delete(f"{self.url}{message_id}/").status_code, 204)
        self.assertEqual(self.client.get(self.url).data["messages"], [])
