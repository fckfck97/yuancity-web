from decimal import Decimal, InvalidOperation
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from apps.utils.yuancity_stage_templates import build_stage_message_payload
from .models import UserAccount as User, LoginLog, UserProfile, UserFollow
from .data.colombia_locations import (
    is_valid_location,
    normalize_city,
    normalize_department,
)
from .utils.phone import normalize as normalize_phone

class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    department = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = UserProfile
        fields = (
            'bio',
            'location',
            'department',
            'city',
            'address_line',
            'latitude',
            'longitude',
            'avatar_url',
            'cover_url',
            'followers_count',
            'following_count',
            'posts_count',
        )
        extra_kwargs = {
            'bio': {'required': False, 'allow_blank': True},
            'location': {'read_only': True},
            'department': {'required': False, 'allow_blank': True},
            'city': {'required': False, 'allow_blank': True},
            'address_line': {'required': False, 'allow_blank': True},
            'latitude': {'required': False, 'allow_null': True},
            'longitude': {'required': False, 'allow_null': True},
        }

    def _build_absolute_uri(self, file_field):
        if not file_field:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(file_field.url)
        return file_field.url

    def get_avatar_url(self, obj):
        return self._build_absolute_uri(obj.avatar)

    def get_cover_url(self, obj):
        return self._build_absolute_uri(obj.cover_image)

    def get_followers_count(self, obj):
        return obj.user.followers.count() if obj.user_id else 0

    def get_following_count(self, obj):
        return obj.user.following.count() if obj.user_id else 0

    def get_posts_count(self, obj):
        return obj.user.products.count() if obj.user_id else 0

class UserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
           'email',
            'first_name',
            'last_name',
            'phone',
            'rol',
        )
        
class UserSerializerEdit(serializers.ModelSerializer):
    social_profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'phone',
            'rol',
            'social_profile',
        )

    def to_internal_value(self, data):
        """
        Sobrescribimos para pasar la instancia del perfil al serializer anidado.
        Esto permite que el serializer del perfil acceda a la instancia existente.
        """
        social_data = data.get('social_profile')
        
        if social_data and self.instance:
            # Obtener o crear el perfil antes de la validación
            profile = getattr(self.instance, 'social_profile', None)
            if profile:
                # Configurar la instancia en el field del serializer anidado
                self.fields['social_profile'].instance = profile
        
        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        social_data = validated_data.pop('social_profile', None)
        user = super().update(instance, validated_data)

        if social_data is not None:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            
            if "bio" in social_data and social_data["bio"] is not None:
                profile.bio = social_data["bio"]

            department = social_data.get("department")
            city = social_data.get("city")
            if department is not None or city is not None:
                dept_value = normalize_department(department)
                city_value = normalize_city(city)
                if dept_value or city_value:
                    if not is_valid_location(dept_value, city_value):
                        raise serializers.ValidationError(
                            {
                                "social_profile": {
                                    "location": "Selecciona un departamento y municipio válidos de Colombia."
                                }
                            }
                        )
                profile.department = dept_value
                profile.city = city_value

            address_line = social_data.get("address_line")
            if address_line is not None:
                profile.address_line = address_line.strip()

            lat_value = social_data.get("latitude")
            lon_value = social_data.get("longitude")
            coordinates_provided = lat_value not in (None, "") or lon_value not in (None, "")
            if coordinates_provided:
                if lat_value in (None, "") or lon_value in (None, ""):
                    raise serializers.ValidationError(
                        {
                            "social_profile": {
                                "coordinates": "Debes enviar latitud y longitud para fijar tu ubicación."
                            }
                        }
                    )
                try:
                    profile.latitude = Decimal(str(lat_value))
                    profile.longitude = Decimal(str(lon_value))
                except (InvalidOperation, TypeError):
                    raise serializers.ValidationError(
                        {
                            "social_profile": {
                                "coordinates": "Formato de coordenadas inválido."
                            }
                        }
                    )
            elif lat_value in ("", None) and lon_value in ("", None) and (
                lat_value is not None or lon_value is not None
            ):
                profile.latitude = None
                profile.longitude = None

            if any(field is not None for field in (address_line, department, city)):
                fragments = [
                    (profile.address_line or "").strip(),
                    profile.city or "",
                    profile.department or "",
                ]
                fragments = [fragment for fragment in fragments if fragment]
                if fragments:
                    fragments.append("Colombia")
                profile.location = ", ".join(fragments)

            profile.save()

        return user


class OTPRequestSerializer(serializers.Serializer):
    """
    Recibe e‑mail o teléfono para solicitar OTP.
    """
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)

    def validate(self, attrs):
        email = attrs.get("email")
        phone = attrs.get("phone")
        if not email and not phone:
            raise serializers.ValidationError("Debes enviar email o phone.")
        return attrs


