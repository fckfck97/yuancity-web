"""
Tasa del día USD → COP para mostrar precios en dólares.

Fuente principal: TRM oficial (Superintendencia Financiera, datos.gov.co). Respaldo: open.er-api.com.
Se guarda en caché 6 h; si las dos fuentes fallan se responde la última tasa buena (marcada `stale`).
GET /api/products/exchange-rate/ → {"base": "USD", "quote": "COP", "rate": 3170.46, "date": "2026-10-16", "source": "trm"}
"""
import logging
from datetime import date

import requests
from django.core.cache import cache
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

CACHE_KEY = "exchange:usd_cop"
LAST_GOOD_KEY = "exchange:usd_cop:last"
CACHE_SECONDS = 6 * 60 * 60
TIMEOUT = 6

TRM_URL = "https://www.datos.gov.co/resource/32sa-8pi3.json"
BACKUP_URL = "https://open.er-api.com/v6/latest/USD"


def _from_trm():
    response = requests.get(TRM_URL, params={"$limit": 1, "$order": "vigenciadesde DESC"}, timeout=TIMEOUT)
    response.raise_for_status()
    row = response.json()[0]
    return {"rate": round(float(row["valor"]), 2), "date": str(row["vigenciadesde"])[:10], "source": "trm"}


def _from_backup():
    response = requests.get(BACKUP_URL, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()
    return {"rate": round(float(data["rates"]["COP"]), 2), "date": date.today().isoformat(), "source": "open.er-api"}


def get_usd_cop_rate():
    cached = cache.get(CACHE_KEY)
    if cached:
        return cached
    for fetch in (_from_trm, _from_backup):
        try:
            result = fetch()
            if result["rate"] > 0:
                payload = {"base": "USD", "quote": "COP", **result, "stale": False}
                cache.set(CACHE_KEY, payload, CACHE_SECONDS)
                cache.set(LAST_GOOD_KEY, payload, None)
                return payload
        except Exception as exc:  # red caída, formato inesperado…
            logger.warning("Tasa USD/COP: %s falló: %s", fetch.__name__, exc)
    last = cache.get(LAST_GOOD_KEY)
    return {**last, "stale": True} if last else None


class ExchangeRateAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        payload = get_usd_cop_rate()
        if not payload:
            return Response({"detail": "Tasa no disponible por ahora."}, status=503)
        return Response(payload)
