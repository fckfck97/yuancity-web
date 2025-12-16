# apps/utils/catalog/zara_seed.py
from django.db import transaction
from apps.category.models import Category  # Importa el modelo real


ZARA_CATEGORIES = {
    "sexo_values": ["Mujer", "Hombre", "Niños"],
    "Mujer": [
        {
            "categoria": "Abrigos y Chaquetas",
            "subcategorias": [
                "Abrigos",
                "Plumíferos",
                "Trench",
                "Cazadoras",
                "Parkas",
                "Chaquetas denim",
                "Blazers",
                "Chalecos",
            ],
        },
        {
            "categoria": "Vestidos y Monos",
            "subcategorias": [
                "Vestidos midi",
                "Vestidos mini",
                "Vestidos largos",
                "Vestidos de fiesta",
                "Monos",
            ],
        },
        {
            "categoria": "Tops y Camisas",
            "subcategorias": [
                "Camisas",
                "Blusas",
                "Tops",
                "Bodies",
                "Camisetas",
                "Polos",
            ],
        },
        {
            "categoria": "Punto y Jerséis",
            "subcategorias": [
                "Jerséis",
                "Cárdigans",
                "Chalecos de punto",
            ],
        },
        {
            "categoria": "Pantalones y Jeans",
            "subcategorias": [
                "Jeans (mom, wide leg, flare, skinny)",
                "Pantalones formales",
                "Joggers",
                "Bermudas",
            ],
        },
        {
            "categoria": "Faldas",
            "subcategorias": [
                "Mini",
                "Midi",
                "Larga",
                "Plisadas",
            ],
        },
        {
            "categoria": "Ropa de Noche y Fiesta",
            "subcategorias": [
                "Partywear",
                "Bodies de fiesta",
                "Vestidos de cóctel",
            ],
        },
        {
            "categoria": "Conjuntos y Trajes",
            "subcategorias": [
                "Trajes",
                "Blazer + pantalón",
                "Total Look",
            ],
        },
        {
            "categoria": "Deporte y Casual",
            "subcategorias": [
                "Sudaderas",
                "Chándal",
                "Ropa deportiva",
                "Leggings",
            ],
        },
        {
            "categoria": "Ropa Interior y Pijamas",
            "subcategorias": [
                "Sujetadores",
                "Braguitas",
                "Bodies",
                "Pijamas",
                "Lencería",
            ],
        },
        {
            "categoria": "Calzado",
            "subcategorias": [
                "Zapatos",
                "Zapatillas",
                "Botas",
                "Sandalias",
                "Tacones",
            ],
        },
        {
            "categoria": "Bolsos y Accesorios",
            "subcategorias": [
                "Bolsos",
                "Mochilas",
                "Cinturones",
                "Bufandas",
                "Gorras",
                "Sombreros",
                "Guantes",
            ],
        },
        {
            "categoria": "Bisutería y Complementos",
            "subcategorias": [
                "Collares",
                "Pulseras",
                "Anillos",
                "Pendientes",
            ],
        },
        {
            "categoria": "Belleza y Perfumes",
            "subcategorias": [
                "Perfumes",
                "Productos de belleza",
            ],
        },
        {
            "categoria": "Promocionales y Temporales",
            "subcategorias": [
                "New In",
                "Special Prices",
                "Colecciones",
                "Colaboraciones",
            ],
        },
    ],
    "Hombre": [
        {
            "categoria": "Abrigos y Chaquetas",
            "subcategorias": [
                "Abrigos",
                "Plumíferos",
                "Cazadoras",
                "Trench",
                "Blazers",
                "Chalecos",
            ],
        },
        {
            "categoria": "Camisas y Tops",
            "subcategorias": [
                "Camisas",
                "Camisetas",
                "Polos",
                "Sudaderas",
                "Jerséis",
            ],
        },
        {
            "categoria": "Pantalones y Jeans",
            "subcategorias": [
                "Jeans",
                "Pantalones chinos",
                "Pantalones formales",
                "Joggers",
                "Shorts",
            ],
        },
        {
            "categoria": "Trajes y Formal",
            "subcategorias": [
                "Trajes",
                "Blazers",
                "Chalecos de traje",
                "Camisas formales",
            ],
        },
        {
            "categoria": "Deporte y Casual",
            "subcategorias": [
                "Chándal",
                "Ropa deportiva",
                "Sudaderas",
                "Polo casual",
            ],
        },
        {
            "categoria": "Ropa Interior y Accesorios",
            "subcategorias": [
                "Ropa interior",
                "Boxers",
                "Calcetines",
                "Cinturones",
                "Gorras",
            ],
        },
        {
            "categoria": "Calzado y Bolsos",
            "subcategorias": [
                "Zapatos",
                "Zapatillas",
                "Botas",
                "Bolsos y mochilas",
            ],
        },
        {
            "categoria": "Accesorios",
            "subcategorias": [
                "Bufandas",
                "Guantes",
                "Relojes (complemento)",
                "Gafas de sol",
            ],
        },
        {
            "categoria": "Promocionales y Temporales",
            "subcategorias": [
                "New In",
                "Special Prices",
                "Colecciones",
                "Colaboraciones",
            ],
        },
    ],
    "Niños": [
        {
            "categoria": "Secciones por edad",
            "subcategorias": [
                "Bebé (0-24m)",
                "Niño (2-12 años)",
                "Niña (2-12 años)",
            ],
        },
        {
            "categoria": "Prendas principales",
            "subcategorias": [
                "Abrigos",
                "Vestidos",
                "Camisetas",
                "Pantalones",
                "Jeans",
                "Conjuntos",
                "Shorts",
            ],
        },
        {
            "categoria": "Ropa Interior y Pijamas",
            "subcategorias": [
                "Bodies bebé",
                "Pijamas",
                "Ropa interior infantil",
            ],
        },
        {
            "categoria": "Calzado infantil",
            "subcategorias": [
                "Zapatos por edad",
                "Zapatillas",
                "Botas",
                "Sandalias",
            ],
        },
        {
            "categoria": "Accesorios infantiles",
            "subcategorias": [
                "Mochilas",
                "Gorros",
                "Bufandas",
                "Guantes",
            ],
        },
        {
            "categoria": "Promocionales y Temporales",
            "subcategorias": [
                "New In Kids",
                "Special Prices Kids",
                "Colecciones infantiles",
            ],
        },
    ],
    "recomendaciones_de_normalizacion": {
        "sexo_field": "usar valores estandarizados: Mujer, Hombre, Niños",
        "nombres": "unificar sinónimos",
    },
}


def seed_zara_categories():
    """
    Crea el árbol:

    Mujer/Hombre/Niños (nivel 1)
      -> categoría (nivel 2)
          -> subcategoría (nivel 3)

    Es idempotente: usa get_or_create, así que puedes llamarla varias veces
    sin generar duplicados (por el unique_together en Category).
    NO borra nada ni toca los productos existentes.
    """
    sexo_values = ZARA_CATEGORIES.get("sexo_values", [])

    with transaction.atomic():
        for sexo in sexo_values:
            bloques = ZARA_CATEGORIES.get(sexo, [])

            # nivel 1: sexo (raíz)
            sexo_cat, _ = Category.objects.get_or_create(
                parent=None,
                name=sexo,
            )

            for bloque in bloques:
                nombre_categoria = bloque.get("categoria")
                subcategorias = bloque.get("subcategorias", [])

                if not nombre_categoria:
                    continue

                # nivel 2: categoría
                categoria_cat, _ = Category.objects.get_or_create(
                    parent=sexo_cat,
                    name=nombre_categoria,
                )

                # nivel 3: subcategorías
                for sub_name in subcategorias:
                    if not sub_name:
                        continue

                    Category.objects.get_or_create(
                        parent=categoria_cat,
                        name=sub_name,
                    )
