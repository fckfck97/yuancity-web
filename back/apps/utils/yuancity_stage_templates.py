import random
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


CONFIG = {
    "cta_url": "https://yuancity.com/",
    "unsubscribe_url": "https://yuancity.com/unsubscribe",
    "logo_url": "https://yuancity.com/templates/logo.png",
    "poster_fallback_url": "https://yuancity.com/template/logo.png",
    "company_name": "YuanCity",
    "company_address": "YuanCity - Compra lo que quieras, cuando quieras",
}


def _build_unsubscribe_url(user_email: str = "", user_id: str = "") -> str:
    base_url = str(CONFIG.get("unsubscribe_url", "") or "")
    if not base_url:
        return ""

    split = urlsplit(base_url)
    query = dict(parse_qsl(split.query, keep_blank_values=True))
    if user_id:
        query["id"] = str(user_id)
    elif user_email:
        query["email"] = str(user_email)

    return urlunsplit(
        (
            split.scheme,
            split.netloc,
            split.path,
            urlencode(query),
            split.fragment,
        )
    )


def _normalize_examples(examples: list | None, max_items: int = 3) -> list[str]:
    return [item.get("poster_url", "") for item in _normalize_media_items(examples, max_items=max_items)]


def _normalize_media_items(examples: list | None, max_items: int = 3) -> list[dict]:
    if not examples:
        return []

    normalized_items: list[dict] = []
    seen: set[str] = set()

    for item in examples:
        if isinstance(item, dict):
            poster_url = str(
                item.get("poster_url")
                or item.get("image")
                or item.get("image_url")
                or item.get("url")
                or ""
            ).strip()
            title = str(item.get("title") or item.get("name") or "").strip()
            content_type = str(
                item.get("content_type")
                or item.get("type")
                or item.get("kind")
                or ""
            ).strip()
            category = str(item.get("category") or item.get("genre") or "").strip()
        else:
            poster_url = str(item or "").strip()
            title = ""
            content_type = ""
            category = ""

        if not poster_url:
            poster_url = str(CONFIG.get("poster_fallback_url", "") or "")

        dedupe_key = poster_url or f"{content_type}:{title}:{category}"
        if dedupe_key in seen:
            continue

        seen.add(dedupe_key)
        normalized_items.append(
            {
                "poster_url": poster_url,
                "title": title,
                "content_type": content_type or "Contenido",
                "category": category,
            }
        )

    if len(normalized_items) <= max_items:
        return normalized_items

    return random.sample(normalized_items, k=max_items)


def _get_genre_name(genre) -> str:
    raw_name = str(getattr(genre, "name", "") or "").strip()
    if hasattr(genre, "get_name_display"):
        display_name = str(genre.get_name_display() or "").strip()
        if display_name:
            return display_name
    return raw_name.replace("_", " ").title() if raw_name else ""


def _resolve_content_type(product) -> str:
    category = getattr(product, "category", None)
    if category:
        return str(category.name).title()
    return "Producto"


def _absolute_media_url(url: str) -> str:
    raw = str(url or "").strip()
    if not raw:
        return ""
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    base = str(CONFIG.get("cta_url", "") or "").strip().rstrip("/")
    if not base:
        return raw
    return f"{base}/{raw.lstrip('/')}"


def _safe_file_url(file_field) -> str:
    """Retorna URL del archivo sin lanzar excepción si no hay archivo asociado."""
    if not file_field:
        return ""
    try:
        return str(getattr(file_field, "url", "") or "").strip()
    except Exception:
        return ""


