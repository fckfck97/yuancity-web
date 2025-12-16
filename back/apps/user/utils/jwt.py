# apps/user/utils/jwt.py
from rest_framework_simplejwt.tokens import RefreshToken

def build_tokens(user):
    """
    Genera pares (refresh, access) para un usuario.
    """
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
