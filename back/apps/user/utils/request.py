# utils/request.py
def client_ip(request):
    """Soporta proxy / load-balancer (X-Forwarded-For)."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        # cadena tipo:  "real_ip, proxy1, proxy2"
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
  