def _load_stage_media_items(stage: int, max_items: int = 3) -> list[dict]:
    try:
        from django.apps import apps
        from django.db.models import F, Q
        
        Product = apps.get_model("product", "Product")
        ProductImage = apps.get_model("product", "ProductImage")
    except Exception:
        return []

    def _query_base():
        """Base queryset para productos activos."""
        return Product.objects.filter(is_available=True, stock__gt=0).order_by("-created_at")

    def to_item(obj) -> dict | None:
        # Intentar obtener la imagen primaria, si no existe o no tiene, la primera disponible
        image_obj = obj.images.filter(is_primary=True).first() or obj.images.first()
        image_url = _absolute_media_url(_safe_file_url(getattr(image_obj, "image", None)))
        
        if not image_url:
            image_url = str(CONFIG.get("poster_fallback_url", "") or "")

        price_formatted = f"{obj.currency} {obj.price:,.2f}"
        category_name = obj.category.name if hasattr(obj, "category") and obj.category else "General"

        return {
            "poster_url": image_url,
            "title": str(obj.name or "").strip(),
            "content_type": price_formatted, # Usamos el tipo para mostrar precio en este diseño
            "category": category_name,
        }

    # Cargar contenido específico según el stage
    prioritized = []
    
    if stage == 0:
        # Bienvenida: productos más nuevos
        prioritized = _query_base()[:max_items * 2]
    
    elif stage == 1:
        # Tendencias: productos con stock bajo o destacados (simulado aquí con orden aleatorio o por precio)
        prioritized = _query_base().order_by("-price")[:max_items * 2]
    
    elif stage == 2:
        # Novedades: últimos agregados
        prioritized = _query_base().order_by("-created_at")[:max_items * 2]
    
    elif stage == 3:
        # Ofertas: (si hubiera un campo de descuento, aquí usamos stock alto como relleno)
        prioritized = _query_base().order_by("-stock")[:max_items * 2]
    
    elif stage == 4:
        # Premium: productos más caros
        prioritized = _query_base().order_by("-price")[:max_items * 2]
    
    elif stage == 5:
        # Regresa: sugerencias variadas
        prioritized = _query_base().order_by("?")[:max_items * 2]
    
    else:
        prioritized = _query_base()[:max_items * 2]

    # Construir lista de items sin duplicados
    items: list[dict] = []
    seen_ids: set = set()
    for obj in prioritized:
        if obj.id in seen_ids:
            continue
        built = to_item(obj)
        if not built:
            continue
        seen_ids.add(obj.id)
        items.append(built)
        if len(items) >= max_items:
            break

    return items


def _replace_vars(
    text: str,
    user_name: str = "",
    user_email: str = "",
    user_id: str = "",
    examples: list | None = None,
) -> str:
    """Reemplaza variables en el template"""
    value = str(text or "")
    config_values = dict(CONFIG)
    config_values["unsubscribe_url"] = _build_unsubscribe_url(user_email=user_email, user_id=user_id)
    for key, config_value in config_values.items():
        value = value.replace(f"{{{{{key}}}}}", str(config_value))
    
    # Reemplazar nombre de usuario
    value = value.replace("{{user_name}}", user_name)
    
    # Reemplazar ejemplos de imágenes si se proporcionan
    normalized_examples = _normalize_examples(examples)
    if normalized_examples:
        for i, example_url in enumerate(normalized_examples[:3], 1):
            value = value.replace(f"{{{{example_{i}_url}}}}", example_url)
    for i in range(1, 4):
        value = value.replace(f"{{{{example_{i}_url}}}}", "")
    
    return value


