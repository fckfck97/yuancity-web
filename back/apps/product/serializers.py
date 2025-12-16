# products/serializers.py

from rest_framework import serializers
from .models import Product, ProductImage
from apps.category.models import Category
from apps.category.serializers import CategorySerializer
from apps.user.models import UserAccount, UserProfile
from apps.cart.utils import seconds_until
from django.utils import timezone
from apps.cart.models import CartItem


def build_reservation_payload(obj, request):
    default_payload = {
        "is_reserved": False,
        "reserved_by_me": False,
        "reserved_until": None,
        "seconds_left": None,
    }
    expires_at = getattr(obj, "reservation_expires_at", None)
    reserved_user_id = getattr(obj, "reservation_user_id", None)
    if not expires_at:
        active_item = (
            CartItem.objects.select_related("cart__user")
            .filter(product=obj, reserved_until__gt=timezone.now())
            .order_by("-reserved_until")
            .first()
        )
        if not active_item:
            return default_payload
        expires_at = active_item.reserved_until
        reserved_user_id = active_item.cart.user_id
    seconds_left = seconds_until(expires_at)
    user = getattr(request, "user", None)
    is_authenticated = bool(user and getattr(user, "is_authenticated", False))
    reserved_by_me = (
        bool(
            is_authenticated
            and reserved_user_id
            and str(user.id) == str(reserved_user_id)
        )
    )
    return {
        "is_reserved": True,
        "reserved_by_me": reserved_by_me,
        "reserved_until": expires_at.isoformat(),
        "seconds_left": seconds_left,
    }


class VendorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    city = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    address_line = serializers.SerializerMethodField()
    location_label = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model  = UserAccount
        fields = [
            'id',
            'full_name',
            'email',
            'city',
            'department',
            'address_line',
            'location_label',
            'latitude',
            'longitude',
            'avatar_url',
        ]

    def _get_profile(self, obj):
        try:
            return obj.social_profile
        except (UserProfile.DoesNotExist, AttributeError):
            return None

    def get_city(self, obj):
        profile = self._get_profile(obj)
        return profile.city if profile else ""

    def get_department(self, obj):
        profile = self._get_profile(obj)
        return profile.department if profile else ""

    def get_address_line(self, obj):
        profile = self._get_profile(obj)
        return profile.address_line if profile else ""

    def get_location_label(self, obj):
        profile = self._get_profile(obj)
        return profile.location if profile else ""

    def get_latitude(self, obj):
        profile = self._get_profile(obj)
        return profile.latitude if profile else None

    def get_longitude(self, obj):
        profile = self._get_profile(obj)
        return profile.longitude if profile else None

    def get_avatar_url(self, obj):
        profile = self._get_profile(obj)
        if profile and profile.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(profile.avatar.url)
            return profile.avatar.url
        return None

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ProductImage
        fields = ['id', 'image', 'alt_text', 'display_order', 'is_primary']



