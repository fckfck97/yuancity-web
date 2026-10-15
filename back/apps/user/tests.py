import re
from datetime import timedelta
from decimal import Decimal
from unittest import mock

from django.core import mail
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.cart.models import Cart
from apps.category.models import Category
from apps.orders.models import Order, OrderItem
from apps.product.models import Product
from apps.wishlist.models import WishList

from apps.user.deletion import identity_hash
from apps.user.models import (
    AccountDeletionRequest,
    DeletedAccountRecord,
    LoginCode,
    LoginLog,
    SocialIdentity,
    UserAccount,
)


def last_code(length):
    """Código enviado en el último correo."""
    return re.search(rf"\b(\d{{{length}}})\b", mail.outbox[-1].body).group(1)


def auth(client, user):
    client.credentials(HTTP_AUTHORIZATION=f"JWT {RefreshToken.for_user(user).access_token}")


def make_order(buyer, vendor, status="delivered", category=None):
    category = category or Category.objects.create(name=f"Ropa {Category.objects.count()}")
    product = Product.objects.create(vendor=vendor, category=category, name="Camisa", price=Decimal("50000"), stock=3)
    order = Order.objects.create(
        user=buyer,
        status=status,
        transaction_id=f"tx-{Order.objects.count()}-{buyer.pk.hex[:6]}",
        amount=Decimal("50000"),
        full_name="Ana Pérez",
        address_line_1="Calle 1",
        city="Bogotá",
        state_province_region="Cundinamarca",
        postal_zip_code="110111",
        telephone_number="3001234567",
        shipping_name="Estándar",
        shipping_time="3 días",
        shipping_price=Decimal("0"),
    )
    OrderItem.objects.create(product=product, order=order, name=product.name, price=product.price, count=1)
    return order, product


