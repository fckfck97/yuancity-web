"""
utils/ai_search.py
──────────────────
Lógica de búsqueda estándar y búsqueda con IA (OpenAI) para el catálogo
de productos.

Funciones exportadas:
  - execute_product_search(query, category_ids, per_limit, request)
  - product_catalog_index_for_ai(max_desc_chars, max_products)
  - call_openai_product_search_interpreter(user_prompt, categories, catalog_index)
  - call_openai_product_result_filter(user_prompt, candidates)
"""

import json
from uuid import UUID

from openai import OpenAI

from django.conf import settings
from django.db.models import Q

from apps.product.models import Product
from apps.product.serializers import ProductMinimalSerializer


# ─────────────────────────────────────────────────────────────
#  Búsqueda estándar
# ─────────────────────────────────────────────────────────────

def _simplify_word(word: str) -> list:
    """
    Devuelve variaciones de una palabra para búsqueda flexible.
    - Quita 's' final: camisas → camisa
    - Quita 'es' final: pantalones → pantalon
    """
    word = word.strip().lower()
    if len(word) < 3:
        return [word]
    variants = [word]
    if word.endswith("s") and len(word) > 3:
        variants.append(word[:-1])
    if word.endswith("es") and len(word) > 4:
        variants.append(word[:-2])
    return list(set(variants))


def _build_product_criteria(query: str) -> Q:
    """
    Filtro Q tokenizado sobre nombre y descripción del producto.
    Busca frase completa y cada palabra con variantes singular/plural.
    """
    query = query.strip()
    if not query:
        return Q()

    base = Q(name__icontains=query) | Q(description__icontains=query)

    words = [w.strip() for w in query.split() if len(w.strip()) >= 2]
    for word in words:
        for variant in _simplify_word(word):
            base |= Q(name__icontains=variant) | Q(description__icontains=variant)

    return base


def execute_product_search(
    query: str,
    category_ids: list = None,
    per_limit: int = 20,
    request=None,
) -> dict:
    """
    Busca productos disponibles por nombre y descripción.

    Returns::

        {
          "query": str,
          "limit": int,
          "total": int,
          "results": {"products": [...]},
        }
    """
    qs = (
        Product.objects.filter(is_available=True, stock__gt=0)
        .select_related("vendor", "vendor__social_profile", "category", "category__parent")
        .prefetch_related("images")
    )

    if query:
        qs = qs.filter(_build_product_criteria(query))

    if category_ids:
        cat_filter = Q()
        for cid in category_ids:
            cat_filter |= (
                Q(category__id=cid)
                | Q(category__parent__id=cid)
                | Q(category__parent__parent__id=cid)
            )
        qs = qs.filter(cat_filter)

    qs = qs.distinct().order_by("-created_at")
    items = list(qs[:per_limit])
    serialized = ProductMinimalSerializer(items, many=True, context={"request": request}).data

    return {
        "query": query,
        "limit": per_limit,
        "total": len(serialized),
        "results": {"products": list(serialized)},
    }


# ─────────────────────────────────────────────────────────────
#  Índice compacto del catálogo para IA
# ─────────────────────────────────────────────────────────────

def product_catalog_index_for_ai(
    max_desc_chars: int = 180,
    max_products: int = 120,
) -> dict:
    """
    Construye un índice compacto de productos activos para dar contexto a la IA.

    Returns::

        {
          "count": int,
          "products": [{"id", "name", "category", "description"}, ...]
        }
    """
    qs = (
        Product.objects.filter(is_available=True, stock__gt=0)
        .select_related("category", "category__parent")
        .only("id", "name", "description", "category")
        .order_by("name")[:max_products]
    )

    products = []
    for p in qs:
        desc = (p.description or "").strip()
        cat_name = p.category.name if p.category else ""
        parent_name = p.category.parent.name if (p.category and p.category.parent) else ""
        products.append({
            "id": str(p.id),
            "name": p.name,
            "category": f"{parent_name} > {cat_name}" if parent_name else cat_name,
            "description": desc[:max_desc_chars],
        })

    return {"count": len(products), "products": products}


