# utils/phone.py
def normalize(phone: str) -> str:
    """Devuelve el número SIN ‘+’ ni espacios."""
    return phone.strip().replace(" ", "").lstrip("+")