def _examples_gallery(examples: list) -> str:
    """Genera galería de productos con diseño superior."""
    items = _normalize_media_items(examples)
    if not items:
        return ""

    cards_html = ""
    for item in items:
        cards_html += f"""
        <td align="center" style="padding:10px;vertical-align:top;" width="{int(100 / len(items))}%">
          <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;height:100%;">
            <tr>
              <td style="padding:0;">
                <img src="{item["poster_url"]}" alt="{item.get("title")}" width="100%" style="display:block;width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:12px 12px 0 0;">
              </td>
            </tr>
            <tr>
              <td align="left" style="padding:12px;">
                <p style="margin:0 0 4px;font-family:'Inter',Helvetica,Arial,sans-serif;font-size:11px;line-height:14px;font-weight:600;color:#6b7280;text-transform:uppercase;">
                  {item.get("category", "General")}
                </p>
                <p style="margin:0 0 8px;font-family:'Inter',Helvetica,Arial,sans-serif;font-size:13px;line-height:18px;font-weight:600;color:#111827;height:36px;overflow:hidden;">
                  {item.get("title", "")}
                </p>
                <p style="margin:0;font-family:'Inter',Helvetica,Arial,sans-serif;font-size:15px;line-height:20px;font-weight:700;color:#2563eb;">
                  {item.get("content_type", "")}
                </p>
              </td>
            </tr>
          </table>
        </td>
        """

    return f"""
<table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#f9fafb;padding:32px 20px;">
  <tr>
    <td>
      <table cellpadding="0" cellspacing="0" border="0" width="100%">
        <tr>
          <td style="padding:0 0 24px;text-align:center;">
            <h2 style="margin:0;font-family:'Inter',Helvetica,Arial,sans-serif;font-size:20px;line-height:28px;font-weight:700;color:#111827;">
              Recomendados para ti
            </h2>
            <p style="margin:4px 0 0;font-family:'Inter',Helvetica,Arial,sans-serif;font-size:14px;line-height:20px;color:#6b7280;">
              Productos seleccionados según tus intereses
            </p>
          </td>
        </tr>
      </table>
      <table cellpadding="0" cellspacing="0" border="0" width="100%">
        <tr>
          {cards_html}
        </tr>
      </table>
    </td>
  </tr>
</table>
"""


def _feature_row(icon: str, title: str, text: str) -> str:
    """Genera una fila de característica con un diseño minimalista y moderno."""
    return f"""
    <tr>
      <td style="padding:8px 20px;">
        <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#ffffff;border:1px solid #f3f4f6;border-radius:12px;padding:16px;">
          <tr>
            <td width="48" align="center" style="padding:0 12px 0 0;">
              <table cellpadding="0" cellspacing="0" border="0" width="40" height="40" style="width:40px;height:40px;background:#eff6ff;border-radius:10px;">
                <tr>
                  <td align="center" valign="middle" style="text-align:center;vertical-align:middle;font-size:20px;line-height:20px;mso-line-height-rule:exactly;font-family:'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji',sans-serif;">{icon}</td>
                </tr>
              </table>
            </td>
            <td>
              <p style="margin:0 0 2px;font-family:'Inter',Helvetica,Arial,sans-serif;font-size:15px;line-height:22px;font-weight:700;color:#111827;">
                {title}
              </p>
              <p style="margin:0;font-family:'Inter',Helvetica,Arial,sans-serif;font-size:13px;line-height:18px;color:#6b7280;">
                {text}
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
"""