class ProductSerializer(serializers.ModelSerializer):
    # write-only uploads
    image = serializers.ImageField(write_only=True, required=False)
    # relaciones
    images          = ProductImageSerializer(many=True, read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    vendor_detail   = VendorSerializer(source='vendor', read_only=True)
    reservation = serializers.SerializerMethodField()

    # dejamos vendor PK read_only (se asigna en la vista)
    vendor = serializers.PrimaryKeyRelatedField(read_only=True, source='vendor.id')
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    availability = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 
            'vendor', 'vendor_detail',
            'category', 'category_detail',
            'name', 'slug', 'description',
            'price', 'discount_percent', 'currency',
            'stock', 'is_available',
            'created_at', 'updated_at',
            'images', 'image',
            'availability', 'reservation',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'vendor']

    def get_availability(self, obj):
        return obj.is_available and obj.stock > 0

    def get_reservation(self, obj):
        request = self.context.get("request")
        return build_reservation_payload(obj, request)

    def create(self, validated_data):
        image_file = validated_data.pop('image', None)
        product    = super().create(validated_data)
        
        # Procesar múltiples medios si existen
        request = self.context.get('request')
        if request and request.data.get('media_count'):
            self._process_media(product, request)
        elif image_file:
            # Retrocompatibilidad: imagen única
            ProductImage.objects.create(
                product=product, image=image_file, display_order=0, is_primary=True
            )
        return product

    def update(self, instance, validated_data):
        image_file = validated_data.pop('image', None)
        product    = super().update(instance, validated_data)
        
        # Procesar múltiples imágenes si existen
        request = self.context.get('request')
        if request and request.data.get('media_count'):
            media_count = int(request.data.get('media_count', 0))
            
            # Determinar si se debe limpiar las imágenes existentes
            # Si replace_all=true, eliminar todas las imágenes existentes
            replace_all = request.data.get('replace_all', 'false').lower() == 'true'
            
            if replace_all and media_count > 0:
                # Reemplazar todas las imágenes
                product.images.all().delete()
                self._process_media(product, request)
            elif media_count > 0:
                # Anexar nuevas imágenes (mantener las existentes)
                # No eliminar imágenes existentes, solo agregar nuevas
                self._process_media(product, request, append_mode=True)
        elif image_file:
            # Retrocompatibilidad: agregar nueva imagen sin borrar las anteriores
            ProductImage.objects.create(
                product=product, image=image_file, display_order=0
            )
        return product
    
    def _process_media(self, product, request, append_mode=False):
        """Procesa múltiples imágenes del request
        
        Args:
            product: Instancia del producto
            request: Request HTTP
            append_mode: Si es True, anexa imágenes sin eliminar las existentes
        """
        media_count = int(request.data.get('media_count', 0))
        
        # Si estamos en modo anexar, obtener el último display_order
        base_order = 0
        if append_mode:
            last_image = product.images.order_by('-display_order').first()
            base_order = (last_image.display_order + 1) if last_image else 0
        
        for i in range(media_count):
            media_file = request.FILES.get(f'media_{i}')
            display_order = int(request.data.get(f'media_{i}_order', i)) + base_order
            is_primary = request.data.get(f'media_{i}_primary', 'false').lower() == 'true'
            
            if not media_file:
                continue
            
            # Si está marcada como principal, desmarcar otras
            if is_primary:
                ProductImage.objects.filter(product=product).update(is_primary=False)
            
            ProductImage.objects.create(
                product=product,
                image=media_file,
                display_order=display_order,
                is_primary=is_primary
            )




class ProductMinimalSerializer(serializers.ModelSerializer):
  first_image = serializers.SerializerMethodField()
  category_detail = serializers.SerializerMethodField()
  availability = serializers.SerializerMethodField()
  vendor_detail = VendorSerializer(source='vendor', read_only=True)
  reservation = serializers.SerializerMethodField()

  class Meta:
    model = Product
    fields = [
      'id', 'name', 'price', 'discount_percent', 'stock', 'is_available',
      'first_image', 'category_detail', 'availability',
      'vendor_detail', 'reservation',
    ]

  def get_first_image(self, obj):
    # Buscar imagen principal
    primary_image = obj.images.filter(is_primary=True).first()
    if primary_image:
      request = self.context.get('request')
      if request:
        return request.build_absolute_uri(primary_image.image.url)
      return primary_image.image.url
    
    # Fallback: primera imagen disponible
    image = obj.images.first()
    if image:
      request = self.context.get('request')
      if request:
        return request.build_absolute_uri(image.image.url)
      return image.image.url
    
    return None

  def get_category_detail(self, obj):
    if obj.category:
      return {
        "id": str(obj.category.id),
        "name": obj.category.name,
        "parent": str(obj.category.parent.id) if obj.category.parent else None,
        "parent_name": obj.category.parent.name if obj.category.parent else None,
      }
    return None

  def get_availability(self, obj):
    return obj.is_available and obj.stock > 0

  def get_reservation(self, obj):
    request = self.context.get("request")
    return build_reservation_payload(obj, request)
