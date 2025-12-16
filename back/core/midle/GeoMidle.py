from django.utils.deprecation import MiddlewareMixin
import requests
from apps.count.models import PageView

class PageViewMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Procesar solo en la ruta raíz
        if request.path == '/':
            # Obtener la IP del usuario
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip_address:
                ip_address = ip_address.split(',')[-1].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR', '')

            # Obtener el user agent del request
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            # Si ya existe un registro con esta IP y user agent, no se crea uno nuevo
            if PageView.objects.filter(ip_address=ip_address, user_agent=user_agent).exists():
                return

            # Inicializar datos de ubicación por defecto
            location_data = {
                "country": "",
                "city": "",
                "latitude": None,
                "longitude": None,
            }
            
            try:
                # Consulta a la API externa para obtener geolocalización
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
                # En caso de error, se mantiene location_data con valores por defecto
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
