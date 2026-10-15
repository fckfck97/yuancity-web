import logging
import time

import jwt
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

APPLE_AUTH_URL = "https://appleid.apple.com/auth"


def apple_revocation_configured():
    return bool(settings.APPLE_TEAM_ID and settings.APPLE_KEY_ID and settings.APPLE_PRIVATE_KEY)


def apple_client_secret():
    now = int(time.time())
    return jwt.encode(
        {"iss": settings.APPLE_TEAM_ID, "iat": now, "exp": now + 300, "aud": "https://appleid.apple.com", "sub": settings.APPLE_APP_ID},
        settings.APPLE_PRIVATE_KEY,
        algorithm="ES256",
        headers={"kid": settings.APPLE_KEY_ID},
    )


def revoke_apple_authorization(authorization_code):
    """
    Revoca el acceso de Sign in with Apple (exigido por Apple al eliminar la cuenta).
    Canjea el authorization_code por un token y lo revoca. Devuelve el estado para la trazabilidad.
    """
    if not apple_revocation_configured():
        return "not_configured"
    if not authorization_code:
        return "missing_code"
    try:
        secret = apple_client_secret()
        token_response = requests.post(
            f"{APPLE_AUTH_URL}/token",
            data={
                "client_id": settings.APPLE_APP_ID,
                "client_secret": secret,
                "code": authorization_code,
                "grant_type": "authorization_code",
            },
            timeout=8,
        )
        token_response.raise_for_status()
        tokens = token_response.json()
        token = tokens.get("refresh_token") or tokens.get("access_token")
        hint = "refresh_token" if tokens.get("refresh_token") else "access_token"
        requests.post(
            f"{APPLE_AUTH_URL}/revoke",
            data={"client_id": settings.APPLE_APP_ID, "client_secret": secret, "token": token, "token_type_hint": hint},
            timeout=8,
        ).raise_for_status()
        return "revoked"
    except (requests.RequestException, jwt.PyJWTError, ValueError):
        logger.exception("No se pudo revocar el acceso de Apple")
        return "failed"