class OTPVerifySerializer(serializers.Serializer):
    identifier = serializers.CharField()
    otp        = serializers.CharField()
    source     = serializers.ChoiceField(      # «web» o «app» (móvil)
        choices=('web', 'app'), default='app', required=False
    )

    def validate(self, data):
        expected_len = 6 if data['source'] == 'web' else 4
        otp = data['otp']

        if not otp.isdigit() or len(otp) != expected_len:
            raise serializers.ValidationError(
                {"otp": f"El código debe tener {expected_len} dígitos numéricos."}
            )
        return data
class LoginLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginLog
        fields = ('id', 'user', 'ip_address',
                  'user_agent', 'success', 'created_at')
        depth = 1               # incluye email / nombre del usuario

class ExpoPushTokenUpsertSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)
    device_os = serializers.ChoiceField(choices=["ios", "android"])
    user_id = serializers.UUIDField(required=False, allow_null=True)


class PublicProfileSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    email = serializers.EmailField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    full_name = serializers.CharField(allow_blank=True)
    bio = serializers.CharField(allow_blank=True, required=False)
    location = serializers.CharField(allow_blank=True, required=False)



class N8NUserStageSerializer(serializers.ModelSerializer):
    """Serializer para stages de mensajes automáticos a usuarios"""
    full_name = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    html = serializers.SerializerMethodField()
    sms_text = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'phone',
            'full_name',
            'consent_notifications',
            'created_at',
            'stage',
            'next_send_at',
            'last_sent_at',
            'subject',
            'message',
            'html',
            'sms_text',
        ]

    def get_full_name(self, obj):
        first = (obj.first_name or "").strip()
        last = (obj.last_name or "").strip()
        full = f"{first} {last}".strip()
        return full.title() if full else ""

    def _payload(self, obj):
        user_name = self.get_full_name(obj)
        return build_stage_message_payload(
            obj.stage,
            user_name=user_name,
            user_email=(obj.email or "").strip(),
            user_id=str(obj.id)
        )


    def get_subject(self, obj):
        return self._payload(obj).get('subject', '')

    def get_message(self, obj):
        return self._payload(obj).get('sms_text', '')

    def get_html(self, obj):
        return self._payload(obj).get('html', '')

    def get_sms_text(self, obj):
        return self._payload(obj).get('sms_text', '')
    
    def to_representation(self, instance):
        # Verificar si el usuario ha completado nombre y apellido
        first = (instance.first_name or "").strip()
        last = (instance.last_name or "").strip()
        full_name = f"{first} {last}".strip()
        
        # No incluir usuario si no tiene nombre completo
        if not full_name:
            return None
        
        data = super().to_representation(instance)
        
        # Validar y limpiar email
        email = data.get('email')
        if email:
            email = str(email).strip().lower()
            # Excluir correos de revisores/demo
            if email.endswith("@yuancity.com"):
                data.pop('email', None)
            # Excluir correos de iCloud
            elif email.endswith("@icloud.com"):
                data.pop('email', None)
            # Excluir correos de Apple Private Relay
            elif email.endswith("@privaterelay.appleid.com"):
                data.pop('email', None)
            else:
                # Validar formato de email
                try:
                    validate_email(email)
                    data['email'] = email
                except ValidationError:
                    data.pop('email', None)
        
        # Omite email/phone vacíos, conserva full_name
        for key in ("email", "phone"):
            if data.get(key) in (None, ""):
                data.pop(key, None)
        
        return data


class FollowListEntrySerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'full_name',
            'bio',
            'location',
            'avatar_url',
            'followers_count',
            'is_following',
        )

    def _get_profile(self, obj):
        try:
            return obj.social_profile
        except (UserProfile.DoesNotExist, AttributeError):
            return None

    def _build_absolute_uri(self, file_field):
        if not file_field:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(file_field.url)
        return file_field.url

    def get_full_name(self, obj):
        return obj.full_name

    def get_bio(self, obj):
        profile = self._get_profile(obj)
        return profile.bio if profile else ""

    def get_location(self, obj):
        profile = self._get_profile(obj)
        if not profile:
            return ""
        # Solo mostrar ciudad, departamento y país (sin dirección exacta)
        location_parts = []
        if profile.city:
            location_parts.append(profile.city)
        if profile.department:
            location_parts.append(profile.department)
        if location_parts:
            location_parts.append("Colombia")
        return ", ".join(location_parts) if location_parts else ""

    def get_avatar_url(self, obj):
        profile = self._get_profile(obj)
        if profile and profile.avatar:
            return self._build_absolute_uri(profile.avatar)
        return None

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_is_following(self, obj):
        viewer_ids = self.context.get('viewer_following_ids')
        if isinstance(viewer_ids, set):
            return obj.id in viewer_ids
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserFollow.objects.filter(
                follower=request.user, following=obj
            ).exists()
        return False


class FollowActionSerializer(serializers.Serializer):
    target = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    action = serializers.ChoiceField(
        choices=("follow", "unfollow", "toggle"),
        default="toggle",
    )

    def validate(self, attrs):
        follower = self.context.get('request').user if self.context.get('request') else None
        target = attrs.get('target')
        if follower and target and follower == target:
            raise serializers.ValidationError("No puedes seguir tu propia cuenta.")
        return attrs