def _build_stage_html(
    preheader: str,
    title: str,
    subtitle: str,
    intro: str,
    features: list,
    examples: list,
    cta_text: str,
    cta_hint: str,
    user_name: str = "",
) -> str:
    """Construye el HTML completo del email con diseño Premium para YuanCity."""
    
    greeting = f"Hola {user_name}," if user_name else "Hola,"
    features_html = "".join(_feature_row(icon, t, txt) for icon, t, txt in features)
    examples_html = _examples_gallery(examples)
    examples_section = ""
    if examples_html:
      examples_section = f"""
        <!-- Galería de productos -->
        <table class="content" cellpadding="0" cellspacing="0" border="0" width="600" style="background:#ffffff;">
          <tr>
            <td style="padding:0;">
              {examples_html}
            </td>
          </tr>
        </table>
"""

    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <meta content="width=device-width, initial-scale=1.0" name="viewport" />
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />
  <meta name="format-detection" content="telephone=no" />
  <meta name="x-apple-disable-message-reformatting" />
  <title>{{{{company_name}}}}</title>
  <!--[if mso]>
  <style type="text/css">
    body, table, td {{ font-family: Arial, Helvetica, sans-serif !important; }}
  </style>
  <![endif]-->
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    * {{ margin:0; padding:0; }}
    body {{ margin:0; padding:0; width:100%; -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; background:#f3f4f6; }}
    table {{ border:0; border-spacing:0; }}
    table, td {{ border-collapse:collapse; }}
    img {{ border:0; outline:none; text-decoration:none; -ms-interpolation-mode:bicubic; display:block; }}
    a {{ text-decoration:none; }}
    .content {{ width:600px; }}
    @media only screen and (max-width:640px) {{
      .content {{ width:100% !important; min-width:0 !important; }}
      .mobile-padding {{ padding:24px 20px !important; }}
      h1 {{ font-size:26px !important; line-height:34px !important; }}
    }}
  </style>
</head>
<body style="margin:0;padding:0;background:#f3f4f6;">
  <div style="display:none;font-size:1px;color:#f3f4f6;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;">
    {preheader}
  </div>
  
  <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#f3f4f6;">
    <tr>
      <td align="center" style="padding:32px 10px;">

        <!-- Header minimal -->
        <table class="content" cellpadding="0" cellspacing="0" border="0" width="600" style="background:#ffffff;border-radius:16px 16px 0 0;">
          <tr>
            <td align="left" style="padding:32px 40px 16px;">
              <img src="{{{{logo_url}}}}" alt="{{{{company_name}}}}" width="140" style="display:block;width:140px;height:auto;">
            </td>
          </tr>
        </table>

        <!-- Contenido principal -->
        <table class="content" cellpadding="0" cellspacing="0" border="0" width="600" style="background:#ffffff;">
          <tr>
            <td class="mobile-padding" style="padding:16px 40px 32px;text-align:left;">
              <p style="margin:0 0 16px;font-family:'Inter',Helvetica,Arial,sans-serif;font-size:14px;line-height:20px;color:#6b7280;font-weight:500;">
                {greeting}
              </p>
              <h1 style="margin:0 0 12px;font-family:'Inter',Helvetica,Arial,sans-serif;font-size:32px;line-height:40px;font-weight:800;color:#111827;letter-spacing:-0.5px;">
                {title}
              </h1>
              <p style="margin:0 0 16px;font-family:'Inter',Helvetica,Arial,sans-serif;font-size:18px;line-height:26px;font-weight:600;color:#2563eb;">
                {subtitle}
              </p>
              <p style="margin:0 0 24px;font-family:'Inter',Helvetica,Arial,sans-serif;font-size:15px;line-height:24px;color:#4b5563;">
                {intro}
              </p>
            </td>
          </tr>

          <!-- Caracteristas -->
          <tr>
            <td style="padding:0 20px 24px;">
              <table cellpadding="0" cellspacing="0" border="0" width="100%">
                {features_html}
              </table>
            </td>
          </tr>
        </table>

        {examples_section}

        <!-- Footer y CTA -->
        <table class="content" cellpadding="0" cellspacing="0" border="0" width="600" style="background:#ffffff;border-radius:0 0 16px 16px;">
          <tr>
            <td align="center" style="padding:32px 40px 24px;">
              <table cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td align="center" style="background:#111827;border-radius:8px;">
                    <a href="{{{{cta_url}}}}" style="display:inline-block;padding:16px 40px;color:#ffffff;font-family:'Inter',Helvetica,Arial,sans-serif;font-size:15px;font-weight:700;text-decoration:none;">
                      {cta_text}
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding:0 40px 40px;font-family:'Inter',Helvetica,Arial,sans-serif;font-size:13px;line-height:20px;color:#6b7280;">
              {cta_hint}
            </td>
          </tr>
        </table>

        <!-- Footer secundario -->
        <table class="content" cellpadding="0" cellspacing="0" border="0" width="600" style="margin-top:24px;">
          <tr>
            <td align="center" style="padding:0 20px;">
              <p style="margin:0 0 8px;font-family:'Inter',Helvetica,Arial,sans-serif;font-size:12px;line-height:18px;color:#9ca3af;font-weight:500;">
                © 2026 {{{{company_address}}}}
              </p>
              <p style="margin:0;font-family:'Inter',Helvetica,Arial,sans-serif;font-size:11px;line-height:16px;color:#9ca3af;">
                Recibes este correo porque eres parte de la comunidad de YuanCity.
                <br>
                <a href="{{{{unsubscribe_url}}}}" style="color:#6b7280;text-decoration:underline;">Cancelar suscripción</a>
              </p>
            </td>
          </tr>
        </table>

        <table class="content" cellpadding="0" cellspacing="0" border="0" width="600">
          <tr>
            <td style="height:32px;font-size:1px;line-height:1px;">&nbsp;</td>
          </tr>
        </table>

      </td>
    </tr>
  </table>
</body>
</html>
"""


# Definición de los 6 stages
STAGES = {
    0: {
        "subject": "🛍️ ¡Bienvenido a YuanCity! Descubre tu próximo artículo favorito",
        "preheader": "Explora nuestra tienda online con productos exclusivos y envíos rápidos",
        "title": "Bienvenido a YuanCity",
        "subtitle": "Tu nuevo rincón favorito para comprar",
        "intro": "Gracias por unirte a nuestra comunidad. En YuanCity nos enfocamos en traerte los mejores productos con una experiencia de compra premium y segura. Desde tecnología hasta moda, tenemos todo lo que necesitas.",
        "features": [
            ("📦", "Envíos Seguros", "Garantizamos que tus pedidos lleguen en perfecto estado hasta tu puerta."),
            ("💳", "Pagos Fáciles", "Múltiples métodos de pago integrados para tu total comodidad."),
            ("🌍", "Variedad Única", "Cientos de categorías y miles de productos seleccionados para ti."),
        ],
        "cta_text": "Empezar a comprar",
        "cta_hint": "Haz clic en el botón y explora nuestro catálogo actualizado.",
        "sms": "¡Bienvenido a YuanCity! Empieza a comprar ahora: {{cta_url}}",
    },
    1: {
        "subject": "🔥 Tendencias: Lo más vendido en YuanCity",
        "preheader": "Los productos que todos están comprando",
        "title": "Tendencias de la semana",
        "subtitle": "Lo que está marcando el ritmo ahora mismo",
        "intro": "Te compartimos los artículos más deseados de nuestra tienda. Estos productos están volando de nuestros estantes virtuales. ¡No te quedes sin el tuyo!",
        "features": [
            ("⭐", "Calidad Garantizada", "Productos calificados por nuestra comunidad con las mejores notas."),
            ("🚀", "Alta Rotación", "Nuestros artículos top en ventas con disponibilidad inmediata."),
            ("💡", "Para ti", "Seleccionados basándonos en las tendencias globales de compra."),
        ],
        "cta_text": "Ver tendencias",
        "cta_hint": "Únete a los miles de clientes que ya disfrutan de estos productos.",
        "sms": "🔥 ¡Lo más vendido! Mira las tendencias en YuanCity: {{cta_url}}",
    },
    2: {
        "subject": "✨ Novedades frescas en YuanCity",
        "preheader": "Acabamos de recibir productos que te encantarán",
        "title": "Recién llegados",
        "subtitle": "Sé el primero en tener lo último",
        "intro": "Actualizamos nuestro inventario constantemente para ofrecerte lo más nuevo del mercado. Echa un vistazo a estos productos recién desempacados en nuestra plataforma.",
        "features": [
            ("🆕", "Últimos ingresos", "Actualizamos nuestro stock diariamente con nuevas sorpresas."),
            ("💎", "Exclusividad", "Artículos que solo encontrarás aquí en YuanCity."),
            ("📍", "Rastreo Directo", "Sigue tus nuevos pedidos en tiempo real desde tu perfil."),
        ],
        "cta_text": "Ver novedades",
        "cta_hint": "Toca aquí para descubrir lo último en tecnología, hogar y más.",
        "sms": "✨ ¡Nuevos productos! Descubre lo más reciente en YuanCity: {{cta_url}}",
    },
    3: {
        "subject": "💰 Ofertas Especiales en YuanCity: ¡No te las pierdas!",
        "preheader": "Precios increíbles por tiempo limitado",
        "title": "¡Oportunidades de ahorro!",
        "subtitle": "Precios que no volverán a repetirse",
        "intro": "Hemos seleccionado una lista de artículos con precios especiales. Ya sea por liquidación de stock o promociones de temporada, hoy es el día perfecto para ahorrar.",
        "features": [
            ("📉", "Súper Descuentos", "Precios reducidos en categorías seleccionadas durante esta semana."),
            ("⚡", "Ofertas Flash", "Artículos de alta demanda con rebajas significativas."),
            ("🎁", "Regalos Ideales", "Encuentra el detalle perfecto al mejor precio."),
        ],
        "cta_text": "Ver ofertas",
        "cta_hint": "Aprovecha antes de que se agote el inventario en oferta.",
        "sms": "💰 ¡Ofertas imperdibles en YuanCity! Compra y ahorra: {{cta_url}}",
    },
    4: {
        "subject": "👑 Experiencia Premium en YuanCity",
        "preheader": "Descubre cómo sacarle el máximo provecho a tu cuenta",
        "title": "Lleva tus compras al siguiente nivel",
        "subtitle": "Servicios exclusivos para clientes como tú",
        "intro": "Queremos que tu experiencia en YuanCity sea inmejorable. Por eso, te recordamos las herramientas que tienes a tu disposición para comprar de forma inteligente y rápida.",
        "features": [
            ("🔔", "Alertas de Stock", "Recibe avisos cuando ese producto que tanto quieres vuelva a estar disponible."),
            ("🎯", "Sugerencias IA", "Nuestro sistema aprende de tus gustos para mostrarte lo que realmente necesitas."),
            ("📲", "App Móvil", "Compra desde cualquier lugar con nuestra aplicación optimizada."),
        ],
        "cta_text": "Configurar perfil",
        "cta_hint": "Personaliza tus preferencias y recibe una experiencia a tu medida.",
        "sms": "👑 Mejora tu experiencia en YuanCity con estas funciones: {{cta_url}}",
    },
    5: {
        "subject": "👋 ¡Te extrañamos en YuanCity! Tu carrito te espera",
        "preheader": "Vuelve y mira lo que tenemos de nuevo para ti",
        "title": "¡Hola de nuevo!",
        "subtitle": "Muchas cosas han cambiado desde tu última visita",
        "intro": "Hace un tiempo que no nos visitas y hemos renovado gran parte de nuestro catálogo. Tenemos nuevas colecciones y servicios esperándote. ¿Vuelves a echar un vistazo?",
        "features": [
            ("🔄", "Catálogo Renovado", "Nuevas marcas y productos agregados recientemente."),
            ("🚛", "Envío Veloz", "Hemos optimizado nuestras rutas para entregarte más rápido."),
            ("💬", "Soporte 24/7", "Estamos aquí para ayudarte en cualquier paso de tu compra."),
        ],
        "cta_text": "Volver a la tienda",
        "cta_hint": "Un clic y estarás de vuelta con tus productos favoritos.",
        "sms": "👋 ¡Te extrañamos en YuanCity! Mira lo nuevo que tenemos: {{cta_url}}",
    },
}


# Templates específicos para notificaciones push (sin URLs, más directos y concisos)
PUSH_STAGES = {
    0: {
        "title": "Bienvenido a YuanCity",
        "body": "{{user_name}}, gracias por unirte. Explora productos exclusivos y encuentra lo que buscas.",
    },
    1: {
        "title": "Lo más vendido esta semana",
        "body": "{{user_name}}, descubre los productos que todos están comprando ahora mismo.",
    },
    2: {
        "title": "Nuevos productos disponibles",
        "body": "{{user_name}}, acabamos de recibir productos frescos que te encantarán.",
    },
    3: {
        "title": "Ofertas especiales para ti",
        "body": "{{user_name}}, precios increíbles por tiempo limitado. ¡No te los pierdas!",
    },
    4: {
        "title": "Mejora tu experiencia",
        "body": "{{user_name}}, descubre herramientas exclusivas para comprar de forma más inteligente.",
    },
    5: {
        "title": "Te extrañamos",
        "body": "{{user_name}}, hemos renovado nuestro catálogo. Vuelve y descubre las novedades.",
    },
}


def build_stage_push_notification(
    stage: int,
    user_name: str = "",
) -> dict:
    """
    Construye una notificación push específica para un stage.
    Retorna un diccionario con 'title' y 'body' sin URLs ni elementos complejos.
    """
    push_data = PUSH_STAGES.get(stage, PUSH_STAGES[0])
    
    # Reemplazar nombre de usuario si existe
    title = push_data.get("title", "").replace("{{user_name}}", user_name)
    body = push_data.get("body", "").replace("{{user_name}}", user_name)
    
    # Limpiar marcadores no reemplazados
    title = title.replace("{{user_name}}", "").strip()
    body = body.replace("{{user_name}}", "").strip()
    
    # Ajustar puntuación si se eliminó el nombre
    if body.startswith(", "):
        body = body[2:].strip()
        body = body[0].upper() + body[1:] if body else ""
    
    return {
        "title": title or "Nuevo contenido en YuanCity",
        "body": body or "Tenemos algo especial para ti",
    }


def build_stage_message_payload(
    stage: int,
    user_name: str = "",
    user_email: str = "",
    user_id: str = "",
    examples: list | None = None,
) -> dict:
    """Construye el payload del mensaje para un stage específico"""
    stage_data = STAGES.get(stage, STAGES[0])
    normalized_items = _normalize_media_items(examples)
    if not normalized_items:
        normalized_items = _load_stage_media_items(stage=stage, max_items=3)
    normalized_examples = _normalize_examples(normalized_items)
    
    html = _build_stage_html(
        preheader=stage_data.get("preheader", ""),
        title=stage_data.get("title", ""),
        subtitle=stage_data.get("subtitle", ""),
        intro=stage_data.get("intro", ""),
        features=stage_data.get("features", []),
        examples=normalized_items,
        cta_text=stage_data.get("cta_text", ""),
        cta_hint=stage_data.get("cta_hint", ""),
        user_name=user_name,
    )
    
    return {
        "subject": _replace_vars(
            stage_data.get("subject", ""),
            user_name=user_name,
            user_email=user_email,
            user_id=user_id,
            examples=normalized_examples,
        ),
        "html": _replace_vars(
            html,
            user_name=user_name,
            user_email=user_email,
            user_id=user_id,
            examples=normalized_examples,
        ),
        "sms_text": _replace_vars(
            stage_data.get("sms", ""),
            user_name=user_name,
            user_email=user_email,
            user_id=user_id,
            examples=normalized_examples,
        ),
    }


def build_stage_output(data: dict, user_name: str = "", examples: list = None) -> dict:
    """Construye la salida completa con todos los datos del stage"""
    try:
        stage = int(data.get("stage", 0) or 0)
    except (TypeError, ValueError):
        stage = 0

    payload = build_stage_message_payload(
        stage,
        user_name=user_name,
        user_email=str(data.get("email", "") or ""),
        user_id=str(data.get("id", "") or ""),
        examples=examples,
    )
    return {
        **data,
        **payload,

    }
