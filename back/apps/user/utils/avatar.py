import logging
import re

import requests
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

MAX_AVATAR_BYTES = 5 * 1024 * 1024
EXTENSIONS = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def import_remote_avatar(profile, url):
    """Guarda la foto de Google como avatar si el perfil aún no tiene una. Nunca rompe el login."""
    if not url or profile.avatar:
        return False
    # Google entrega miniaturas de 96px (`=s96-c`); se pide una versión más grande.
    url = re.sub(r"=s\d+-c$", "=s400-c", url)
    try:
        response = requests.get(url, timeout=6)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").split(";")[0].strip()
        if content_type not in EXTENSIONS or len(response.content) > MAX_AVATAR_BYTES:
            return False
        profile.avatar.save(f"avatar{EXTENSIONS[content_type]}", ContentFile(response.content), save=True)
        return True
    except requests.RequestException:
        logger.warning("No se pudo importar la foto de perfil de %s", url)
        return False
