# apps/user/utils/password.py
from django.utils.crypto import get_random_string

def strong_random_password(length=12):
    """
    Genera una contraseña aleatoria con letras, dígitos y símbolos.
    """
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    return get_random_string(length, chars)
