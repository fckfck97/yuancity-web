from rest_framework import serializers

from apps.orders.models import Order, OrderItem

from .models import VendorBankAccount, VendorPayout


class VendorBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorBankAccount
        fields = [
            "id",
            "bank_name",
            "account_type",
            "account_number",
            "account_holder_name",
            "document_type",
            "document_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")


class VendorPayoutSerializer(serializers.ModelSerializer):
    order_transaction_id = serializers.CharField(
        source="order.transaction_id", read_only=True
    )
    order_date = serializers.DateTimeField(source="order.date_issued", read_only=True)

    class Meta:
        model = VendorPayout
        fields = [
            "id",
            "order",
            "order_transaction_id",
            "order_date",
            "status",
            "gross_amount",
            "platform_fee",
            "net_amount",
            "items_count",
            "buyer_confirmed_at",
            "available_on",
            "released_at",
        ]
        read_only_fields = fields


class FinancePortalLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()


class FinanceOrderItemSerializer(serializers.ModelSerializer):
    vendor_id = serializers.SerializerMethodField()
    vendor_email = serializers.SerializerMethodField()
    vendor_name = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "name",
            "price",
            "count",
            "platform_fee",
            "vendor_earnings",
            "vendor_id",
            "vendor_email",
            "vendor_name",
        ]

    def _get_vendor(self, obj):
        product = getattr(obj, "product", None)
        return getattr(product, "vendor", None) if product else None

    def get_vendor_id(self, obj):
        vendor = self._get_vendor(obj)
        return str(vendor.id) if vendor else None

    def get_vendor_email(self, obj):
        vendor = self._get_vendor(obj)
        return vendor.email if vendor else None

    def get_vendor_name(self, obj):
        vendor = self._get_vendor(obj)
        if not vendor:
            return None
        return vendor.full_name or vendor.email


class FinanceOrderSerializer(serializers.ModelSerializer):
    buyer_email = serializers.EmailField(source="user.email", read_only=True)
    buyer_name = serializers.SerializerMethodField()
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    items = serializers.SerializerMethodField()
    total_platform_fee = serializers.SerializerMethodField()
    vendor_total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "transaction_id",
            "status",
            "status_label",
            "amount",
            "shipping_price",
            "date_issued",
            "buyer_email",
            "buyer_name",
            "city",
            "state_province_region",
            "country_region",
            "telephone_number",
            "items",
            "total_platform_fee",
            "vendor_total",
        ]

    def get_buyer_name(self, obj):
        return obj.user.full_name if obj.user_id else ""

    def get_items(self, obj):
        queryset = obj.orderitem_set.all()
        return FinanceOrderItemSerializer(queryset, many=True).data

    def _sum_field(self, obj, attr):
        total = 0
        for item in obj.orderitem_set.all():
            value = getattr(item, attr, 0) or 0
            total += value
        return total

    def get_total_platform_fee(self, obj):
        return self._sum_field(obj, "platform_fee")

    def get_vendor_total(self, obj):
        return self._sum_field(obj, "vendor_earnings")


class FinanceVendorPayoutSerializer(serializers.ModelSerializer):
    vendor_email = serializers.EmailField(source="vendor.email", read_only=True)
    vendor_name = serializers.SerializerMethodField()
    vendor_phone = serializers.CharField(source="vendor.phone", read_only=True)
    vendor_id = serializers.SerializerMethodField()
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    bank_account = serializers.SerializerMethodField()
    order_transaction_id = serializers.CharField(
        source="order.transaction_id", read_only=True
    )

    class Meta:
        model = VendorPayout
        fields = [
            "id",
            "status",
            "status_label",
            "gross_amount",
            "platform_fee",
            "net_amount",
            "items_count",
            "buyer_confirmed_at",
            "available_on",
            "released_at",
            "notes",
            "vendor_email",
            "vendor_name",
            "vendor_phone",
            "vendor_id",
            "order_transaction_id",
            "bank_account",
        ]
        read_only_fields = fields

    def get_vendor_name(self, obj):
        if not obj.vendor_id:
            return ""
        return obj.vendor.full_name or obj.vendor.email

    def get_vendor_id(self, obj):
        return str(obj.vendor_id) if obj.vendor_id else None

    def get_bank_account(self, obj):
        vendor = getattr(obj, "vendor", None)
        if not vendor:
            return obj.bank_account_snapshot or None
        try:
            account = vendor.bank_account
        except VendorBankAccount.DoesNotExist:
            return obj.bank_account_snapshot or None
        return VendorBankAccountSerializer(account).data


class FinancePayoutStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=VendorPayout.Status.choices)
    notes = serializers.CharField(required=False, allow_blank=True)
    available_on = serializers.DateTimeField(required=False, allow_null=True)
    buyer_confirmed = serializers.BooleanField(required=False)
