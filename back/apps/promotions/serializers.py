# promotions/serializers.py
from rest_framework import serializers
from .models import Promotion
from apps.product.models import Product
from apps.product.serializers import ProductMinimalSerializer


def build_banner_url(obj, request):
    if not obj.banner:
        return None
    url = obj.banner.url
    if request:
        return request.build_absolute_uri(url)
    return url


class PromotionListSerializer(serializers.ModelSerializer):
    banner_url = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    vendor_name = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = [
            "id",
            "title",
            "description",
            "slug",
            "banner",
            "banner_url",
            "products_count",
            "vendor_name",
        ]

    def get_banner_url(self, obj):
        request = self.context.get("request")
        return build_banner_url(obj, request)

    def get_products_count(self, obj):
        return obj.products.count()

    def get_vendor_name(self, obj):
        vendor = getattr(obj, "vendor", None)
        if not vendor:
            return None
        if getattr(vendor, "full_name", None):
            return vendor.full_name
        return getattr(vendor, "first_name", None)


class PromotionDetailSerializer(serializers.ModelSerializer):
    products = ProductMinimalSerializer(many=True, read_only=True)
    banner_url = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    vendor_name = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = [
            "id",
            "title",
            "description",
            "slug",
            "banner",
            "banner_url",
            "start_date",
            "end_date",
            "is_active",
            "products_count",
            "vendor_name",
            "products",
        ]

    def get_banner_url(self, obj):
        request = self.context.get("request")
        return build_banner_url(obj, request)

    def get_products_count(self, obj):
        return obj.products.count()

    def get_vendor_name(self, obj):
        vendor = getattr(obj, "vendor", None)
        if not vendor:
            return None
        if vendor.full_name:
            return vendor.full_name
        return vendor.first_name


class PromotionSuggestionSerializer(serializers.ModelSerializer):
    banner_url = serializers.SerializerMethodField()
    vendor_name = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = [
            "id",
            "title",
            "slug",
            "banner",
            "banner_url",
            "vendor_name",
            "products_count",
        ]

    def get_banner_url(self, obj):
        request = self.context.get("request")
        return build_banner_url(obj, request)

    def get_vendor_name(self, obj):
        vendor = getattr(obj, "vendor", None)
        if not vendor:
            return None
        if vendor.full_name:
            return vendor.full_name
        return vendor.first_name

    def get_products_count(self, obj):
        return obj.products.count()


class PromotionDashboardSerializer(serializers.ModelSerializer):
    products = ProductMinimalSerializer(many=True, read_only=True)
    product_ids = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="products",
    )
    banner_url = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    vendor_name = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = [
            "id",
            "title",
            "description",
            "slug",
            "banner",
            "banner_url",
            "start_date",
            "end_date",
            "is_active",
            "products",
            "products_count",
            "vendor_name",
            "product_ids",
        ]
        read_only_fields = ["slug"]

    def get_banner_url(self, obj):
        request = self.context.get("request")
        return build_banner_url(obj, request)

    def get_products_count(self, obj):
        return obj.products.count()

    def get_vendor_name(self, obj):
        vendor = getattr(obj, "vendor", None)
        if not vendor:
            return None
        if vendor.full_name:
            return vendor.full_name
        return vendor.first_name

    def validate_products(self, products):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and user.rol == "vendor":
            invalid = [p for p in products if p.vendor != user]
            if invalid:
                raise serializers.ValidationError(
                    "Solo puedes asociar productos de tu tienda."
                )
        return products

    def create(self, validated_data):
        products = validated_data.pop("products", [])
        promotion = Promotion.objects.create(**validated_data)
        if products:
            promotion.products.set(products)
        return promotion

    def update(self, instance, validated_data):
        products = validated_data.pop("products", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if products is not None:
            instance.products.set(products)
        return instance