# ─────────────────────────────────────────────────────────────
#  Primera llamada a OpenAI: interpreta el prompt
# ─────────────────────────────────────────────────────────────

def call_openai_product_search_interpreter(
    user_prompt: str,
    categories: list,
    catalog_index: dict = None,
) -> dict:
    """
    Interpreta el prompt del usuario y devuelve parámetros optimizados
    para buscar en el catálogo de productos.

    Args:
        user_prompt:   texto libre del usuario.
        categories:    lista de dicts ``{"id": ..., "name": ...}``.
        catalog_index: índice compacto de productos (opcional).

    Returns::

        {
          "query": str,
          "category_ids": [...],
          "suggestions": [...],
          "answer": str,
          "raw_prompt": str,
        }
    """
    if not getattr(settings, "OPENAI_API_KEY", None):
        raise RuntimeError("OPENAI_API_KEY no configurada")

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    category_lines = "\n".join(
        f'- id="{c["id"]}" name="{c["name"]}"' for c in categories[:100]
    )

    index_summary = ""
    if catalog_index:
        count = catalog_index.get("count", 0)
        index_summary = f"\n\nProductos disponibles: {count}."
        sample = catalog_index.get("products", [])[:40]
        if sample:
            names = [p["name"] for p in sample if p.get("name")][:30]
            index_summary += "\nEjemplos: " + ", ".join(names)

    messages = [
        {
            "role": "system",
            "content": (
                "Eres un experto en comercio electrónico. "
                "Interpreta búsquedas en lenguaje natural y conviértelas en parámetros "
                "para buscar productos en una tienda.\n\n"
                "INSTRUCCIONES:\n"
                "1. Analiza la intención: ¿producto específico? ¿categoría? ¿característica?\n"
                "2. Genera 'query' con palabras clave cortas y relevantes del producto\n"
                "3. Si corresponde a categorías de la lista, incluye sus IDs en 'category_ids'\n"
                "4. Si no hay categoría clara, deja 'category_ids' vacío []\n"
                "5. Sugiere 2-3 búsquedas alternativas\n"
                "6. Genera respuesta breve y amigable (máx 5 palabras)\n\n"
                "EJEMPLOS:\n"
                '"camisas de hombre" → {"query":"camisa hombre","category_ids":["<id>"],"answer":"Camisas para hombre"}\n'
                '"zapatos deportivos" → {"query":"zapato deportivo","category_ids":["<calzado>"],"answer":"Zapatos deportivos"}\n'
                '"crema hidratante" → {"query":"crema hidratante","category_ids":["<belleza>"],"answer":"Cremas hidratantes"}\n'
                '"algo para regalar" → {"query":"regalo","category_ids":[],"answer":"Ideas para regalar"}\n\n'
                "FORMATO DE RESPUESTA (JSON válido únicamente):\n"
                '{"query":"término","category_ids":[],"suggestions":["s1","s2"],"answer":"respuesta"}\n\n'
                "REGLAS:\n"
                "- 'query' corto (1-3 palabras), singular de preferencia\n"
                "- Usa SOLO IDs de la lista de categorías provista\n"
                "- 'answer' máximo 5 palabras\n"
            ),
        },
        {
            "role": "user",
            "content": (
                f"Búsqueda del usuario: {user_prompt}\n\n"
                "Categorías disponibles:\n" + category_lines
                + index_summary
            ),
        },
    ]

    try:
        completion = client.chat.completions.create(
            model=getattr(settings, "OPENAI_SEARCH_MODEL", "gpt-3.5-turbo"),
            temperature=0.3,
            messages=messages,
            timeout=20,
        )
        parsed = json.loads(completion.choices[0].message.content)
    except Exception as exc:
        raise RuntimeError(f"Error llamando a OpenAI: {exc}")

    ai_query = str(parsed.get("query") or "").strip() or user_prompt.strip()

    valid_ids = {str(c["id"]) for c in categories}
    raw_ids = parsed.get("category_ids") or []
    if not isinstance(raw_ids, list):
        raw_ids = []
    category_ids = [str(c) for c in raw_ids if str(c) in valid_ids]

    suggestions = parsed.get("suggestions") or []
    if not isinstance(suggestions, list):
        suggestions = []
    suggestions = [str(s).strip() for s in suggestions if str(s).strip()][:3]

    answer = str(parsed.get("answer") or "").strip()
    if not answer:
        answer = f"Resultados de {ai_query}"

    return {
        "query": ai_query,
        "category_ids": category_ids,
        "suggestions": suggestions,
        "answer": answer,
        "raw_prompt": user_prompt,
    }


