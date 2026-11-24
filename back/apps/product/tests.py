import io
import tempfile
from decimal import Decimal

from unittest import mock

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

from rest_framework.test import APITestCase

from apps.category.models import Category
from apps.user.models import UserAccount, UserProfile
from apps.product.models import Product, ProductImage


def make_vendor(email, lat=None, lng=None, city=""):
    user = UserAccount.objects.create_user(email=email, password="x", first_name="Ven", last_name=email[:3], rol="vendor")
    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={"username": email.split("@")[0]})
    profile.latitude = Decimal(str(lat)) if lat is not None else None
    profile.longitude = Decimal(str(lng)) if lng is not None else None
    profile.city = city
    profile.save()
    return user


class ProductListTests(APITestCase):
    def setUp(self):
        parent = Category.objects.create(name="Papelería")
        self.category = Category.objects.create(name="Arte y Manualidades", parent=parent)
        vendor = make_vendor("v1@correo.com")
        self.cheap = Product.objects.create(vendor=vendor, category=self.category, name="Lápiz rojo", price=1000, stock=5)
        self.sale = Product.objects.create(
            vendor=vendor, category=self.category, name="Cuaderno", description="Tapa dura roja", price=9000, stock=5, discount_percent=30
        )

    def test_busqueda_por_varias_palabras_y_descripcion(self):
        response = self.client.get("/api/products/list/", {"search": "tapa roja"})
        self.assertEqual([p["id"] for p in response.data["results"]], [str(self.sale.id)])

    def test_busqueda_por_categoria_padre(self):
        response = self.client.get("/api/products/list/", {"search": "papelería"})
        self.assertEqual(response.data["count"], 2)

    def test_orden_y_solo_ofertas(self):
        asc = self.client.get("/api/products/list/", {"ordering": "price_asc"}).data["results"]
        self.assertEqual(asc[0]["id"], str(self.cheap.id))
        on_sale = self.client.get("/api/products/list/", {"on_sale": "1"}).data["results"]
        self.assertEqual([p["id"] for p in on_sale], [str(self.sale.id)])

    def test_highlights_trae_ofertas_relampago_con_descuento(self):
        data = self.client.get("/api/products/highlights/").data
        self.assertEqual([p["id"] for p in data["flash_deals"]], [str(self.sale.id)])


class NearbySellersTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Ropa")
        # Barranquilla (~1 km del punto de consulta) y Bogotá (~700 km).
        self.near = make_vendor("cerca@correo.com", 10.97, -74.79, "Barranquilla")
        self.far = make_vendor("lejos@correo.com", 4.71, -74.07, "Bogotá")
        self.no_location = make_vendor("sinubicacion@correo.com")
        for vendor in (self.near, self.far, self.no_location):
            Product.objects.create(vendor=vendor, category=self.category, name=f"Camisa {vendor.email}", price=20000, stock=3)
        Product.objects.create(vendor=self.near, category=self.category, name="Agotado", price=1, stock=0)

    def test_solo_vendedores_en_el_radio_con_productos_disponibles(self):
        data = self.client.get("/api/products/nearby/", {"lat": 10.9685, "lng": -74.7813, "radius_km": 25}).data
        self.assertEqual(data["count"], 1)
        seller = data["sellers"][0]
        self.assertEqual(seller["id"], str(self.near.id))
        self.assertLess(seller["distance_km"], 3)
        self.assertEqual(seller["products_count"], 1)
        self.assertEqual(len(seller["products"]), 1)
        self.assertNotIn("email", seller)

    def test_ordena_por_distancia(self):
        # Desde el centro de Colombia: Bogotá (~260 km) antes que Barranquilla (~440 km).
        data = self.client.get("/api/products/nearby/", {"lat": 7.0, "lng": -74.4, "radius_km": 300}).data
        self.assertEqual([s["city"] for s in data["sellers"]], ["Bogotá"])
        self.assertEqual(data["radius_km"], 300)

    def test_valida_coordenadas(self):
        self.assertEqual(self.client.get("/api/products/nearby/", {"lat": "x", "lng": 1}).status_code, 400)


def png(name):
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), (200, 0, 0)).save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ProductGalleryEditTests(APITestCase):
    def setUp(self):
        self.vendor = make_vendor("galeria@correo.com")
        self.product = Product.objects.create(vendor=self.vendor, category=Category.objects.create(name="Hogar"), name="Silla", price=5000, stock=2)
        self.a = ProductImage.objects.create(product=self.product, image=png("a.png"), display_order=0, is_primary=True)
        self.b = ProductImage.objects.create(product=self.product, image=png("b.png"), display_order=1)
        self.client.force_authenticate(self.vendor)

    def test_quita_reordena_y_pone_nueva_como_principal(self):
        response = self.client.patch(
            f"/api/products/{self.product.id}/update/",
            {"image_order": f"new:0,id:{self.b.id}", "media_0": png("c.png")},
            format="multipart",
        )
        self.assertEqual(response.status_code, 200, response.data)
        images = list(self.product.images.order_by("display_order"))
        self.assertEqual(len(images), 2)
        self.assertTrue(images[0].is_primary)
        self.assertNotEqual(images[0].id, self.b.id)
        self.assertEqual((images[1].id, images[1].is_primary), (self.b.id, False))
        self.assertFalse(ProductImage.objects.filter(id=self.a.id).exists())


class ExchangeRateTests(APITestCase):
    def setUp(self):
        cache.clear()

    def _response(self, payload):
        response = mock.Mock()
        response.json.return_value = payload
        response.raise_for_status.return_value = None
        return response

    @mock.patch("apps.product.exchange.requests.get")
    def test_trm_oficial_y_cache(self, get):
        get.return_value = self._response([{"valor": "3170.46", "vigenciadesde": "2026-10-16T00:00:00.000"}])
        first = self.client.get("/api/products/exchange-rate/").data
        self.assertEqual((first["rate"], first["date"], first["source"]), (3170.46, "2026-10-16", "trm"))
        self.client.get("/api/products/exchange-rate/")
        self.assertEqual(get.call_count, 1)

    @mock.patch("apps.product.exchange.requests.get")
    def test_respaldo_y_ultima_buena(self, get):
        get.side_effect = [Exception("trm caída"), self._response({"rates": {"COP": 3200.5}})]
        self.assertEqual(self.client.get("/api/products/exchange-rate/").data["source"], "open.er-api")
        cache.delete("exchange:usd_cop")
        get.side_effect = Exception("sin red")
        stale = self.client.get("/api/products/exchange-rate/").data
        self.assertEqual((stale["rate"], stale["stale"]), (3200.5, True))