class EmailCodeLoginTests(APITestCase):
    request_url = "/api/login/otp/request/"
    verify_url = "/api/login/otp/verify/"

    def test_new_app_gets_six_digit_code_and_account_is_created_on_verify(self):
        response = self.client.post(self.request_url, {"email": "Nueva@Correo.com", "code_length": 6}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_new_user"])
        self.assertEqual(response.data["code_length"], 6)
        self.assertNotIn("otp", response.data)
        # La cuenta no existe hasta validar el código.
        self.assertFalse(UserAccount.objects.filter(email="nueva@correo.com").exists())

        code = last_code(6)
        self.assertNotIn(code, str(response.data))
        self.assertNotEqual(LoginCode.objects.get().code_hash, code)

        response = self.client.post(self.verify_url, {"identifier": "nueva@correo.com", "otp": code}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertTrue(response.data["is_new_user"])
        user = UserAccount.objects.get(email="nueva@correo.com")
        self.assertTrue(Cart.objects.filter(user=user).exists())
        self.assertTrue(WishList.objects.filter(user=user).exists())
        self.assertEqual(LoginLog.objects.get(user=user).provider, "otp")

    def test_published_app_without_code_length_still_gets_four_digits(self):
        self.client.post(self.request_url, {"email": "legacy@correo.com"}, format="json")
        code = last_code(4)
        response = self.client.post(self.verify_url, {"identifier": "legacy@correo.com", "otp": code}, format="json")
        self.assertEqual(response.status_code, 200)

    def test_code_is_single_use(self):
        self.client.post(self.request_url, {"email": "uno@correo.com", "code_length": 6}, format="json")
        code = last_code(6)
        self.assertEqual(self.client.post(self.verify_url, {"identifier": "uno@correo.com", "otp": code}, format="json").status_code, 200)
        self.assertEqual(self.client.post(self.verify_url, {"identifier": "uno@correo.com", "otp": code}, format="json").status_code, 400)

    def test_wrong_code_counts_attempts_and_locks_after_five(self):
        self.client.post(self.request_url, {"email": "intentos@correo.com", "code_length": 6}, format="json")
        code = last_code(6)
        wrong = "000000" if code != "000000" else "111111"
        response = self.client.post(self.verify_url, {"identifier": "intentos@correo.com", "otp": wrong}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["attempts_left"], 4)
        for _ in range(4):
            self.client.post(self.verify_url, {"identifier": "intentos@correo.com", "otp": wrong}, format="json")
        # Ni el código correcto sirve después de 5 intentos fallidos.
        response = self.client.post(self.verify_url, {"identifier": "intentos@correo.com", "otp": code}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_expired_code_is_rejected(self):
        self.client.post(self.request_url, {"email": "vencido@correo.com", "code_length": 6}, format="json")
        code = last_code(6)
        LoginCode.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
        response = self.client.post(self.verify_url, {"identifier": "vencido@correo.com", "otp": code}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_resend_is_throttled(self):
        self.client.post(self.request_url, {"email": "spam@correo.com"}, format="json")
        response = self.client.post(self.request_url, {"email": "spam@correo.com"}, format="json")
        self.assertEqual(response.status_code, 429)
        self.assertGreater(response.data["resend_in"], 0)

    def test_new_code_invalidates_previous(self):
        self.client.post(self.request_url, {"email": "dos@correo.com", "code_length": 6}, format="json")
        first = last_code(6)
        LoginCode.objects.update(created_at=timezone.now() - timedelta(minutes=2))
        self.client.post(self.request_url, {"email": "dos@correo.com", "code_length": 6}, format="json")
        second = last_code(6)
        if first != second:
            self.assertEqual(self.client.post(self.verify_url, {"identifier": "dos@correo.com", "otp": first}, format="json").status_code, 400)
        self.assertEqual(self.client.post(self.verify_url, {"identifier": "dos@correo.com", "otp": second}, format="json").status_code, 200)

    def test_existing_user_logs_in_without_duplicates(self):
        user = UserAccount.objects.create_user(email="existe@correo.com", password="x", first_name="E", last_name="X")
        response = self.client.post(self.request_url, {"email": "EXISTE@correo.com", "code_length": 6}, format="json")
        self.assertFalse(response.data["is_new_user"])
        response = self.client.post(self.verify_url, {"identifier": "existe@correo.com", "otp": last_code(6)}, format="json")
        self.assertFalse(response.data["is_new_user"])
        self.assertEqual(UserAccount.objects.filter(email__iexact="existe@correo.com").count(), 1)
        self.assertEqual(RefreshToken(response.data["refresh"])["user_id"], str(user.pk))

    def test_store_review_account_skips_code(self):
        UserAccount.objects.create_user(email="apple.revisor@yuancity.com", password="x", first_name="A", last_name="R")
        response = self.client.post(self.verify_url, {"identifier": "apple.revisor@yuancity.com", "otp": "1234"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    @mock.patch("apps.user.views.send_sms_in_background")
    def test_phone_code(self, send_sms):
        response = self.client.post(self.request_url, {"phone": "+57 300 123 4567", "code_length": 6}, format="json")
        self.assertEqual(response.status_code, 200)
        code = re.search(r"(\d{6})", send_sms.call_args[0][1]).group(1)
        response = self.client.post(self.verify_url, {"identifier": "+573001234567", "otp": code}, format="json")
        self.assertEqual(response.status_code, 200)
        user = UserAccount.objects.get(phone="573001234567")
        self.assertTrue(user.phone_verified)

    def test_mail_failure_returns_503_and_discards_code(self):
        with mock.patch("apps.user.views.send_mail", side_effect=OSError("smtp caído")):
            response = self.client.post(self.request_url, {"email": "caido@correo.com"}, format="json")
        self.assertEqual(response.status_code, 503)
        self.assertFalse(LoginCode.objects.exists())

    @override_settings(WEB_ALLOWED_EMAILS=["admin@yuancity.com"])
    def test_web_login_uses_six_digit_hashed_code(self):
        UserAccount.objects.create_user(email="admin@yuancity.com", password="x", first_name="A", last_name="D")
        self.assertEqual(self.client.post("/api/login/otp/request/web/", {"email": "otro@yuancity.com"}, format="json").status_code, 403)
        self.assertEqual(self.client.post("/api/login/otp/request/web/", {"email": "admin@yuancity.com"}, format="json").status_code, 200)
        response = self.client.post(self.verify_url, {"identifier": "admin@yuancity.com", "otp": last_code(6), "source": "web"}, format="json")
        self.assertEqual(response.status_code, 200)


class SessionTests(APITestCase):
    def setUp(self):
        self.user = UserAccount.objects.create_user(email="sesion@correo.com", password="x", first_name="S", last_name="S")

    def test_legacy_refresh_path_used_by_published_app(self):
        refresh = str(RefreshToken.for_user(self.user))
        response = self.client.post("/api/auth/jwt/refresh/", {"refresh": refresh}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_logout_blacklists_refresh(self):
        refresh = str(RefreshToken.for_user(self.user))
        auth(self.client, self.user)
        self.assertEqual(self.client.post("/api/auth/logout/", {"refresh": refresh}, format="json").status_code, 204)
        self.client.credentials()
        self.assertEqual(self.client.post("/api/auth/refresh/", {"refresh": refresh}, format="json").status_code, 401)


class SocialLoginTests(APITestCase):
    url = "/api/social/login/"

    def google(self, sub, email):
        return {
            "sub": sub,
            "email": email,
            "email_verified": True,
            "aud": "client-ios",
            "given_name": "Laura",
            "family_name": "Lozano",
        }

    @override_settings(GOOGLE_CLIENT_IDS=["client-ios", None])
    def test_google_links_identity_by_subject(self):
        with mock.patch("apps.user.views.google_id_token.verify_oauth2_token", return_value=self.google("g-1", "laura@gmail.com")):
            response = self.client.post(self.url, {"provider": "google", "id_token": "t"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_new_user"])
        user = UserAccount.objects.get(email="laura@gmail.com")
        self.assertEqual(user.first_name, "Laura")
        self.assertTrue(Cart.objects.filter(user=user).exists())
        self.assertTrue(SocialIdentity.objects.filter(user=user, provider="google", subject="g-1").exists())

        # Si cambia el correo en Google, sigue entrando a la misma cuenta.
        with mock.patch("apps.user.views.google_id_token.verify_oauth2_token", return_value=self.google("g-1", "nuevo@gmail.com")):
            response = self.client.post(self.url, {"provider": "google", "id_token": "t"}, format="json")
        self.assertFalse(response.data["is_new_user"])
        self.assertEqual(UserAccount.objects.count(), 1)

    @override_settings(GOOGLE_CLIENT_IDS=["client-ios"])
    def test_google_rejects_unknown_audience_and_unverified_email(self):
        payload = {**self.google("g-2", "x@gmail.com"), "aud": "otro"}
        with mock.patch("apps.user.views.google_id_token.verify_oauth2_token", return_value=payload):
            self.assertEqual(self.client.post(self.url, {"provider": "google", "id_token": "t"}, format="json").status_code, 400)
        payload = {**self.google("g-2", "x@gmail.com"), "email_verified": False}
        with mock.patch("apps.user.views.google_id_token.verify_oauth2_token", return_value=payload):
            self.assertEqual(self.client.post(self.url, {"provider": "google", "id_token": "t"}, format="json").status_code, 400)


class AccountDeletionTests(APITestCase):
    def setUp(self):
        self.user = UserAccount.objects.create_user(
            email="borrar@correo.com", password="x", first_name="Ana", last_name="Pérez", phone="573009998877"
        )
        SocialIdentity.objects.create(user=self.user, provider="google", subject="g-borrar")
        self.vendor = UserAccount.objects.create_user(email="vende@correo.com", password="x", first_name="V", last_name="V")

    def test_status_reports_blockers_and_history(self):
        auth(self.client, self.user)
        response = self.client.get("/api/users/me/deletion/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["can_delete"])
        self.assertFalse(response.data["keeps_orders"])
        self.assertEqual(response.data["providers"], ["google"])

    def test_delete_without_orders_removes_everything(self):
        user_id = self.user.pk
        auth(self.client, self.user)
        response = self.client.delete("/api/users/me/", {"reason": "Ya no lo uso", "google_revoked": True}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["mode"], "deleted")
        self.assertFalse(UserAccount.objects.filter(pk=user_id).exists())
        record = DeletedAccountRecord.objects.get(original_user_id=user_id)
        self.assertEqual(record.email_hash, identity_hash("borrar@correo.com"))
        self.assertEqual(record.email_hint, "bo***@correo.com")
        self.assertNotIn("borrar@correo.com", str(record.__dict__))
        self.assertEqual(record.platform_revocation, {"google": "revoked_by_client"})
        self.assertEqual(record.source, "app")
        self.assertEqual(DeletedAccountRecord.objects.count(), 1)

    def test_delete_with_orders_anonymizes_and_keeps_orders(self):
        order, _ = make_order(buyer=self.user, vendor=self.vendor)
        auth(self.client, self.user)
        response = self.client.delete("/api/users/me/", {}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["mode"], "anonymized")

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertTrue(self.user.email.endswith("@deleted.yuancity.invalid"))
        self.assertIsNone(self.user.phone)
        self.assertEqual(self.user.first_name, "Usuario")
        self.assertFalse(self.user.has_usable_password())
        self.assertFalse(SocialIdentity.objects.filter(user=self.user).exists())
        self.assertTrue(Order.objects.filter(pk=order.pk).exists())
        self.assertEqual(DeletedAccountRecord.objects.get(original_user_id=self.user.pk).mode, "anonymized")

        # El correo queda libre para volver a registrarse y se reconoce a quien vuelve.
        self.client.credentials()
        self.client.post("/api/login/otp/request/", {"email": "borrar@correo.com", "code_length": 6}, format="json")
        response = self.client.post("/api/login/otp/verify/", {"identifier": "borrar@correo.com", "otp": last_code(6)}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_new_user"])
        new_user = UserAccount.objects.get(email="borrar@correo.com")
        self.assertEqual(DeletedAccountRecord.objects.get(original_user_id=self.user.pk).rejoined_user, new_user)

    def test_vendor_with_sales_is_anonymized_and_sold_products_hidden(self):
        _, sold = make_order(buyer=self.user, vendor=self.vendor)
        unsold = Product.objects.create(vendor=self.vendor, category=sold.category, name="Gorra", price=Decimal("10000"), stock=5)
        auth(self.client, self.vendor)
        response = self.client.delete("/api/users/me/", {}, format="json")
        self.assertEqual(response.status_code, 200)
        sold.refresh_from_db()
        self.assertFalse(sold.is_available)
        self.assertEqual(sold.stock, 0)
        self.assertFalse(Product.objects.filter(pk=unsold.pk).exists())

    def test_active_order_blocks_deletion(self):
        make_order(buyer=self.user, vendor=self.vendor, status="shipping")
        auth(self.client, self.user)
        response = self.client.delete("/api/users/me/", {}, format="json")
        self.assertEqual(response.status_code, 409)
        self.assertTrue(UserAccount.objects.get(pk=self.user.pk).is_active)
        self.assertFalse(self.client.get("/api/users/me/deletion/").data["can_delete"])

    def test_legacy_route_of_published_app(self):
        auth(self.client, self.user)
        self.assertEqual(self.client.delete(f"/api/delete/account/{self.vendor.pk}/").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/delete/account/{self.user.pk}/").status_code, 204)
        self.assertFalse(UserAccount.objects.filter(pk=self.user.pk).exists())

    def test_admin_deletion_also_leaves_record(self):
        user_id = self.user.pk
        self.user.delete()
        self.assertEqual(DeletedAccountRecord.objects.get(original_user_id=user_id).source, "admin")

    def test_web_flow_with_email_code(self):
        response = self.client.post("/api/account/deletion/request/", {"email": "nadie@correo.com"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)  # misma respuesta, sin revelar si existe

        response = self.client.post("/api/account/deletion/request/", {"email": "BORRAR@correo.com"}, format="json")
        self.assertEqual(response.status_code, 200)
        code = last_code(6)
        wrong = "000000" if code != "000000" else "111111"
        response = self.client.post("/api/account/deletion/confirm/", {"email": "borrar@correo.com", "otp": wrong}, format="json")
        self.assertEqual(response.status_code, 400)
        response = self.client.post(
            "/api/account/deletion/confirm/", {"email": "borrar@correo.com", "otp": code, "reason": "Privacidad"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(UserAccount.objects.filter(email="borrar@correo.com").exists())
        request = AccountDeletionRequest.objects.get(status="completed")
        self.assertEqual(request.code_hash, "")
        self.assertEqual(DeletedAccountRecord.objects.get().source, "web")

    def test_web_flow_is_rate_limited(self):
        for _ in range(3):
            self.client.post("/api/account/deletion/request/", {"email": "nadie@correo.com"}, format="json")
        response = self.client.post("/api/account/deletion/request/", {"email": "nadie@correo.com"}, format="json")
        self.assertEqual(response.status_code, 429)


class MobileVersionTests(APITestCase):
    def test_version_endpoint_is_public(self):
        from apps.mobile.models import MobileAppVersion

        MobileAppVersion.objects.create(platform="ios", latest_version="1.1.0", minimum_supported_version="1.0.5")
        response = self.client.get("/api/mobile/version/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["ios"]["latestVersion"], "1.1.0")
        self.assertIsNone(response.data["android"])