# ─────────────────────────────────────────────────────────────
#  Segunda llamada a OpenAI: filtra candidatos y devuelve UUIDs
# ─────────────────────────────────────────────────────────────

def call_openai_product_result_filter(
    user_prompt: str,
    candidates: list,
) -> dict:
    """
    Segunda llamada a OpenAI: recibe candidatos y devuelve solo los UUIDs
    de productos que realmente coinciden con la intención del usuario.

    Args:
        user_prompt: texto original del usuario.
        candidates:  lista de productos serializados.

    Returns::

        {
          "selected_ids": [uuid, ...],
          "answer": str,
          "reasoning": str,
        }
    """
    if not getattr(settings, "OPENAI_API_KEY", None):
        raise RuntimeError("OPENAI_API_KEY no configurada")

    if not candidates:
        return {
            "selected_ids": [],
            "answer": "No encontré productos que coincidan",
            "reasoning": "Sin candidatos",
        }

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    candidate_lines = []
    for p in candidates[:40]:
        cat_detail = p.get("category_detail") or {}
        if isinstance(cat_detail, dict):
            parent = cat_detail.get("parent_name") or ""
            cname = cat_detail.get("name") or ""
            cat = f"{parent} > {cname}" if parent else cname
        else:
            cat = ""
        candidate_lines.append(
            f'- ID: {p.get("id")} | '
            f'Nombre: {p.get("name")} | '
            f'Categoría: {cat} | '
            f'Precio: {p.get("price")}'
        )

    messages = [
        {
            "role": "system",
            "content": (
                "Eres un experto en comercio electrónico. "
                "Analiza los candidatos y selecciona SOLO los productos que coinciden "
                "con la intención del usuario.\n\n"
                "CRITERIOS:\n"
                "- Coincidencia exacta o cercana en nombre: ALTA prioridad\n"
                "- Coincidencia en categoría relevante: MEDIA prioridad\n"
                "- Selecciona máximo 20; si ninguno coincide, devuelve lista vacía\n"
                "- Ordena por relevancia (más relevante primero)\n\n"
                "FORMATO DE RESPUESTA (JSON válido únicamente):\n"
                '{"selected_ids":["uuid1","uuid2",...],'
                '"answer":"respuesta breve","reasoning":"explicación"}\n\n'
                "- NUNCA inventes IDs, usa solo los de la lista\n"
                "- 'answer' máximo 6 palabras\n"
            ),
        },
        {
            "role": "user",
            "content": (
                f"Búsqueda del usuario: {user_prompt}\n\n"
                "Candidatos:\n" + "\n".join(candidate_lines)
            ),
        },
    ]

    try:
        completion = client.chat.completions.create(
            model=getattr(settings, "OPENAI_SEARCH_MODEL", "gpt-3.5-turbo"),
            temperature=0.2,
            messages=messages,
            timeout=20,
        )
        parsed = json.loads(completion.choices[0].message.content)
    except Exception as exc:
        raise RuntimeError(f"Error en filtrado OpenAI: {exc}")

    raw_ids = parsed.get("selected_ids") or []
    if not isinstance(raw_ids, list):
        raw_ids = []

    valid_ids = []
    for id_str in raw_ids:
        try:
            UUID(str(id_str))
            valid_ids.append(str(id_str))
        except (ValueError, AttributeError):
            continue

    return {
        "selected_ids": valid_ids[:20],
        "answer": str(parsed.get("answer", "Aquí tienes los productos")).strip(),
        "reasoning": str(parsed.get("reasoning", "")).strip(),
    }
