from django.db.models import Count
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PageViewSerializer,NewsLetterSerializer
from .models import PageView,NewsLetter
from rest_framework import permissions
import requests
from apps.user.models import UserAccount
class PageViewCountView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        # Obtener la IP del usuario: se privilegia HTTP_X_FORWARDED_FOR, sino REMOTE_ADDR.
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            # Toma la última IP del listado en caso de múltiples
            ip_address = ip_address.split(',')[-1].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', '')

        # Obtener el user agent desde las cabeceras del request
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Validar que el user agent esté presente
        if not user_agent:
            return Response(
                {'message': "Se requiere el user agent del navegador"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Si ya existe un registro con la misma IP y user agent, se evita duplicar
        if PageView.objects.filter(ip_address=ip_address, user_agent=user_agent).exists():
            return Response(
                {'message': "Registro ya existente"},
                status=status.HTTP_200_OK
            )

        # Inicializar datos de ubicación por defecto
        location_data = {
            "country": "",
            "city": "",
            "latitude": None,
            "longitude": None,
        }

        try:
            # Realizar consulta a la API de geolocalización (ip-api.com)
            response = requests.get(f"http://ip-api.com/json/{ip_address}")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    location_data = {
                        "country": data.get("country", ""),
                        "city": data.get("city", ""),
                        "latitude": data.get("lat"),
                        "longitude": data.get("lon"),
                    }
        except Exception as e:
            # En caso de error, se mantiene la información por defecto
            print("Error retrieving location data:", e)

        # Crear el registro PageView con los datos obtenidos
        PageView.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            country=location_data.get("country", ""),
            city=location_data.get("city", ""),
            latitude=location_data.get("latitude"),
            longitude=location_data.get("longitude"),
        )

        return Response(
            {'message': "Registro completado satisfactoriamente"},
            status=status.HTTP_201_CREATED
        )

class NewsLetterView(APIView):
  permission_classes = [permissions.AllowAny]

  def post(self, request, format=None):
    # Obtener el correo electrónico desde los datos enviados por el frontend
    email = request.data.get('email')

    # Validar que el correo electrónico exista
    if email is None:
      return Response({'message': "Se requiere el correo electrónico"}, status=status.HTTP_400_BAD_REQUEST)

    # Verificar si el correo ya está registrado en UserAccount
    if UserAccount.objects.filter(email=email).exists():
      return Response({'message': "El correo ya está registrado como usuario"}, status=status.HTTP_200_OK)

    # Verificar si ya existe un registro con el mismo correo electrónico en NewsLetter
    if NewsLetter.objects.filter(email=email).exists():
      return Response({'message': "Registro ya existente"}, status=status.HTTP_200_OK)

    # Serializar los datos para guardarlos en la base de datos
    serializer = NewsLetterSerializer(data={'email': email})
    if serializer.is_valid():
      serializer.save()
      return Response({'message': "Registro completado satisfactoriamente"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)